"""CRUD operations for Product."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    """Creates a new product."""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    """Gets a product by ID."""
    result = await db.execute(
        select(Product).options(selectinload(Product.category)).filter(Product.id == product_id)
    )
    return result.scalars().first()


async def get_product_by_sku(db: AsyncSession, sku: str) -> Product | None:
    """Gets a product by SKU."""
    result = await db.execute(
        select(Product).filter(Product.sku == sku)
    )
    return result.scalars().first()


async def get_all_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = None,
    is_available: bool | None = None
) -> list[Product]:
    """Gets products with filtering."""
    query = select(Product).options(selectinload(Product.category))
    
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    if is_available is not None:
        query = query.filter(Product.is_available == is_available)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_product(db: AsyncSession, product_id: int, product_update: ProductUpdate) -> Product | None:
    """Updates a product."""
    db_product = await get_product_by_id(db, product_id)
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Deletes a product."""
    db_product = await get_product_by_id(db, product_id)
    if not db_product:
        return False
    
    db.delete(db_product)
    await db.commit()
    return True


async def decrease_product_stock(db: AsyncSession, product_id: int, quantity: int) -> Product | None:
    """Decreases product stock."""
    db_product = await get_product_by_id(db, product_id)
    if not db_product or db_product.stock < quantity:
        return None
    
    db_product.stock -= quantity
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def increase_product_stock(db: AsyncSession, product_id: int, quantity: int) -> Product | None:
    """Increases product stock."""
    db_product = await get_product_by_id(db, product_id)
    if not db_product:
        return None
    
    db_product.stock += quantity
    await db.commit()
    await db.refresh(db_product)
    return db_product