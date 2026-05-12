import asyncio
import bcrypt  # Імпортуємо bcrypt напряму
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, AsyncSessionLocal
from app.models import Category, Product, User

async def get_password_hash(password: str):
    # Використовуємо bcrypt напряму, щоб обійти баг passlib
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def init_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(id) FROM categories"))
        count = result.scalar()
        
        if count == 0:
            print("Наповнюємо базу даними...")
            
            # Створюємо категорії
            cat1 = Category(name="Ноутбуки", description="Потужні лептопи", slug="laptops")
            cat2 = Category(name="Смартфони", description="Мобільні телефони", slug="smartphones")
            session.add_all([cat1, cat2])
            await session.commit()
            await session.refresh(cat1)
            await session.refresh(cat2)
            
            # Створюємо товари
            prod1 = Product(name="MacBook Pro 14", description="M2 Pro chip", price=2000.0, stock=10, category_id=cat1.id, sku="MAC-001")
            prod2 = Product(name="iPhone 15 Pro", description="Titanium body", price=1100.0, stock=25, category_id=cat2.id, sku="IPH-015")
            session.add_all([prod1, prod2])
            
            # Створюємо тестового користувача
            hashed_pwd = await get_password_hash("testpassword")
            user1 = User(username="admin", email="admin@test.com", hashed_password=hashed_pwd)
            session.add(user1)
            
            await session.commit()
            print("База успішно наповнена!")
        else:
            print("Дані вже існують.")

async def main():
    print("Запуск init_db...")
    await init_data()
    # Закриваємо з'єднання
    await engine.dispose()
    print("Готово.")

if __name__ == "__main__":
    asyncio.run(main())