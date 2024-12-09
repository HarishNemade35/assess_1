from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.core.auth import create_access_token, authenticate_user,hash_password
from app.core.db import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = User(username=user.username, password=hash_password(user.password))  # Hash password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    # Pass arguments in the correct order (username, password, db)
    authenticated_user = authenticate_user(user.username, user.password, db)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": authenticated_user.username})  # Create token
    return {"access_token": token, "token_type": "bearer"}
