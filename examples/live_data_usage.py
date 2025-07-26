"""
Live data functionality examples for DataProcessing package.
"""

import pandas as pd
import sqlite3
import tempfile
import os
import time
import random
from dataprocessing import (
    load_from_db, load_from_api, create_live_stream, 
    LiveDataManager, CSVData
)

print("=== DataProcessing Live Data Examples ===\n")

# Example 1: Database Connections
print("1. Database Connections:")
print("-" * 40)

# Create a temporary SQLite database for demonstration
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

try:
    # Create sample database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            department TEXT,
            salary REAL
        )
    """)
    
    # Insert sample data
    sample_employees = [
        (1, 'Alice Johnson', 28, 'Engineering', 75000),
        (2, 'Bob Smith', 32, 'Marketing', 65000),
        (3, 'Charlie Brown', 35, 'Engineering', 85000),
        (4, 'Diana Prince', 29, 'Sales', 70000),
        (5, 'Eve Wilson', 31, 'HR', 60000)
    ]
    
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", sample_employees)
    conn.commit()
    conn.close()
    
    # Load data from database
    data = load_from_db('sqlite', db_path, "SELECT * FROM employees")
    print("Data loaded from SQLite database:")
    print(data.head())
    print(f"Shape: {data.shape}")
    print()
    
    # Use SQL on database data
    result = data.sql("SELECT department, AVG(salary) as avg_salary FROM data GROUP BY department")
    print("Department average salaries:")
    print(result)
    print()

except Exception as e:
    print(f"Database example error: {e}")
    print()

finally:
    # Clean up
    if os.path.exists(db_path):
        os.unlink(db_path)

# Example 2: API Connections
print("2. API Connections:")
print("-" * 40)

# Mock API data for demonstration
def mock_api_response():
    """Simulate API response."""
    return {
        'data': [
            {'id': 1, 'name': 'Product A', 'price': 29.99, 'category': 'Electronics'},
            {'id': 2, 'name': 'Product B', 'price': 49.99, 'category': 'Books'},
            {'id': 3, 'name': 'Product C', 'price': 19.99, 'category': 'Electronics'},
            {'id': 4, 'name': 'Product D', 'price': 39.99, 'category': 'Clothing'},
            {'id': 5, 'name': 'Product E', 'price': 79.99, 'category': 'Electronics'}
        ]
    }

# Simulate API call (in real usage, this would be a real API)
try:
    # For demonstration, we'll create a DataFrame directly
    # In real usage: data = load_from_api('https://api.example.com', '/products')
    api_data = mock_api_response()
    df = pd.DataFrame(api_data['data'])
    data = CSVData(df)
    
    print("Data loaded from API:")
    print(data.head())
    print(f"Shape: {data.shape}")
    print()
    
    # Process API data
    result = data.sql("SELECT category, COUNT(*) as count, AVG(price) as avg_price FROM data GROUP BY category")
    print("Product categories summary:")
    print(result)
    print()

except Exception as e:
    print(f"API example error: {e}")
    print()

# Example 3: Real-time Data Streams
print("3. Real-time Data Streams:")
print("-" * 40)

def generate_sensor_data():
    """Generate mock sensor data."""
    return {
        'temperature': round(random.uniform(20, 30), 2),
        'humidity': round(random.uniform(40, 80), 2),
        'pressure': round(random.uniform(1000, 1020), 2)
    }

def generate_stock_data():
    """Generate mock stock price data."""
    return {
        'symbol': 'AAPL',
        'price': round(random.uniform(150, 200), 2),
        'volume': random.randint(1000, 10000)
    }

try:
    # Create real-time data streams
    sensor_stream = create_live_stream(generate_sensor_data, interval=0.5, max_records=10)
    stock_stream = create_live_stream(generate_stock_data, interval=1.0, max_records=5)
    
    print("Starting data streams...")
    sensor_stream.start()
    stock_stream.start()
    
    # Collect data for a few seconds
    time.sleep(3)
    
    # Get collected data
    sensor_data = CSVData(sensor_stream.get_latest_data())
    stock_data = CSVData(stock_stream.get_latest_data())
    
    print("Sensor data collected:")
    print(sensor_data.head())
    print()
    
    print("Stock data collected:")
    print(stock_data.head())
    print()
    
    # Stop streams
    sensor_stream.stop()
    stock_stream.stop()
    
    print("Data streams stopped.")
    print()

except Exception as e:
    print(f"Stream example error: {e}")
    print()

# Example 4: Live Data Manager
print("4. Live Data Manager:")
print("-" * 40)

try:
    # Create a manager to handle multiple connections
    manager = LiveDataManager()
    
    # Create another temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path2 = f.name
    
    # Set up database
    conn = sqlite3.connect(db_path2)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product TEXT,
            amount REAL,
            date TEXT
        )
    """)
    
    sample_sales = [
        (1, 'Laptop', 1200.00, '2024-01-15'),
        (2, 'Mouse', 25.00, '2024-01-15'),
        (3, 'Keyboard', 75.00, '2024-01-16'),
        (4, 'Monitor', 300.00, '2024-01-16'),
        (5, 'Laptop', 1100.00, '2024-01-17')
    ]
    
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)", sample_sales)
    conn.commit()
    conn.close()
    
    # Connect to database through manager
    db_conn = manager.connect_database('sales_db', 'sqlite', db_path2)
    
    # Query data
    with db_conn:
        sales_data = CSVData(db_conn.query("SELECT * FROM sales"))
        print("Sales data from managed connection:")
        print(sales_data.head())
        print()
        
        # Analyze sales
        result = sales_data.sql("""
            SELECT 
                date,
                COUNT(*) as transactions,
                SUM(amount) as total_sales,
                AVG(amount) as avg_sale
            FROM data 
            GROUP BY date
            ORDER BY date
        """)
        print("Daily sales summary:")
        print(result)
        print()
    
    # Create a stream through manager
    def generate_web_traffic():
        return {
            'page': random.choice(['home', 'products', 'about', 'contact']),
            'visitors': random.randint(10, 100),
            'bounce_rate': round(random.uniform(0.1, 0.8), 3)
        }
    
    traffic_stream = manager.create_stream('web_traffic', generate_web_traffic, interval=0.3, max_records=8)
    traffic_stream.start()
    
    # Collect some data
    time.sleep(2)
    
    traffic_data = CSVData(traffic_stream.get_latest_data())
    print("Web traffic data:")
    print(traffic_data.head())
    print()
    
    # Clean up
    traffic_stream.stop()
    manager.close_all()
    
    if os.path.exists(db_path2):
        os.unlink(db_path2)

except Exception as e:
    print(f"Manager example error: {e}")
    print()

# Example 5: Combining Live Data with CSV Processing
print("5. Combining Live Data with CSV Processing:")
print("-" * 40)

try:
    # Create sample CSV data
    csv_data = {
        'product_id': [1, 2, 3, 4, 5],
        'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories'],
        'base_price': [1200, 25, 75, 300, 150]
    }
    
    df = pd.DataFrame(csv_data)
    df.to_csv('products.csv', index=False)
    
    # Load CSV data
    products = CSVData(df)
    print("CSV Products data:")
    print(products.head())
    print()
    
    # Simulate live sales data
    def get_live_sales():
        return {
            'product_id': random.randint(1, 5),
            'quantity': random.randint(1, 10),
            'discount': round(random.uniform(0, 0.2), 2)
        }
    
    sales_stream = create_live_stream(get_live_sales, interval=0.5, max_records=6)
    sales_stream.start()
    
    # Collect live sales data
    time.sleep(2)
    live_sales = CSVData(sales_stream.get_latest_data())
    sales_stream.stop()
    
    print("Live sales data:")
    print(live_sales.head())
    print()
    
    # Combine CSV and live data using SQL
    with products.sql_processor() as processor:
        # Add live sales data to the database
        live_sales.df.to_sql('sales', processor._connection, if_exists='replace', index=False)
        
        # Join products with sales
        combined = processor.query("""
            SELECT 
                p.product_name,
                p.category,
                p.base_price,
                s.quantity,
                s.discount,
                p.base_price * s.quantity * (1 - s.discount) as total_revenue
            FROM data p
            LEFT JOIN sales s ON p.product_id = s.product_id
            ORDER BY total_revenue DESC
        """)
        
        print("Combined products and sales data:")
        print(combined)
        print()
    
    # Clean up
    if os.path.exists('products.csv'):
        os.unlink('products.csv')

except Exception as e:
    print(f"Combination example error: {e}")
    print()

print("=== Live Data Examples Completed! ===")
print("\nKey Live Data Features Available:")
print("✅ Database connections (SQLite, PostgreSQL, MySQL)")
print("✅ API connections with authentication")
print("✅ Real-time data streams")
print("✅ Live data management")
print("✅ Integration with CSV processing")
print("✅ SQL queries on live data")
print("✅ Automatic resource cleanup") 