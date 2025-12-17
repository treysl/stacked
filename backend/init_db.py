import asyncio
import httpx
import sys
import os

# Add parent directory to path for standalone execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, create_user, insert_product, get_db
from auth import get_password_hash


async def fetch_products_from_dummyjson():
    """Fetch products from dummyjson.com API"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://dummyjson.com/products")
        if response.status_code == 200:
            data = response.json()
            return data.get('products', [])
        else:
            print(f"Error fetching products: {response.status_code}")
            return []


async def initialize_database():
    """Initialize database with tables, admin user, and products"""
    print("Initializing database...")
    
    # Initialize database tables
    await init_db()
    print("[OK] Database tables created")
    
    # Create admin user
    admin_password_hash = get_password_hash("password")
    try:
        admin_id = await create_user("admin", "admin@example.com", admin_password_hash)
        print("[OK] Admin user created (username: admin, password: password)")
    except Exception as e:
        # User might already exist
        print(f"[INFO] Admin user already exists or error: {e}")
    
    # Fetch and insert products
    print("Fetching products from dummyjson.com...")
    products = await fetch_products_from_dummyjson()
    
    if products:
        print(f"Found {len(products)} products. Inserting into database...")
        inserted_count = 0
        for product in products:
            try:
                await insert_product(product)
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting product {product.get('id', 'unknown')}: {e}")
        
        print(f"[OK] Inserted {inserted_count} products into database")
    else:
        print("[WARNING] No products fetched from dummyjson.com")
    
    print("\nDatabase initialization complete!")
    print("You can now start the backend server with: uvicorn backend.main:app --reload")


if __name__ == "__main__":
    asyncio.run(initialize_database())

