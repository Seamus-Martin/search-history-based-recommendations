from openai import OpenAI
import json

client = OpenAI()

def shopping_agent(
    question: str,
    visited_pages: list[dict],
    stores: list[dict]
):
    prompt = f"""
You are an AI shopping assistant.

First, determine the user's intent:
- "shopping_habits"
- "store_recommendation"
- "ambiguous"

Then respond accordingly.

User question:
{question}

User browsing history (summarized):
{json.dumps(visited_pages[:20], indent=2)}

Known stores:
{json.dumps(stores, indent=2)}

Rules:
- If shopping_habits, then summarize patterns and preferences
- If store_recommendation, then pick the BEST matching store
- Always explain WHY
- If recommending a store, output a URL
- Output ONLY valid JSON

Output format:
{{
  "intent": "...",
  "answer": "...",
  "recommended_store": {{
    "title": "...",
    "url": "...",
    "reason": "..."
  }} | null
}}
"""
    
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError:
        return {
            "intent": "error",
            "answer": "I couldn’t process that request.",
            "recommended_store": None
        }
