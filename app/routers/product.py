"""API routers for product management."""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.database import get_db
from app.crud import product as product_crud

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = Query(None),
    is_available: bool | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Gets a list of all products with filtering."""
    products = await product_crud.get_all_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        is_available=is_available
    )
    return products


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates a new product."""
    # Check SKU uniqueness
    existing_product = await product_crud.get_product_by_sku(db, product_data.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    return await product_crud.create_product(db, product_data)


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Gets a product by ID."""
    product = await product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates a product."""
    product = await product_crud.update_product(db, product_id, product_data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a product."""
    success = await product_crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return None