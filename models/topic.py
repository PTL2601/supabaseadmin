from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TopicBase(BaseModel):
    topicname: str
    topicdesc: Optional[str] = None
    subjectid: Optional[int] = None
    isactive: bool = True
    date_of_completion: Optional[datetime] = None
    raglink: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicUpdate(TopicBase):
    pass


class TopicInDB(TopicBase):
    id: int

    class Config:
        from_attributes = True


class TopicResponse(TopicInDB):
    subject_name: Optional[str] = None
    questions_count: int = 0
    completed_count: int = 0