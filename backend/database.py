import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Отримуємо адресу бази з налаштувань сервера (Render)
# Якщо налаштувань немає — використовуємо локальний файл SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gis_ops.db")

# Хак для Render: він видає адресу "postgres://", а SQLAlchemy хоче "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Налаштування для різних баз
connect_args = {}

if "sqlite" in DATABASE_URL:
    # SQLite потребує цього аргументу
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()