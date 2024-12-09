from datetime import datetime, timezone
import calendar
from typing import Optional
from app.models.offer import Offer
from app.models.order import Order
from sqlalchemy.orm import Session
from fastapi import HTTPException


# Helper function to check if today is a public holiday or Sunday
def is_public_holiday_or_sunday() -> bool:
    today = datetime.utcnow().date()
    # List of public holidays (for demonstration, add more holidays as required)
    public_holidays = [
        datetime(2024, 1, 1).date(),  # New Year
        datetime(2024, 8, 15).date(),  # Independence Day (example)
        datetime(2024, 1, 26).date()   # Republic Day (example)
        # Add other public holidays here
    ]
    if today.weekday() == calendar.SUNDAY or today in public_holidays:
        return True
    return False


def is_offer_valid(offer_code: str, db: Session, user_id: int) -> Offer:
    # Fetch the offer from the database
    offer = db.query(Offer).filter(Offer.code == offer_code).first()
    if not offer:
        raise HTTPException(status_code=400, detail="Invalid offer code.")  # Return error for invalid offer code

    # Ensure the offer's expiry date is timezone-aware
    if offer.expiry_date.tzinfo is None:
        offer.expiry_date = offer.expiry_date.replace(tzinfo=timezone.utc)  # Make naive datetime aware

    # Check if the offer has expired
    current_time = datetime.now(timezone.utc)  # Use timezone-aware datetime
    if offer.expiry_date < current_time:
        raise HTTPException(status_code=400, detail="Offer code has expired.")  # Return error for expired offer

    # Check if the user has already used or claimed this offer code
    offer_used = db.query(Order).filter(Order.user_id == user_id, Order.offer_code == offer_code).first()
    if offer_used:
        raise HTTPException(status_code=400, detail="Offer code has already been used or claimed by this user.")

    return offer  # If all validations pass, return the offer object


def calculate_discount(order_total: float, offer: Offer) -> float:
    """
    Calculate the discount based on whether the offer is a percentage or a fixed amount.
    """
    if offer.is_percentage:
        discount = order_total * (offer.discount_value / 100)
    else:
        discount = offer.discount_value
    
    # Ensure the discount does not exceed the total amount of the order
    return min(discount, order_total)
