from sqlalchemy import Table, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from database import metadata

VisitedPage = Table(
    "visited_pages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String, nullable=False),
    Column("title", String),
    Column("html", Text),
    Column("ai_summary", Text),
    Column("topic", String),
    Column("intent", String),
    Column("entities", JSON),
    Column("created_at", DateTime, server_default=func.now())
)
