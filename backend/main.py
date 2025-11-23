from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, date
from typing import List, Optional
from . import models, schemas
from .database import engine, SessionLocal, Base

# Створити таблиці
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GIS Operational Situation API",
    description="API для веб-системи відображення оперативної обстановки",
    version="0.2.0"
)

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
#   API ENDPOINTS
# ---------------------------

@app.get("/api/incidents", response_model=List[schemas.Incident])
def list_incidents(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,  # Пошук по тексту
    start_date: Optional[date] = None, # Фільтр дати "від"
    end_date: Optional[date] = None,   # Фільтр дати "до"
    db: Session = Depends(get_db)
):
    query = db.query(models.Incident)

    if category:
        query = query.filter(models.Incident.category == category)
    if severity:
        query = query.filter(models.Incident.severity == severity)
    if status:
        query = query.filter(models.Incident.status == status)
    
    # Пошук по назві АБО опису
    if q:
        search = f"%{q}%"
        query = query.filter(or_(
            models.Incident.title.ilike(search),
            models.Incident.description.ilike(search)
        ))
    
    # Фільтрація по даті
    if start_date:
        query = query.filter(models.Incident.created_at >= start_date)
    if end_date:
        # Додаємо час 23:59:59 до дати закінчення
        query = query.filter(models.Incident.created_at <= datetime.combine(end_date, datetime.max.time()))

    return query.order_by(models.Incident.created_at.desc()).all()

@app.get("/api/incidents/{incident_id}", response_model=schemas.Incident)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Інцидент не знайдено")
    return incident

@app.post("/api/incidents", response_model=schemas.Incident, status_code=201)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    db_incident = models.Incident(
        title=incident.title,
        description=incident.description,
        category=incident.category,
        severity=incident.severity,
        status=incident.status,
        latitude=incident.latitude,
        longitude=incident.longitude,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@app.put("/api/incidents/{incident_id}", response_model=schemas.Incident)
def update_incident(
    incident_id: int,
    incident_update: schemas.IncidentUpdate,
    db: Session = Depends(get_db)
):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Інцидент не знайдено")

    for field, value in incident_update.dict(exclude_unset=True).items():
        setattr(incident, field, value)

    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident

@app.delete("/api/incidents/{incident_id}", status_code=204)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Інцидент не знайдено")
    db.delete(incident)
    db.commit()
    return