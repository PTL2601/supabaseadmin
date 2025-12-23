from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID


class SessionBase(BaseModel):
    tgid: int
    mode: str
    topicid: int
    total: int = 10
    current_index: int = 0
    created_at: datetime


class SessionCreate(SessionBase):
    questions: List[Any] = []
    answers: List[Any] = []


class SessionUpdate(BaseModel):
    current_index: Optional[int] = None
    answers: Optional[List[Any]] = None


class SessionInDB(SessionBase):
    id: UUID
    questions: List[Any] = []
    answers: List[Any] = []

    class Config:
        from_attributes = True


class SessionResponse(SessionInDB):
    topic_name: Optional[str] = None
    current_question: Optional[str] = None
    current_answer: Optional[str] = None