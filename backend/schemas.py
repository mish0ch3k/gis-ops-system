from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IncidentBase(BaseModel):
    title: str = Field(..., example="Пожежа в складському приміщенні")
    description: Optional[str] = Field(None, example="Задимлення, працюють рятувальники")
    category: Optional[str] = Field(None, example="fire")
    severity: Optional[str] = Field("medium", example="high")
    status: Optional[str] = Field("open", example="open")

    latitude: float = Field(..., example=50.4501)
    longitude: float = Field(..., example=30.5234)

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Incident(IncidentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True