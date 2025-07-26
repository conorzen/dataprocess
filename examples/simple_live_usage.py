"""
Simple live data usage examples for DataProcessing package.
Demonstrates the intuitive syntax for importing and querying live data.
"""

from dataprocessing import import_live, create_live_stream, EnhancedLiveData

print("=== Simple Live Data Examples ===\n")

# Example 1: Simple import with @ syntax
print("1. Simple Import with @ Syntax:")
print("-" * 40)

# Import data from URL (with @ prefix)
data = import_live("@https://example.com/live-data.csv")

# Print headers
print("Column headers:")
print(data.header[:10])  # Show first 10 columns
print(f"Total columns: {len(data.header)}")
print()

# Example 2: Create live stream
print("2. Create Live Stream:")
print("-" * 40)

# Create live stream with 60-second refresh interval
teacher_data = create_live_stream(data, interval=60)

print("Live stream created with 60-second refresh interval")
print(f"Data shape: {teacher_data.shape}")
print()

# Example 3: SQL queries
print("3. SQL Queries:")
print("-" * 40)

# Query all records
results = teacher_data.sql("SELECT * FROM data LIMIT 10")
print(f"Records found: {len(results)}")
print("Sample data:")
print(results.head(3))
print()

# Query sample data
verified_teachers = teacher_data.sql("""
    SELECT * FROM data LIMIT 5
""")
print("Sample data:")
print(verified_teachers)
print()

# Example 4: Advanced SQL queries
print("4. Advanced SQL Queries:")
print("-" * 40)

# Data summary
region_stats = teacher_data.sql("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT *) as unique_records
    FROM data
""")
print("Data summary:")
print(region_stats)
print()

# Check data types
availability = teacher_data.sql("""
    SELECT 
        typeof(*) as data_type,
        COUNT(*) as count
    FROM data 
    GROUP BY typeof(*)
""")
print("Data types:")
print(availability)
print()

# Example 5: Using enhanced methods
print("5. Enhanced Methods:")
print("-" * 40)

# Filter data
teachers = teacher_data.filter("1=1")  # Get all records
print(f"Total records: {len(teachers)}")

# Select specific columns
teacher_info = teacher_data.select(['*'])  # Get all columns
print("Data columns:")
print(teacher_info.head(3))
print()

# Group by with aggregation
region_counts = teacher_data.group_by('*', '*', 'COUNT')
print("Data counts:")
print(region_counts.head(5))
print()

# Example 6: Real-time monitoring
print("6. Real-time Monitoring:")
print("-" * 40)

print("Starting real-time monitoring...")
print("Press Ctrl+C to stop")

try:
    # Monitor for changes
previous_count = len(teacher_data.sql("SELECT * FROM data"))
print(f"Initial record count: {previous_count}")

# In a real scenario, you would run this in a loop
# For demonstration, we'll just show the current state
current_count = len(teacher_data.sql("SELECT * FROM data"))
print(f"Current record count: {current_count}")

if current_count != previous_count:
    print(f"🚨 ALERT: Record count changed by {current_count - previous_count}")
else:
    print("✅ No change in record count")
        
except KeyboardInterrupt:
    print("\nMonitoring stopped")

# Example 7: Context manager usage
print("\n7. Context Manager Usage:")
print("-" * 40)

# Use context manager for automatic cleanup
with import_live("@https://example.com/live-data.csv") as live_data:
    # Data is automatically refreshed
teachers = live_data.sql("SELECT COUNT(*) as count FROM data")
print(f"Total records in pool: {teachers.iloc[0]['count']}")
    
    # Get latest data
    latest = live_data.get_data()
    print(f"Latest data shape: {latest.shape}")

print("Context manager automatically cleaned up resources")
print()

# Example 8: Multiple data sources
print("8. Multiple Data Sources:")
print("-" * 40)

# You can work with multiple live data sources
teacher_pool = import_live("@https://example.com/live-data.csv")

# Compare data
roles_comparison = teacher_pool.sql("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT *) as unique_records
    FROM data
""")
print("Data comparison:")
print(roles_comparison)
print()

print("=== Simple Live Data Examples Completed! ===")
print("\nKey Features Demonstrated:")
print("✅ Simple @ syntax for importing data")
print("✅ Easy live stream creation")
print("✅ Intuitive SQL queries")
print("✅ Enhanced filtering and selection methods")
print("✅ Real-time monitoring capabilities")
print("✅ Automatic resource cleanup")
print("✅ Multiple data source support") 