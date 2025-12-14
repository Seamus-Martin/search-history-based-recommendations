from pydantic import BaseModel
from typing import Optional

class PageCreate(BaseModel):
    title: Optional[str] = None
    url: str

class PageOut(BaseModel):
    id: int
    title: Optional[str] = None
    url: str
    ai_summary: Optional[str] = None
