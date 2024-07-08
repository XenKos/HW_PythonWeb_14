import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordRequestForm
from app import main, auth, models, crud, schemas
from app.database import Base, get_db
from app.config import settings

# Override database URL for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Set up a test database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency to override get_db with a testing session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override app's dependencies with testing versions
main.app.dependency_overrides[main.get_db] = override_get_db

# Create a test client using the FastAPI app
client = TestClient(main.app)

def test_register_user():
    """
    Тестує реєстрацію нового користувача через маршрут /register/.

    """
    user_data = {
        "email": "test@example.com",
        "password": "password",
        "full_name": "Test User"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert response.json()["full_name"] == user_data["full_name"]

def test_login_for_access_token():
    """
    Тестує отримання доступового токену для аутентифікації через маршрут /token/.

    """
    form_data = OAuth2PasswordRequestForm(username="test@example.com", password="password")
    response = client.post("/token/", data=form_data.dict())
    assert response.status_code == 200
    assert "access_token" in response.json()

