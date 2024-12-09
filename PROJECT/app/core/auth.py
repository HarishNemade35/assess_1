from jose import jwt, JWTError
from fastapi import HTTPException, Depends,status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
# from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from app.models.user import User
from app.models.owner import Owner
from app.core.db import get_db
from typing import Dict
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token creation
def create_access_token(data: Dict[str, str], expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token verification
def verify_token(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

def authenticate_user(username: str, password: str, db: Session):
    """
    Authenticate a user by verifying their username and password.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password):  # Verify password
        return user
    return None

def authenticate_owner(db: Session, ownername: str, password: str):
    owner = db.query(Owner).filter(Owner.ownername == ownername).first()
    if owner and verify_password(password, owner.password):
        return owner  # Return the owner if credentials are valid
    return None



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode token
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

# Get current owner
def get_current_owner(token: str, db: Session = Depends(get_db)) -> Owner:
    payload = decode_access_token(token)
    ownername = payload.get("sub")
    print(f"Ownername from token: {ownername}")  # Debugging line
    if not ownername:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - Missing 'sub'",
        )

    owner = db.query(Owner).filter(Owner.ownername == ownername).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Owner not found",
        )

    return owner