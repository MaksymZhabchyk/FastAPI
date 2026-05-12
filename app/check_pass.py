import asyncio
from sqlalchemy import select
from app.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

async def check_hash():
    # Створюємо тимчасову сесію
    async with AsyncSession(engine) as session:
        # Шукаємо твого юзера
        query = select(User).where(User.username == "Maksym_Final")
        result = await session.execute(query)
        user = result.scalars().first()
        
        if user:
            print("\n" + "="*50)
            print(f"Користувач: {user.username}")
            print(f"Солоний хеш: {user.hashed_password}")
            print("="*50 + "\n")
        else:
            print("Користувача не знайдено!")

if __name__ == "__main__":
    asyncio.run(check_hash())