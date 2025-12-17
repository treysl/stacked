"""
Simple script to execute SQL queries against the database.
Requires admin credentials.
"""
import requests
import json

API_BASE_URL = "http://localhost:8001"

def login_as_admin():
    """Login and get JWT token"""
    response = requests.post(
        f"{API_BASE_URL}/api/login",
        json={"username": "admin", "password": "password"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Logged in as admin")
        return token
    else:
        print(f"✗ Login failed: {response.json()}")
        return None

def execute_sql_query(query, token):
    """Execute a SQL query"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/query",
        headers=headers,
        json={"query": query}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data["results"], data["row_count"]
    else:
        print(f"✗ Query failed: {response.json()}")
        return None, 0

if __name__ == "__main__":
    print("SQL Query Tool")
    print("=" * 50)
    
    # Login
    token = login_as_admin()
    if not token:
        exit(1)
    
    # Query to retrieve all products with name, price, and availability
    query = """
    SELECT 
        product_name AS name,
        price,
        availability_status AS availability,
        stock_quantity,
        category,
        description
    FROM products 
    WHERE deleted_at IS NULL 
    ORDER BY product_name ASC
    """
    
    print("\nExecuting query...")
    print(query)
    print("\n" + "=" * 50)
    
    results, row_count = execute_sql_query(query, token)
    
    if results:
        print(f"\n✓ Query successful! Found {row_count} rows\n")
        
        # Print results in a readable format
        if row_count > 0:
            # Print column headers
            first_row = results[0]
            headers = list(first_row.keys())
            print(" | ".join(f"{h:20}" for h in headers))
            print("-" * (len(headers) * 23))
            
            # Print rows (limit to first 10 for readability)
            for row in results[:10]:
                values = [str(row.get(h, ""))[:20] for h in headers]
                print(" | ".join(f"{v:20}" for v in values))
            
            if row_count > 10:
                print(f"\n... and {row_count - 10} more rows")
        else:
            print("No results found.")
    else:
        print("\n✗ Query execution failed")

