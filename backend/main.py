from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
import uuid
from typing import Optional

from .database import (
    init_db, create_user, get_user_by_username, get_user_by_id,
    get_all_products, get_product_by_id, create_order, get_user_orders,
    execute_query
)
from .auth import verify_password, get_password_hash, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .models import (
    UserRegister, UserLogin, UserResponse, Token,
    ProductResponse, OrderCreate, OrderResponse, SQLQuery
)

app = FastAPI(title="E-Commerce API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return int(user_id)


# Routes
@app.get("/")
async def root():
    return {"message": "E-Commerce API", "docs": "/docs"}


@app.post("/api/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if user exists
    existing_user = await get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    password_hash = get_password_hash(user_data.password)
    user_id = await create_user(user_data.username, user_data.email, password_hash)
    
    # Get created user
    user = await get_user_by_id(user_id)
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.post("/api/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    user = await get_user_by_username(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/products", response_model=list[ProductResponse])
async def get_products():
    """Get all products"""
    products = await get_all_products()
    return [ProductResponse(**product) for product in products]


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get a single product by ID"""
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return ProductResponse(**product)


@app.post("/api/orders", response_model=dict)
async def create_order_endpoint(
    order_data: OrderCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new order (requires authentication)"""
    
    # Generate unique order ID
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Create order
    order_db_id = await create_order(
        user_id=user_id,
        order_id=order_id,
        total_amount=order_data.total_amount,
        items=[item.dict() for item in order_data.items]
    )
    
    return {
        "order_id": order_id,
        "id": order_db_id,
        "status": "created",
        "total_amount": order_data.total_amount
    }


@app.get("/api/orders", response_model=list[dict])
async def get_orders(user_id: int = Depends(get_current_user_id)):
    """Get user's order history (requires authentication)"""
    orders = await get_user_orders(user_id)
    
    # Group orders by order_id
    orders_dict = {}
    for order in orders:
        order_id = order["order_id"]
        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "order_id": order_id,
                "order_date": order["order_date"],
                "total_amount": order["total_amount"],
                "order_status": order["order_status"],
                "items": []
            }
        orders_dict[order_id]["items"].append({
            "product_id": order["product_id"],
            "product_name": order["product_name"],
            "quantity": order["quantity"],
            "unit_price": order["unit_price"]
        })
    
    return list(orders_dict.values())


@app.post("/api/query")
async def execute_sql_query(
    query_data: SQLQuery,
    user_id: int = Depends(get_current_user_id)
):
    """Execute SQL query (admin only)"""
    
    # Check if user is admin
    user = await get_user_by_id(user_id)
    if not user or user["username"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can execute SQL queries"
        )
    
    try:
        results = await execute_query(query_data.query)
        return {"results": results, "row_count": len(results)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

