from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class ContactCreate(BaseModel):
    """
    Схема для створення нового контакту.

    Attributes:
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (EmailStr): Електронна адреса контакту.
        phone_number (str): Номер телефону контакту.
        birthday (date): Дата народження контакту.
        additional_info (Optional[str], optional): Додаткова інформація про контакт.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None

class Contact(BaseModel):
    """
    Схема для відображення контакту.

    Attributes:
        id (int): Ідентифікатор контакту.
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (EmailStr): Електронна адреса контакту.
        phone_number (str): Номер телефону контакту.
        birthday (date): Дата народження контакту.
        additional_info (Optional[str], optional): Додаткова інформація про контакт.

    Config:
        orm_mode (bool): Показує, що модель може бути отримана напряму з ORM.
    """
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    """
    Схема для створення нового користувача.

    Attributes:
        email (EmailStr): Електронна адреса користувача.
        password (str): Пароль користувача.
    """
    email: EmailStr
    password: str

class User(BaseModel):
    """
    Схема для відображення користувача.

    Attributes:
        id (int): Ідентифікатор користувача.
        email (EmailStr): Електронна адреса користувача.
        is_verified (bool): Показує, чи верифікований користувач.

    Config:
        orm_mode (bool): Показує, що модель може бути отримана напряму з ORM.
    """
    id: int
    email: EmailStr
    is_verified: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    Схема для представлення токену.

    Attributes:
        access_token (str): Токен доступу.
        refresh_token (str): Токен оновлення.
        token_type (str): Тип токену.
    """
    access_token: str
    refresh_token: str
    token_type: str


    