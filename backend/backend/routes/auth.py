from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.utils.auth_utils import hash_password, verify_password, create_access_token
from backend.utils.database import users_collection

router = APIRouter(tags=["Authentication"])


class UserRegister(BaseModel):
    name: str
    email: str
    phone: str


class UserLogin(BaseModel):
    email: str
    phone: str


@router.post("/register")
def register(user: UserRegister):
    if users_collection is None:
        raise HTTPException(status_code=503, detail="Database connection is not available. Please check MongoDB IP whitelisting.")
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Insert new user
    users_collection.insert_one({
        "name": user.name,
        "email": user.email,
        "phone": user.phone # Storing plain for this specific project flow
    })

    # Auto-login upon registration
    access_token = create_access_token({"sub": user.email})
    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login")
def login(user: UserLogin):
    if users_collection is None:
        raise HTTPException(status_code=503, detail="Database connection is not available. Please check MongoDB IP whitelisting.")

    # Find user in database
    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    # Verify phone (acting as password in this simplified workflow)
    if user.phone != db_user["phone"]:
        raise HTTPException(status_code=400, detail="Incorrect phone number")

    # Create JWT token
    access_token = create_access_token({"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }