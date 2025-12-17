import aiosqlite
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "database.db"


async def get_db():
    """Get database connection"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database with all tables"""
    db = await get_db()
    
    # Create users table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """)
    
    # Create products table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL,
            category TEXT,
            availability_status TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """)
    
    # Create orders table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            order_status TEXT DEFAULT 'pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create order_items table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_item_id TEXT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    await db.commit()
    await db.close()


async def create_user(username: str, email: str, password_hash: str) -> int:
    """Create a new user and return user ID"""
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    await db.commit()
    user_id = cursor.lastrowid
    await db.close()
    return user_id


async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE username = ? AND deleted_at IS NULL",
        (username,)
    )
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return None


async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL",
        (user_id,)
    )
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return None


async def insert_product(product_data: Dict[str, Any]) -> int:
    """Insert a product and return product ID"""
    db = await get_db()
    cursor = await db.execute(
        """INSERT INTO products (product_id, product_name, description, price, 
           stock_quantity, category, availability_status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            product_data.get('id'),
            product_data.get('title', ''),
            product_data.get('description', ''),
            product_data.get('price', 0),
            product_data.get('stock', 0),
            product_data.get('category', ''),
            product_data.get('availabilityStatus', 'In Stock')
        )
    )
    await db.commit()
    product_id = cursor.lastrowid
    await db.close()
    return product_id


async def get_all_products() -> List[Dict[str, Any]]:
    """Get all products"""
    db = await get_db()
    cursor = await db.execute(
        """SELECT id, product_id, product_name, description, price, 
           stock_quantity, category, availability_status, created_date
           FROM products WHERE deleted_at IS NULL ORDER BY product_name ASC"""
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]


async def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Get product by ID"""
    db = await get_db()
    cursor = await db.execute(
        """SELECT id, product_id, product_name, description, price, 
           stock_quantity, category, availability_status, created_date
           FROM products WHERE id = ? AND deleted_at IS NULL""",
        (product_id,)
    )
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return None


async def create_order(user_id: int, order_id: str, total_amount: float, 
                      items: List[Dict[str, Any]]) -> int:
    """Create an order and order items"""
    db = await get_db()
    
    # Create order
    cursor = await db.execute(
        """INSERT INTO orders (order_id, user_id, total_amount, order_status)
           VALUES (?, ?, ?, 'pending')""",
        (order_id, user_id, total_amount)
    )
    order_db_id = cursor.lastrowid
    
    # Create order items
    for item in items:
        await db.execute(
            """INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price)
               VALUES (?, ?, ?, ?, ?)""",
            (
                f"{order_id}-{item['product_id']}",
                order_db_id,
                item['product_id'],
                item['quantity'],
                item['unit_price']
            )
        )
    
    await db.commit()
    await db.close()
    return order_db_id


async def get_user_orders(user_id: int) -> List[Dict[str, Any]]:
    """Get all orders for a user"""
    db = await get_db()
    cursor = await db.execute(
        """SELECT o.id, o.order_id, o.order_date, o.total_amount, o.order_status,
           oi.order_item_id, oi.product_id, oi.quantity, oi.unit_price,
           p.product_name, p.stock_quantity
           FROM orders o
           INNER JOIN order_items oi ON o.id = oi.order_id
           INNER JOIN products p ON oi.product_id = p.id
           WHERE o.user_id = ? AND o.deleted_at IS NULL
           ORDER BY o.order_date DESC""",
        (user_id,)
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]


async def execute_query(sql: str) -> List[Dict[str, Any]]:
    """Execute a SQL query and return results (admin only)"""
    db = await get_db()
    try:
        cursor = await db.execute(sql)
        rows = await cursor.fetchall()
        await db.commit()
        await db.close()
        return [dict(row) for row in rows]
    except Exception as e:
        await db.close()
        raise e

