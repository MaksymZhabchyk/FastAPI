"""CRUD operations for Category."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
    """Creates a new category."""
    db_category = Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_category_by_id(db: AsyncSession, category_id: int) -> Category | None:
    """Gets a category by ID."""
    result = await db.execute(
        select(Category).options(selectinload(Category.products)).filter(Category.id == category_id)
    )
    return result.scalars().first()


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category | None:
    """Gets a category by slug."""
    result = await db.execute(
        select(Category).filter(Category.slug == slug)
    )
    return result.scalars().first()


async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Category]:
    """Gets all categories."""
    result = await db.execute(
        select(Category).options(selectinload(Category.products)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_category(db: AsyncSession, category_id: int, category_update: CategoryUpdate) -> Category | None:
    """Updates a category."""
    db_category = await get_category_by_id(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    """Deletes a category."""
    db_category = await get_category_by_id(db, category_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    await db.commit()
    return True