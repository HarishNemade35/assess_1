from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
from app.routes import user, order, offer, product,owner
from app.core.db import engine
from app.models import user as user_model, order as order_model, offer as offer_model, product as product_model,owner as owner_model

# Initialize the FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")
# Initialize Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Render the index.html template
    return templates.TemplateResponse("index.html", {"request": request})




# Register routes
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(order.router, prefix="/order", tags=["Order"])
app.include_router(owner.router,prefix="/owner",tags=["Owner"])
app.include_router(offer.router, prefix="/offer", tags=["Offer"])
app.include_router(product.router, prefix="/product", tags=["Product"])

# Create database tables if they do not exist
@app.on_event("startup")
async def startup():
    user_model.Base.metadata.create_all(bind=engine)
    owner_model.Base.metadata.create_all(bind=engine)
    order_model.Base.metadata.create_all(bind=engine)
    offer_model.Base.metadata.create_all(bind=engine)
    product_model.Base.metadata.create_all(bind=engine)


# Serve the index.html file when the root URL is accessed
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("app", "static", "index.html")) as file:
        return HTMLResponse(content=file.read())



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8002)





