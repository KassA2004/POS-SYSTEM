from typing import List
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.db.models.tenant_models import (
    Order,
    OrderLineItem,
    Payment,
    Product,
    ProductRecipe,
    InventoryWarehouse,
    InventoryTransaction,
)
from app.models.order_schemas import (
    OrderCreateRequest,
    OrderUpdateRequest,
    OrderResponse,
    OrderLineItemResponse,
    PaymentResponse,
)


async def create_order_service(
    db: AsyncSession,
    employee_id: int,
    branch_id: int,
    request: OrderCreateRequest,
) -> OrderResponse:
    """
    Atomically processes a new order:
      1. Validates products and computes pricing & inventory requirements.
      2. Locks inventory rows with FOR UPDATE and verifies sufficient stock.
      3. Deducts stock and logs inventory transaction movements.
      4. Saves order, line items, and payment atomically.
    """
    if not request.line_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one line item.",
        )

    order_num = request.order_number or f"ORD-{int(datetime.now(timezone.utc).timestamp())}-{uuid.uuid4().hex[:6].upper()}"

    # Check for order number duplication
    existing_order = await db.execute(select(Order.id).where(Order.order_number == order_num))
    if existing_order.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order number '{order_num}' already exists.",
        )

    total_amount = Decimal("0.00")
    line_item_records = []
    required_deductions = defaultdict(Decimal)

    # 1. Inspect line items, calculate totals & gather required warehouse deductions
    for item in request.line_items:
        prod_result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = prod_result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found.",
            )
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' (ID {item.product_id}) is inactive.",
            )

        subtotal = product.price * Decimal(item.quantity)
        total_amount += subtotal

        line_item_records.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "unit_price": product.price,
            "subtotal_price": subtotal,
        })

        # Calculate warehouse item requirements
        if product.is_recipe:
            recipe_result = await db.execute(
                select(ProductRecipe).where(ProductRecipe.product_id == product.id)
            )
            recipes = recipe_result.scalars().all()
            if not recipes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{product.name}' is flagged as a recipe but has no recipe ingredients configured.",
                )
            for recipe in recipes:
                required_deductions[recipe.warehouse_item_id] += recipe.quantity_required * Decimal(item.quantity)
        elif product.direct_warehouse_item_id is not None:
            required_deductions[product.direct_warehouse_item_id] += Decimal(item.quantity)

    # Validate payment amount covers total
    if request.payment.amount < total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({request.payment.amount}) is less than order total ({total_amount}).",
        )

    # 2. Pessimistic row locking on required inventory items
    inventory_map = {}
    if required_deductions:
        sorted_item_ids = sorted(required_deductions.keys())
        inv_result = await db.execute(
            select(InventoryWarehouse)
            .where(InventoryWarehouse.warehouse_item_id.in_(sorted_item_ids))
            .with_for_update()
        )
        inventory_map = {inv.warehouse_item_id: inv for inv in inv_result.scalars().all()}

        # Verify stock sufficiency for all required ingredients
        for item_id, req_qty in required_deductions.items():
            inv = inventory_map.get(item_id)
            available = inv.quantity if inv else Decimal("0.000")
            if available < req_qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient inventory stock for warehouse item ID {item_id}: required {req_qty}, available {available}.",
                )

    # 3. Create Order
    new_order = Order(
        branch_id=branch_id,
        employee_id=employee_id,
        order_number=order_num,
        status="paid",
        total_amount=total_amount,
    )
    db.add(new_order)
    await db.flush()  # Generate new_order.id

    # 4. Apply inventory deductions & log transactions
    for item_id, req_qty in required_deductions.items():
        inv = inventory_map[item_id]
        inv.quantity -= req_qty

        inv_tx = InventoryTransaction(
            warehouse_item_id=item_id,
            employee_id=employee_id,
            quantity_change=-req_qty,
            transaction_type="SALE",
            reference_type="ORDER",
            reference_id=new_order.id,
        )
        db.add(inv_tx)

    # 5. Save order line items
    for item_data in line_item_records:
        db.add(OrderLineItem(order_id=new_order.id, **item_data))

    # 6. Save payment
    payment_record = Payment(
        order_id=new_order.id,
        amount=request.payment.amount,
        payment_method=request.payment.payment_method,
        status="SUCCESS",
        reference_number=request.payment.reference_number,
    )
    db.add(payment_record)

    await db.flush()

    return await get_order_by_id_service(db, branch_id, new_order.id)


async def update_order_status_service(
    db: AsyncSession,
    employee_id: int,
    branch_id: int,
    order_id: int,
    request: OrderUpdateRequest,
) -> OrderResponse:
    """
    Handles Order Void / Refund actions and performs inverse inventory stock adjustments.
    """
    target_status = request.status.lower()
    if target_status not in ["voided", "refunded"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order update status must be either 'voided' or 'refunded'.",
        )

    result = await db.execute(
        select(Order)
        .options(selectinload(Order.order_line_items))
        .where(Order.id == order_id, Order.branch_id == branch_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found at this branch.",
        )

    if order.status in ["voided", "refunded"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} is already {order.status}.",
        )

    # Calculate restored warehouse inventory items
    restoration_map = defaultdict(Decimal)
    for line_item in order.order_line_items:
        prod_result = await db.execute(select(Product).where(Product.id == line_item.product_id))
        product = prod_result.scalar_one_or_none()
        if not product:
            continue

        if product.is_recipe:
            recipe_result = await db.execute(
                select(ProductRecipe).where(ProductRecipe.product_id == product.id)
            )
            for recipe in recipe_result.scalars().all():
                restoration_map[recipe.warehouse_item_id] += recipe.quantity_required * Decimal(line_item.quantity)
        elif product.direct_warehouse_item_id is not None:
            restoration_map[product.direct_warehouse_item_id] += Decimal(line_item.quantity)

    # Apply inverse inventory restoration with row locking
    if restoration_map:
        sorted_item_ids = sorted(restoration_map.keys())
        inv_result = await db.execute(
            select(InventoryWarehouse)
            .where(InventoryWarehouse.warehouse_item_id.in_(sorted_item_ids))
            .with_for_update()
        )
        inv_map = {inv.warehouse_item_id: inv for inv in inv_result.scalars().all()}

        for item_id, restore_qty in restoration_map.items():
            inv = inv_map.get(item_id)
            if inv:
                inv.quantity += restore_qty

            inv_tx = InventoryTransaction(
                warehouse_item_id=item_id,
                employee_id=employee_id,
                quantity_change=restore_qty,
                transaction_type="RETURN",
                reference_type=f"ORDER_{target_status.upper()}",
                reference_id=order.id,
            )
            db.add(inv_tx)

    # Update Order & Payments status
    order.status = target_status

    pmt_result = await db.execute(select(Payment).where(Payment.order_id == order.id))
    for pmt in pmt_result.scalars().all():
        pmt.status = target_status.upper()

    await db.flush()
    return await get_order_by_id_service(db, branch_id, order.id)


async def get_orders_service(
    db: AsyncSession,
    branch_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[OrderResponse]:
    """
    Retrieves order history for a branch ordered by creation time.
    """
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.order_line_items), selectinload(Order.payments))
        .where(Order.branch_id == branch_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    orders = result.scalars().all()

    return [
        OrderResponse(
            id=o.id,
            branch_id=o.branch_id,
            employee_id=o.employee_id,
            order_number=o.order_number,
            status=o.status,
            total_amount=o.total_amount,
            created_at=o.created_at,
            updated_at=o.updated_at,
            line_items=[OrderLineItemResponse.model_validate(li) for li in o.order_line_items],
            payments=[PaymentResponse.model_validate(p) for p in o.payments],
        )
        for o in orders
    ]


async def get_order_by_id_service(
    db: AsyncSession,
    branch_id: int,
    order_id: int,
) -> OrderResponse:
    """
    Retrieves full single order details with line items and payments.
    """
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.order_line_items), selectinload(Order.payments))
        .where(Order.id == order_id, Order.branch_id == branch_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found at this branch.",
        )

    return OrderResponse(
        id=order.id,
        branch_id=order.branch_id,
        employee_id=order.employee_id,
        order_number=order.order_number,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        updated_at=order.updated_at,
        line_items=[OrderLineItemResponse.model_validate(li) for li in order.order_line_items],
        payments=[PaymentResponse.model_validate(p) for p in order.payments],
    )
