from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import database, engine, metadata
from models import VisitedPage
from schemas import PageCreate, PageOut
from sqlalchemy import select, insert
from fetcher import fetch_html, extract_text
from analysis_agent import analyze_page
import asyncio
import json
from shopping_agent import shopping_agent

app = FastAPI()

# Combined CORS middleware for local testing and the Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "chrome-extension://abcdefg123456"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve frontend
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# Create DB tables
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Background task
async def process_page(record_id: int, url: str, title: str):
    print("BACKGROUND TASK STARTED:", record_id, url)

    html = await fetch_html(url)
    if not html:
        print("HTML FETCH FAILED:", url)
        return

    print("HTML FETCHED:", len(html))

    text = extract_text(html)
    if not text:
        print("TEXT EXTRACTION FAILED")
        return

    print("CALLING AI AGENT")
    analysis = await asyncio.to_thread(analyze_page, text, title or "", url)
    print("AI RESULT:", analysis)

    query = (
        VisitedPage.update()
        .where(VisitedPage.c.id == record_id)
        .values(
            html=html,
            ai_summary=analysis.get("concise_summary"),
            topic=analysis.get("main_topic"),
            intent=analysis.get("user_intent"),
            entities=analysis.get("key_entities"),
        )
    )
    await database.execute(query)
    print("ANALYSIS SAVED:", record_id)

# API Endpoints 
@app.post("/api/history", response_model=PageOut)
async def receive_visited_page(
    payload: PageCreate,
    background_tasks: BackgroundTasks
):
    try:
        record_id = await database.execute(
            insert(VisitedPage).values(
                title=payload.title,
                url=payload.url
            )
        )

        background_tasks.add_task(
            process_page,
            record_id,
            payload.url,
            payload.title
        )

        return PageOut(
            id=record_id,
            title=payload.title,
            url=payload.url,
            ai_summary=None
        )

    except Exception as e:
        # pydantic cannot guess so:
        print("POST /api/history failed:", e)
        raise HTTPException(status_code=400, detail="Invalid history entry")

@app.get("/api/pages", response_model=list[PageOut])
async def list_pages():
    rows = await database.fetch_all(select(VisitedPage).order_by(VisitedPage.c.created_at.desc()))
    return [PageOut(id=r["id"], title=r["title"], url=r["url"], ai_summary=r["ai_summary"]) for r in rows]

@app.delete("/api/pages/{page_id}")
async def delete_page(page_id: int):
    query = VisitedPage.delete().where(VisitedPage.c.id == page_id)
    await database.execute(query)
    return {"status": "deleted", "id": page_id}

#Agent for chatbot post function
@app.post("/api/chat")
async def chat(payload: dict):
    question = payload["question"]

    pages = await database.fetch_all(
        select(VisitedPage)
        .order_by(VisitedPage.c.created_at.desc())
        .limit(50)
    )

    visited_pages = [
        {
            "title": p["title"],
            "url": p["url"],
            "summary": p["ai_summary"]
        }
        for p in pages
    ]

    with open("shopify_stores.json") as f:
        stores = json.load(f)#import the shopify stores from the json list

    result = shopping_agent(question, visited_pages, stores)
    return result
