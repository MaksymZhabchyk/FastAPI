"""CRUD operations for User."""

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import User
from app.schemas.user import UserCreate, UserUpdate

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє пароль за допомогою bcrypt."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Створює нового користувача. 
    Очікується, що user.password вже захешовано у роутері.
    """
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=user.password,  # Тут уже лежить хеш із роутера
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Отримує користувача за ID."""
    result = await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.id == user_id)
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Отримує користувача за іменем (username)."""
    result = await db.execute(
        select(User).filter(User.username == username)
    )
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Отримує користувача за email."""
    result = await db.execute(
        select(User).filter(User.email == email)
    )
    return result.scalars().first()

async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Отримує список усіх користувачів."""
    result = await db.execute(
        select(User).options(selectinload(User.profile)).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User | None:
    """Оновлює дані користувача."""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        # Якщо в оновленні є пароль, його треба було б хешувати, 
        # але зазвичай для зміни пароля роблять окремий ендпоінт.
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Видаляє користувача."""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    await db.delete(db_user)
    await db.commit()
    return True