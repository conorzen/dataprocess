"""
SQL functionality examples for DataProcessing package.
"""

import pandas as pd
from dataprocessing import load, CSVData, SQLProcessor, sql_query, build_query

# Create sample data
sample_data = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
    'age': [25, 30, 35, 28, 32, 45, 29, 38, 26, 41],
    'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'HR', 'Engineering', 'Marketing', 'Sales', 'HR', 'Engineering'],
    'salary': [50000, 60000, 70000, 55000, 65000, 80000, 52000, 75000, 48000, 85000],
    'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'hire_date': ['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-28', '2020-11-05', '2017-12-01', '2021-06-15', '2019-09-12', '2022-01-20', '2018-04-30']
}

# Create DataFrame and save as CSV
df = pd.DataFrame(sample_data)
df.to_csv('employee_data.csv', index=False)

print("=== DataProcessing SQL Examples ===\n")

# Load data
data = load("employee_data.csv")
print(f"Loaded data shape: {data.shape}")
print("Sample data:")
print(data.head(3))
print()

# Example 1: Basic SQL queries
print("1. Basic SQL Queries:")
print("-" * 40)

# Simple SELECT
result = data.sql("SELECT name, age, department FROM data WHERE age > 30")
print("Employees over 30:")
print(result.head())
print()

# COUNT query
result = data.sql("SELECT COUNT(*) as total_employees FROM data")
print("Total employees:")
print(result)
print()

# GROUP BY with aggregation
result = data.sql("""
    SELECT department, 
           COUNT(*) as employee_count,
           AVG(salary) as avg_salary,
           MAX(salary) as max_salary
    FROM data 
    GROUP BY department
    ORDER BY avg_salary DESC
""")
print("Department statistics:")
print(result)
print()

# Example 2: Advanced SQL queries
print("2. Advanced SQL Queries:")
print("-" * 40)

# Complex filtering and sorting
result = data.sql("""
    SELECT name, age, department, salary, city
    FROM data 
    WHERE age BETWEEN 25 AND 35 
    AND salary > 60000
    ORDER BY salary DESC
    LIMIT 5
""")
print("Young high earners:")
print(result)
print()

# Window functions (if supported)
result = data.sql("""
    SELECT name, department, salary,
           RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
    FROM data
    ORDER BY department, salary DESC
""")
print("Salary ranking by department:")
print(result)
print()

# Example 3: Using SQLProcessor for advanced operations
print("3. Using SQLProcessor:")
print("-" * 40)

with data.sql_processor() as processor:
    # Get table structure
    table_info = processor.get_table_info()
    print("Table structure:")
    print(table_info[['name', 'type']])
    print()
    
    # Get sample data
    sample = processor.get_sample_data(3)
    print("Sample data:")
    print(sample)
    print()
    
    # Execute multiple queries
    result1 = processor.query("SELECT COUNT(*) as total FROM data")
    result2 = processor.query("SELECT DISTINCT department FROM data")
    
    print("Total count:", result1.iloc[0]['total'])
    print("Departments:", list(result2['department']))
    print()

# Example 4: SQL query templates
print("4. SQL Query Templates:")
print("-" * 40)

# Using predefined templates
query = build_query('filter', condition='age > 30 AND salary > 70000')
result = data.sql(query)
print("High-earning employees over 30:")
print(result)
print()

# Custom query with template
query = "SELECT department, city, AVG(salary) as avg_salary, AVG(age) as avg_age FROM data GROUP BY department, city"
result = data.sql(query)
print("Average salary and age by department and city:")
print(result)
print()

# Example 5: Complex data analysis
print("5. Complex Data Analysis:")
print("-" * 40)

# Salary distribution analysis
result = data.sql("""
    SELECT 
        CASE 
            WHEN salary < 50000 THEN 'Low'
            WHEN salary < 70000 THEN 'Medium'
            ELSE 'High'
        END as salary_category,
        COUNT(*) as count,
        AVG(age) as avg_age
    FROM data
    GROUP BY salary_category
    ORDER BY avg_age
""")
print("Salary categories by age:")
print(result)
print()

# Department comparison
result = data.sql("""
    SELECT 
        department,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary,
        MIN(age) as youngest,
        MAX(age) as oldest,
        AVG(age) as avg_age
    FROM data
    GROUP BY department
    HAVING COUNT(*) > 1
    ORDER BY avg_salary DESC
""")
print("Department comparison:")
print(result)
print()

# Example 6: Data transformation with SQL
print("6. Data Transformation:")
print("-" * 40)

# Create calculated columns
result = data.sql("""
    SELECT 
        name,
        age,
        department,
        salary,
        salary * 0.1 as bonus,
        CASE 
            WHEN age < 30 THEN 'Young'
            WHEN age < 40 THEN 'Mid-career'
            ELSE 'Senior'
        END as career_stage
    FROM data
    ORDER BY salary DESC
""")
print("Data with calculated columns:")
print(result.head())
print()

# Example 7: Joining with other data
print("7. Joining Data:")
print("-" * 40)

# Create department info
dept_data = {
    'department': ['Engineering', 'Marketing', 'Sales', 'HR'],
    'budget': [1000000, 500000, 800000, 300000],
    'manager': ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Wilson']
}
dept_df = pd.DataFrame(dept_data)

# Use SQLProcessor to join data
with data.sql_processor() as processor:
    # Add department data to the database
    dept_df.to_sql('departments', processor._connection, if_exists='replace', index=False)
    
    # Join the tables
    result = processor.query("""
        SELECT 
            e.name,
            e.department,
            e.salary,
            d.budget,
            d.manager,
            e.salary / d.budget * 100 as salary_budget_ratio
        FROM data e
        LEFT JOIN departments d ON e.department = d.department
        ORDER BY salary_budget_ratio DESC
    """)
    
    print("Employee data with department info:")
    print(result)
    print()

print("=== SQL Examples Completed! ===")
print("\nKey SQL Features Available:")
print("✅ Basic SELECT, WHERE, ORDER BY, GROUP BY")
print("✅ Aggregation functions (COUNT, AVG, SUM, MIN, MAX)")
print("✅ Window functions (RANK, ROW_NUMBER)")
print("✅ JOIN operations")
print("✅ Subqueries and CTEs")
print("✅ Query templates for common operations")
print("✅ Direct SQL execution on CSV data") 