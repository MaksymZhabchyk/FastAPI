"""CRUD operations for Order and OrderItem."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Order, OrderItem, Product
from app.schemas.order import OrderCreate


async def create_order(db: AsyncSession, order: OrderCreate) -> Order:
    """Creates a new order."""
    db_order = Order(
        user_id=order.user_id,
        notes=order.notes,
        status="pending"
    )
    db.add(db_order)
    await db.flush()  # To get the order ID
    
    total_amount = 0.0
    
    # Add order items
    if order.items:
        for item in order.items:
            product = await db.get(Product, item.product_id)
            if not product:
                raise ValueError(f"Product with id {item.product_id} not found")
            
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price
            )
            db.add(order_item)
            total_amount += order_item.total_price
    
    db_order.total_amount = total_amount
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    """Gets an order by ID."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .options(selectinload(Order.user))
        .filter(Order.id == order_id)
    )
    return result.scalars().first()


async def get_orders_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> list[Order]:
    """Gets all orders for a user."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .filter(Order.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_all_orders(db: AsyncSession, skip: int = 0, limit: int = 100, status: str | None = None) -> list[Order]:
    """Gets all orders."""
    query = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product))
    
    if status:
        query = query.filter(Order.status == status)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Order | None:
    """Updates an order status."""
    db_order = await get_order_by_id(db, order_id)
    if not db_order:
        return None
    
    db_order.status = status
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    """Deletes an order."""
    db_order = await get_order_by_id(db, order_id)
    if not db_order:
        return False
    
    db.delete(db_order)
    await db.commit()
    return True


async def add_order_item(
    db: AsyncSession,
    order_id: int,
    product_id: int,
    quantity: int,
    unit_price: float
) -> OrderItem | None:
    """Adds an item to an order."""
    order = await get_order_by_id(db, order_id)
    if not order:
        return None
    
    product = await db.get(Product, product_id)
    if not product:
        return None
    
    order_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=quantity * unit_price
    )
    db.add(order_item)
    
    # Update order total amount
    order.total_amount += order_item.total_price
    
    await db.commit()
    await db.refresh(order_item)
    return order_item


async def remove_order_item(db: AsyncSession, order_item_id: int) -> bool:
    """Removes an item from an order."""
    order_item = await db.get(OrderItem, order_item_id)
    if not order_item:
        return False
    
    # Update order total amount
    order = await db.get(Order, order_item.order_id)
    if order:
        order.total_amount -= order_item.total_price
    
    db.delete(order_item)
    await db.commit()
    return True