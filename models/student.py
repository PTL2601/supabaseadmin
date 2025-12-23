from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class StudentBase(BaseModel):
    fullname: Optional[str] = None
    token: str
    tgid: Optional[int] = None
    isactive: Optional[bool] = True
    group: Optional[str] = Field(None, alias="Group")


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    fullname: Optional[str] = None
    tgid: Optional[int] = None
    isactive: Optional[bool] = None
    group: Optional[str] = None


class Student(StudentBase):
    id: int
    createdat: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class StudentResponse(BaseModel):
    success: bool
    data: Optional[Student] = None
    message: Optional[str] = None


class StudentListResponse(BaseModel):
    success: bool
    data: List[Student]
    total: int
    page: int
    page_size: int