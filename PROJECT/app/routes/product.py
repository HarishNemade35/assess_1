from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.owner import Owner
from app.schemas.product import ProductCreate, ProductResponse
from app.core.auth import get_current_owner
from app.core.db import get_db
from typing import List

router = APIRouter()

# Add Product API
@router.post("/product", response_model=ProductResponse)
async def add_product(
    product_data: ProductCreate, 
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)):

    """Adds a new product to the database."""
    
    # Check if the product already exists
    existing_product = db.query(Product).filter(Product.name == product_data.name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product already exists.")
    

    # Create and add the product to the database
    # Create and add the product to the database
    product = Product(
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
        owner_id=current_owner.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock
    )


# Get All Products API
@router.get("/get_product", response_model=List[ProductResponse])  # List of products
async def get_all_product(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    """Fetches all products owned by the current owner."""
    if not current_owner:
        raise HTTPException(status_code=404, detail="Not authorized, this is only for Owner")

    # Fetch all products from the database
    products = db.query(Product).all()

    # Convert the products to the ProductResponse model
    return products  # 


# Delete Product API
@router.delete("/product/{product_id}",status_code=200)
async def delete_product(
    Product_int : int,
    db : Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    """Deletes a product owned by the current owner."""  
    product = db.query(Product).filter(Product.id == Product_int).first()
    
    #find order
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Ensure the order belongs to the current user
    # Ensure the product belongs to the current owner
    if not current_owner:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    # Delete the order
    db.delete(product)
    db.commit()

    return {"message": "Product successfully deleted"}
    
