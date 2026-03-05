from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.utils.auth_utils import hash_password, verify_password, create_access_token
from backend.utils.database import users_collection

router = APIRouter(tags=["Authentication"])

# In-memory fallback for users when MongoDB is unavailable
_in_memory_users = {}


class UserRegister(BaseModel):
    name: str
    email: str
    phone: str


class UserLogin(BaseModel):
    email: str
    phone: str


@router.post("/register")
def register(user: UserRegister):
    # Check if user already exists
    if users_collection is not None:
        # Use MongoDB if available
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Insert new user
        users_collection.insert_one({
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        })
    else:
        # Use in-memory fallback
        if user.email in _in_memory_users:
            raise HTTPException(status_code=400, detail="User already exists")
        
        _in_memory_users[user.email] = {
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        }
    
    # Auto-login upon registration
    access_token = create_access_token({"sub": user.email})
    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login")
def login(user: UserLogin):
    db_user = None
    
    if users_collection is not None:
        # Use MongoDB if available
        db_user = users_collection.find_one({"email": user.email})
    else:
        # Use in-memory fallback
        db_user = _in_memory_users.get(user.email)
    
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