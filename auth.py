from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from cloudinary.uploader import upload
from . import crud, models, schemas, database, utils
from .config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register/", response_model=schemas.User, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), background_tasks: BackgroundTasks):
    """
    Register a new user.

    Args:
        user (schemas.UserCreate): User data for registration.
        db (Session): Database session dependency.
        background_tasks (BackgroundTasks): Background tasks dependency.

    Returns:
        schemas.User: The registered user.

    Raises:
        HTTPException: If the email is already registered.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = utils.hash_password(user.password)
    new_user = crud.create_user(db=db, user=user)
    
    send_verification_email.delay(new_user.email, new_user.id)
    
    return new_user


@router.get("/verify/")
def verify_email(token: str, db: Session = Depends(database.get_db)):
    """
    Verify user's email using a token.

    Args:
        token (str): Verification token.
        db (Session): Database session dependency.

    Returns:
        dict: Success message if the email is verified.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        
        db_user = crud.update_user_verification_status(db=db, user_id=user_id, is_verified=True)
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return {"message": "Email successfully verified"}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

@background_tasks.add_task
def send_verification_email(email_to: str, user_id: int):
    """
    Send verification email to the user.

    Args:
        email_to (str): Recipient email address.
        user_id (int): User ID for creating verification token.
    """
    token = create_verification_token(user_id)
    message = MessageSchema(
        subject="Email Verification",
        recipients=[email_to],
        body=f"Click the following link to verify your email: {settings.BACKEND_URL}/verify/?token={token}",
        subtype="html"
    )
    fm = FastMail(settings.MAIL_CONFIG)
    fm.send_message(message)

def create_verification_token(user_id: int) -> str:
    """
    Create a verification token for email confirmation.

    Args:
        user_id (int): User ID.

    Returns:
        str: Generated JWT token.
    """
    delta = timedelta(hours=24)
    now = datetime.utcnow()
    exp = now + delta
    exp_timestamp = int(exp.timestamp())
    return jwt.encode({"sub": str(user_id), "exp": exp_timestamp}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def update_avatar(current_user: models.User, avatar_url: str, db: Session):
    """
    Update user's avatar.

    Args:
        current_user (models.User): Current user model.
        avatar_url (str): URL of the new avatar.
        db (Session): Database session dependency.

    Returns:
        models.User: Updated user model.
    """
    upload_response = cloudinary.uploader.upload(avatar_url)
    current_user.avatar_url = upload_response['secure_url']
    db.commit()
    db.refresh(current_user)
    return current_user


