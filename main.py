from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from dotenv import load_dotenv
import os
import redis

from . import models, schemas, crud, auth
from .database import SessionLocal, engine
from .config import settings

load_dotenv()

# Створення бази даних
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Налаштування обмежень
limiter = FastAPILimiter(
    key_func=lambda _: "global",  
    rate_limits={
        "contacts": "100/minute",  
        "register": "5/minute",    
    }
)

# Увімкнення CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """
    Функція для отримання об'єкту сесії бази даних.

    Returns:
        Session: Об'єкт сесії SQLAlchemy для взаємодії з базою даних.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """
    Функція, яка виконується при запуску додатку.

    Ініціалізує обмеження доступу до API за допомогою Redis.
    """
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
    await limiter.init(redis_client)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Функція, яка виконується при зупинці додатку.

    Вимикає обмеження доступу до API.
    """
    await limiter.shutdown()

@app.post("/register/", response_model=schemas.User, dependencies=[Depends(RateLimiter(limit="5/minute"))])
async def register_user(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Реєстрація нового користувача.

    Args:
        user (schemas.UserCreate): Об'єкт, що містить дані для створення нового користувача.
        background_tasks (BackgroundTasks): Об'єкт для асинхронного виконання завдань в фоновому режимі.
        db (Session, optional): Сесія бази даних SQLAlchemy. За замовчуванням отримується через функцію get_db.

    Returns:
        schemas.User: Об'єкт користувача, що був створений.

    Raises:
        HTTPException: Якщо користувач з вказаною електронною адресою вже існує.
    """
    return await auth.register_user(user, db, background_tasks)

@app.get("/notes/", response_model=List[schemas.Note])
async def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Отримання списку нотаток.

    Args:
        skip (int, optional): Кількість записів, які треба пропустити. За замовчуванням 0.
        limit (int, optional): Максимальна кількість записів для повернення. За замовчуванням 10.
        db (Session, optional): Сесія бази даних SQLAlchemy. За замовчуванням отримується через функцію get_db.

    Returns:
        List[schemas.Note]: Список об'єктів нотаток.

    Raises:
        HTTPException: Якщо виникла помилка під час отримання нотаток.
    """
    return crud.get_notes(db, skip=skip, limit=limit)

@app.post("/token/", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Отримання доступового токену для аутентифікації користувача.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): Форма, що містить дані для аутентифікації. За замовчуванням отримується через завжди єкт.
        db (Session, optional): Сесія бази даних SQLAlchemy. За замовчуванням отримується через функцію get_db.

    Returns:
        schemas.Token: Об'єкт, що містить доступовий токен.

    Raises:
        HTTPException: Якщо користувач з вказаними обліковими даними не знайдений або пароль неправильний.
    """
    return auth.login_for_access_token(form_data, db)

@app.post("/contacts/", response_model=schemas.Contact, dependencies=[Depends(RateLimiter(limit="100/minute"))])
def create_contact(contact: schemas.ContactCreate, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    Створення нового контакту.

    Args:
        contact (schemas.ContactCreate): Об'єкт, що містить дані для створення нового контакту.
        current_user (schemas.User, optional): Поточний користувач. За замовчуванням отримується через функцію auth.get_current_user.
        db (Session, optional): Сесія бази даних SQLAlchemy. За замовчуванням отримується через функцію get_db.

    Returns:
        schemas.Contact: Об'єкт, що містить створений контакт.

    Raises:
        HTTPException: Якщо обмеження швидкості створення контактів перевищено або користувач не авторизований.
    """
    return crud.create_contact(db, contact)

@app.put("/users/avatar/", response_model=schemas.User)
def update_avatar(avatar_url: str, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    Оновлення аватара користувача.

    Args:
        avatar_url (str): URL нового аватара.
        current_user (schemas.User, optional): Поточний користувач. За замовчуванням отримується через функцію auth.get_current_user.
        db (Session, optional): Сесія бази даних SQLAlchemy. За замовчуванням отримується через функцію get_db.

    Returns:
        schemas.User: Об'єкт користувача з оновленим аватаром.
    """
    return auth.update_avatar(current_user, avatar_url, db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    