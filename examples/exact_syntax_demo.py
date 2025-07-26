"""
Exact syntax demonstration for DataProcessing package.
Shows the simple, intuitive syntax requested by the user.
"""

from dataprocessing import import_live, create_live_stream

print("=== Exact Syntax Demo ===\n")

# Your exact requested syntax:
print("1. Import data with @ syntax:")
data = import_live("@https://example.com/live-data.csv")

print("2. Create live stream:")
teacher_data = create_live_stream(data, interval=60)

print("3. Print headers:")
print(teacher_data.header[:10])  # Show first 10 columns

print("\n4. SQL query:")
results = teacher_data.sql("SELECT * FROM data LIMIT 10")
print(f"Found {len(results)} records")
print(results.head(3))

print("\n=== Additional Examples ===")

# More SQL queries
print("\n5. Sample data:")
verified = teacher_data.sql("""
    SELECT * FROM data LIMIT 5
""")
print(verified)

print("\n6. Data summary:")
region_stats = teacher_data.sql("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT *) as unique_records
    FROM data
""")
print(region_stats)

print("\n7. Column types:")
available = teacher_data.sql("""
    SELECT 
        typeof(*) as data_type,
        COUNT(*) as count
    FROM data 
    GROUP BY typeof(*)
""")
print(available)

print("\n=== Syntax Summary ===")
print("✅ data = import_live('@URL')")
print("✅ teacher_data = create_live_stream(data, interval=60)")
print("✅ print(teacher_data.header)")
print("✅ results = teacher_data.sql('SELECT * FROM data WHERE condition')")
print("✅ print(results)")

print("\n🎉 Simple and intuitive live data processing!") 