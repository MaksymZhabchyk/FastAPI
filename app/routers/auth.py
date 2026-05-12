import bcrypt
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import User # Якщо будуть помилки з Order/Profile, поки приберемо їх
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserMe,
)

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])

# --- ДОПОМІЖНІ ФУНКЦІЇ ---

def hash_password(password: str) -> str:
    """Хешування пароля через чистий bcrypt."""
    salt = bcrypt.gensalt()
    # Обрізаємо до 72 символів, щоб bcrypt не видавав помилку ValueError
    pwd_bytes = password[:72].encode('utf-8')
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевірка пароля."""
    return bcrypt.checkpw(plain_password[:72].encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(subject: str) -> str:
    """Створення JWT токена."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

async def get_current_user(
    access_token: str | None = Cookie(default=None, alias=settings.cookie_name),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Отримання користувача з куки."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Видаляємо 'Bearer ', якщо він є
        token = access_token.replace("Bearer ", "") if access_token.startswith("Bearer ") else access_token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- РУЧКИ (ENDPOINTS) ---

@router.post("/register", response_model=UserMe, status_code=201)
async def register_user(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    # Перевірка, чи існує юзер (щоб не було IntegrityError 500)
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Створюємо юзера. Передаємо ТІЛЬКИ ті поля, які є в таблиці 4-ї лаби
    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        email=f"{user_data.username}@example.com" # Поле email зазвичай обов'язкове
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        print(f"Критична помилка бази: {e}")
        raise HTTPException(status_code=500, detail="Database Error")

@router.post("/login", response_model=MessageResponse)
async def login_user(
    credentials: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(subject=user.username)
    response.set_cookie(
        key=settings.cookie_name,
        value=f"Bearer {token}",
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax"
    )
    return {"message": "Login successful"}

@router.get("/me", response_model=UserMe)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(settings.cookie_name)
    return {"message": "Logout successful"}