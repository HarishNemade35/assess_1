from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Updated import
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()  # This loads the variables from the .env file

# Get the DATABASE_URL from environment variables (you should have this in your .env file)
DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise ValueError("DATABASE_URL not found in .env file")


# Create the database engine
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
engine = create_engine(DATABASE_URL)
# SessionLocal to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()  # Updated to use sqlalchemy.orm.declarative_base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
