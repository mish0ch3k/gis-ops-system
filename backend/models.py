from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)                # Назва події
    description = Column(String, nullable=True)           # Опис
    category = Column(String, nullable=True)              # Категорія (пожежа, ДТП, військова подія тощо)
    severity = Column(String, nullable=True)              # Рівень (low/medium/high/critical)
    status = Column(String, nullable=True)                # Відкрита/закрита/в процесі

    latitude = Column(Float, nullable=False)              # Широта
    longitude = Column(Float, nullable=False)             # Довгота

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)