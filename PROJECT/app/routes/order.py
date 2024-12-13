from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.product import Product
from app.models.offer import Offer
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.schemas.product import ProductCreate, ProductResponse
from app.utils.helpers import is_offer_valid, calculate_discount, is_public_holiday_or_sunday
from app.core.db import get_db
from app.core.auth import get_current_user
from app.models.user import User
from datetime import datetime
from typing import List

router = APIRouter()



@router.get("/get_product", response_model=List[ProductResponse])  # List of products
async def get_all_product(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a list of all products. Accessible only to authenticated users."""

    if not current_user:
        raise HTTPException(status_code=404, detail="Not authorized, this is only for Owner")

    # Fetch all products from the database
    products = db.query(Product).all()

    # Convert the products to the ProductResponse model
    return products  # 


@router.post("/order", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    """Creates a new order, checks for public holidays, product availability, and applies any valid offer code."""
    # Check if today is a public holiday or Sunday
    if is_public_holiday_or_sunday():
        raise HTTPException(
            status_code=400, detail="Orders cannot be placed on public holidays or Sundays."
        )

    # Fetch the product and validate stock
    # Validate product availability and order details
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if product.stock < order_data.quantity:
        raise HTTPException(
            status_code=400, detail="Entered quantity is not available in stock."
        )

    # Calculate the total amount
    total_amount = product.price * order_data.quantity

    # Handle offer code if provided
    # Calculate total and apply offer (if any)
    discount_amount = 0.0
    if order_data.offer_code:
        offer = is_offer_valid(order_data.offer_code, db, user_id)
        if not offer:
            raise HTTPException(status_code=400, detail="Invalid or expired offer code.")
        if offer.product_id and offer.product_id != order_data.product_id:
            raise HTTPException(
                status_code=400, detail="Offer code is not applicable for this product."
            )
        discount_amount = calculate_discount(total_amount, offer)

    # Calculate final amount
    # Create and save the order
    final_amount = total_amount - discount_amount
    if final_amount < 99 or final_amount > 4999:
        raise HTTPException(
            status_code=400, detail="Order amount must be between ₹99 and ₹4,999 after discount."
        )

    # Create the order
    # Get an order by ID
    order = Order(
        user_id=user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        offer_code=order_data.offer_code,
        total_amount=total_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        created_at=datetime.utcnow(),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        product_id=order.product_id,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
        created_at=order.created_at.isoformat(),
    )


# Get an order by ID
@router.get("/order/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the order from the database
    """Fetches a specific order by its ID. Accessible only to the user who created the order."""
    order = db.query(Order).filter(Order.id == order_id).first()

    # Check if the order exists
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if the user is authorized to view this order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this order."
        )

    # Return the order details
    return OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        product_id=order.product_id,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
        created_at=order.created_at.isoformat(),
    )

    


@router.put("/order/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the order
    """Updates an existing order if the user is authorized."""
    order = db.query(Order).filter(Order.id == order_id).first()

    # Check if the order exists
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if the user is authorized to update this order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this order."
        )

    # Update product if it has changed
    # Update order details (product and quantity)
    if order_data.product_id is not None and order_data.product_id != order.product_id:
        product = db.query(Product).filter(Product.id == order_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        if product.stock < (order_data.quantity or order.quantity):  # Check stock
            raise HTTPException(
                status_code=400,
                detail="Entered quantity is not available in stock."
            )
        order.product_id = order_data.product_id

    # Update quantity if provided
    if order_data.quantity is not None:
        if order.product_id:
            product = db.query(Product).filter(Product.id == order.product_id).first()
            if product.stock < order_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail="Entered quantity is not available in stock."
                )
        order.quantity = order_data.quantity

    # Commit the changes
    # Commit and return updated order
    db.commit()
    db.refresh(order)

    # Return updated order
    return OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        product_id=order.product_id,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
        created_at=order.created_at.isoformat(),
    )


@router.delete("/order/{order_id}", status_code=204)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the order
    """Deletes an order if it belongs to the authenticated user."""
    order = db.query(Order).filter(Order.id == order_id).first()

    # Check if the order exists
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if the user is authorized to delete this order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this order."
        )

    # Delete the order
    db.delete(order)
    db.commit()

    return {"message": "Order successfully deleted"}
    


# Add product to an existing order
@router.post("/order/{order_id}/add-product", response_model=OrderResponse)
async def add_product_to_order(
    order_id: int,
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch the order by ID
    """Adds a product to an existing order if stock is available and final amount is within limits."""
    order = db.query(Order).filter(Order.id == order_id).first()

    # Check if the order exists
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if the order belongs to the current user
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this order")

    # Fetch the product by ID
    product = db.query(Product).filter(Product.id == product_id).first()

    # Check if the product exists
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check product stock availability
    if product.stock < quantity:
        raise HTTPException(
            status_code=400, detail="Entered quantity is not available in stock"
        )

    # Update the total amount and quantities
    additional_amount = product.price * quantity
    new_total_amount = order.total_amount + additional_amount

    # Ensure the updated final amount is within limits
    if new_total_amount < 99 or new_total_amount > 4999:
        raise HTTPException(
            status_code=400,
            detail="Order amount must be between ₹99 and ₹4,999 after adding the product",
        )

    # Update the order
    order.quantity += quantity  # Update quantity
    order.total_amount = new_total_amount
    order.final_amount = new_total_amount  # Assuming no discounts apply to the new product
    order.created_at = datetime.utcnow()


    # Commit changes to the database
    db.commit()
    db.refresh(order)

    # Return the updated order
    return OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        product_id=product_id,
        total_amount=order.total_amount,# Assuming no discounts apply
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
        created_at=order.created_at.isoformat(),
    )



