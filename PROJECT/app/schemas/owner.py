from pydantic import BaseModel

class OwnerBase(BaseModel):
    ownername: str

class OwnerCreate(OwnerBase):
    password: str

class OwnerResponse(OwnerBase):
    id: int

    class Config:
        orm_mode = True
