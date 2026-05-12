"""API routers for order management."""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderItemCreate
from app.database import get_db
from app.crud import order as order_crud

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=list[Order])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """Gets a list of all orders."""
    orders = await order_crud.get_all_orders(
        db,
        skip=skip,
        limit=limit,
        status=status_filter
    )
    return orders


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates a new order."""
    try:
        return await order_crud.create_order(db, order_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Gets an order by ID."""
    order = await order_crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.get("/user/{user_id}", response_model=list[Order])
async def get_user_orders(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Gets all orders for a user."""
    orders = await order_crud.get_orders_by_user(db, user_id, skip=skip, limit=limit)
    return orders


@router.put("/{order_id}", response_model=Order)
async def update_order_status(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Updates an order status."""
    if not order_data.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status cannot be empty"
        )
    
    order = await order_crud.update_order_status(db, order_id, order_data.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Deletes an order."""
    success = await order_crud.delete_order(db, order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return None


@router.post("/{order_id}/items", status_code=status.HTTP_201_CREATED)
async def add_order_item(
    order_id: int,
    item_data: OrderItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Adds an item to an order."""
    item = await order_crud.add_order_item(
        db,
        order_id,
        item_data.product_id,
        item_data.quantity,
        item_data.unit_price
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order or product not found"
        )
    return item


@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_order_item(
    order_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Removes an item from an order."""
    success = await order_crud.remove_order_item(db, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return None