import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
from backend.main import app, get_db
from backend import models

# Створюємо клієнт для тестів
client = TestClient(app)

# 1. ТЕСТОВИЙ ДВІЙНИК (MOCK): Імітація сесії бази даних
def override_get_db():
    mock_db = MagicMock()
    try:
        yield mock_db
    finally:
        pass

# --- ТЕСТИ ---

def test_read_main_root():
    """Тест перевіряє, чи працює Swagger UI (документація)"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_create_incident():
    """Тест створення інциденту з використанням Mock об'єкта"""
    
    # Підготовка вхідних даних
    payload = {
        "title": "Test Fire",
        "description": "Testing description",
        "category": "fire",
        "severity": "high",
        "status": "open",
        "latitude": 50.45,
        "longitude": 30.52
    }

    # --- ВИПРАВЛЕННЯ: Налаштовуємо Mock, щоб він повертав об'єкт з ID і датами ---
    mock_session = MagicMock()
    
    # Коли ми зберігаємо об'єкт, ми імітуємо, що БД присвоїла йому ID і дати
    def mock_add(instance):
        instance.id = 1
        instance.created_at = datetime.now()
        instance.updated_at = datetime.now()
    
    mock_session.add.side_effect = mock_add
    
    # Підміняємо залежність
    app.dependency_overrides[get_db] = lambda: mock_session

    # Виклик API
    response = client.post("/api/incidents", json=payload)

    # Отримання даних
    data = response.json()

    # Перевірки
    assert response.status_code == 201
    assert data["title"] == "Test Fire"
    assert data["id"] == 1  # Тепер ID точно буде, бо ми його задали в mock_add
    assert isinstance(data["latitude"], float)

def test_get_incidents_empty():
    """Тест отримання списку, коли база повертає порожній список"""
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.get("/api/incidents")
    assert response.status_code == 200
    assert response.json() == []

def test_get_specific_incident_not_found():
    """Тест на помилку 404, якщо інциденту не існує"""
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.get("/api/incidents/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Інцидент не знайдено"

def test_db_commit_called():
    """Перевірка, чи викликається метод commit() при створенні"""
    
    mock_session = MagicMock()
    
    # Теж додаємо ID, щоб пройти валідацію схеми
    def mock_add(instance):
        instance.id = 2
        instance.created_at = datetime.now()
        instance.updated_at = datetime.now()
    mock_session.add.side_effect = mock_add

    app.dependency_overrides[get_db] = lambda: mock_session

    payload = {
        "title": "Spy Test", 
        "latitude": 10.0, 
        "longitude": 10.0,
        "description": "desc",
        "category": "other",
        "severity": "low",
        "status": "open"
    }
    client.post("/api/incidents", json=payload)

    # Перевіряємо поведінку
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()