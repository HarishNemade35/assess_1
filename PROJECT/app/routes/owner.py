from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.owner import OwnerCreate, OwnerResponse
from app.models.owner import Owner
from app.schemas.offer import OfferCreate, OfferResponse
from app.models.offer import Offer
from datetime import datetime, timezone
from app.core.db import get_db
from app.core.auth import create_access_token, authenticate_owner,hash_password
from datetime import datetime

router = APIRouter()

# Register a new owner
@router.post("/register", response_model=OwnerResponse)
def register_owner(owner: OwnerCreate, db: Session = Depends(get_db)):
    """Registers a new owner by checking if the username is already taken and saving the owner to the database."""

    existing_owner = db.query(Owner).filter(Owner.ownername == owner.ownername).first()
    if existing_owner:
        raise HTTPException(status_code=400, detail="Ownername already taken")
    
    # Hash the password before saving it
    new_owner = Owner(ownername=owner.ownername, password=hash_password(owner.password))  # Hash password
    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)
    return new_owner


# Login an existing owner
@router.post("/login")
def login_owner(owner: OwnerCreate, db: Session = Depends(get_db)):
    """Authenticates an owner and returns a JWT token if the credentials are valid."""

    # Authenticate the owner based on username and password
    authenticated_owner = authenticate_owner(db, owner.ownername, owner.password)
    if not authenticated_owner:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

    # Generate and return a JWT token
    token = create_access_token(data={"sub": authenticated_owner.ownername})
    
    return {"access_token": token, "token_type": "bearer"}
