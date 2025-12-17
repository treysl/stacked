# Simple E-Commerce Platform

A minimal full-stack e-commerce platform built for educational purposes. This application demonstrates the relationship between frontend, backend, and database layers.

## Features

- **Product Browsing**: View products fetched from dummyjson.com and stored in local database
- **Shopping Cart**: Add products to cart and manage quantities
- **User Authentication**: Register and login with JWT token-based authentication
- **Order Management**: Place orders and view order history
- **SQL Query Interface**: Admin users can execute SQL queries directly (for educational purposes)

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Authentication**: JWT tokens

## Project Structure

```
stacked/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection & models
│   ├── auth.py              # JWT authentication utilities
│   ├── models.py            # Pydantic models
│   └── init_db.py           # Database initialization script
├── frontend/
│   ├── index.html           # Product listing page
│   ├── cart.html            # Shopping cart page
│   ├── login.html           # Login/Register page
│   ├── orders.html          # Order history page
│   ├── styles.css           # Shared styles
│   └── app.js               # Frontend JavaScript
├── database.db              # SQLite database file (auto-created)
├── requirements.txt         # Python dependencies
├── start-server.bat         # Windows batch file to start backend server
├── stop-server.bat          # Windows batch file to stop backend server
├── start-frontend.bat       # Windows batch file to start frontend server
└── README.md                # This file
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

This will create the database tables, create an admin user, and fetch products from dummyjson.com:

```bash
python backend/init_db.py
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `password`

### 3. Start Backend Server

**Option 1: Using batch file (Windows)**
```bash
start-server.bat
```

**Option 2: Using command line**
```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8001`
API documentation will be available at `http://localhost:8001/docs`

**To stop the server:**
- If using batch file: Run `stop-server.bat` or press Ctrl+C in the server window
- If using command line: Press Ctrl+C

### 4. Start Frontend Server

**IMPORTANT:** You must use a web server to run the frontend. Opening HTML files directly (`file://`) will cause CORS errors.

**Option 1: Using batch file (Windows)**
```bash
start-frontend.bat
```

**Option 2: Using command line**
```bash
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080/index.html` in your browser.

**Note:** Both the backend server (port 8001) and frontend server (port 8080) need to be running simultaneously.

## Usage

### As a Regular User

1. **Browse Products**: Visit the products page to see all available items
2. **Add to Cart**: Click "Add to Cart" on any product
3. **View Cart**: Navigate to the cart page to review items
4. **Register/Login**: Create an account or login with existing credentials
5. **Checkout**: Place an order from the cart page
6. **View Orders**: See your order history on the orders page

### As Admin User

1. Login with admin credentials (username: `admin`, password: `password`)
2. Use the SQL query endpoint to execute queries:
   - Endpoint: `POST /api/query`
   - Body: `{"query": "SELECT * FROM products LIMIT 10;"}`
   - Requires Authorization header with Bearer token

## API Endpoints

- `POST /api/register` - Register a new user
- `POST /api/login` - Login and get JWT token
- `GET /api/products` - Get all products
- `GET /api/products/{id}` - Get single product
- `POST /api/orders` - Create order (requires auth)
- `GET /api/orders` - Get user's order history (requires auth)
- `POST /api/query` - Execute SQL query (admin only)

## Database Schema

### Users Table
- id, username, email, password_hash, created_at, deleted_at

### Products Table
- id, product_id, product_name, description, price, stock_quantity, category, availability_status, created_date, deleted_at

### Orders Table
- id, order_id, user_id, total_amount, order_status, order_date, deleted_at

### Order Items Table
- id, order_item_id, order_id, product_id, quantity, unit_price

## SQL Query Examples

As an admin user, you can execute SQL queries like:

```sql
-- Get all products
SELECT * FROM products WHERE deleted_at IS NULL;

-- Get user order history (as shown in report)
SELECT 
    o.order_id,
    o.order_date,
    o.total_amount,
    o.order_status,
    oi.order_item_id,
    p.product_id,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    p.stock_quantity
FROM orders o
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE o.user_id = 1 
    AND o.deleted_at IS NULL
ORDER BY o.order_date DESC;
```

## Notes

- This is a simple educational project - not production-ready
- The JWT secret key is hardcoded (change in production)
- CORS is set to allow all origins (restrict in production)
- Products are fetched from dummyjson.com on initialization
- Cart is stored in browser localStorage
- JWT tokens are stored in browser localStorage

## Troubleshooting

- **Backend not starting**: Make sure port 8000 is not in use
- **Products not loading**: Ensure backend server is running and database is initialized
- **CORS errors**: Make sure backend CORS middleware is configured correctly
- **Database errors**: Delete `database.db` and run `init_db.py` again

