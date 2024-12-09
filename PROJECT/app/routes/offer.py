from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferResponse,OfferUpdate
from app.core.db import get_db
from app.core.auth import get_current_owner
from app.models.owner import Owner
from datetime import datetime, timezone

router = APIRouter()


@router.post("/offers", response_model=OfferResponse)
async def create_offer(
    offer: OfferCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner),  # Assuming it returns an Owner object
):
    # Ensure expiry date is valid
    current_time = datetime.now(timezone.utc)
    if offer.expiry_date < current_time:
        raise HTTPException(status_code=400, detail="Expiry date cannot be in the past")

    # Use the owner_id from the current_owner object
    try:
        new_offer = Offer(**offer.dict(), owner_id=current_owner.id)
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)
        return new_offer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the offer: {str(e)}")


@router.put("/offers/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int, 
    offer_data: OfferUpdate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner),
):
    # Fetch the offer
    offer = db.query(Offer).filter(Offer.id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Ensure the offer belongs to the current owner
    if offer.owner_id != current_owner.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this offer")

    # Update fields dynamically
    for key, value in offer_data.dict(exclude_unset=True).items():
        setattr(offer, key, value)

    db.commit()
    db.refresh(offer)
    return offer





@router.delete("/offers/{offer_id}", status_code=200)
async def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner),
):
    # Fetch the offer
    offer = db.query(Offer).filter(Offer.id == offer_id).first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Ensure the offer belongs to the current owner
    if offer.owner_id != current_owner.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this offer")

    # Delete the offer
    if db.delete(offer):
        raise HTTPException(status_code=200,detail="Offer delete Delete Successfully{offer_id}")

    db.refresh(offer)
    db.commit()

    
