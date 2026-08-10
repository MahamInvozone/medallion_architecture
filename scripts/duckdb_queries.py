import duckdb
import time


# --------------------------------
# File path
# --------------------------------

parquet_file = "data/gold/department_summary.parquet"


# --------------------------------
# Connect to DuckDB
# --------------------------------

con = duckdb.connect()


# --------------------------------
# 1. Read Gold Parquet file
# --------------------------------

print("\n" + "=" * 80)
print("DUCKDB - GOLD DATA")
print("=" * 80)

query = f"""
SELECT *
FROM '{parquet_file}'
"""

gold_data = con.execute(query).fetchdf()

print("\nGold data:")
print(gold_data.to_string(index=False))


# --------------------------------
# 2. Query department salaries
# --------------------------------

print("\n" + "=" * 80)
print("DEPARTMENT SALARY ANALYSIS")
print("=" * 80)

query = f"""
SELECT
    department,
    employee_count,
    average_salary,
    total_salary
FROM '{parquet_file}'
ORDER BY total_salary DESC
"""

result = con.execute(query).fetchdf()

print("\n")
print(result.to_string(index=False))


# --------------------------------
# 3. Find highest average salary
# --------------------------------

query = f"""
SELECT
    department,
    average_salary
FROM '{parquet_file}'
ORDER BY average_salary DESC
LIMIT 1
"""

highest_salary = con.execute(query).fetchdf()

print("\nDepartment with highest average salary:")
print(highest_salary.to_string(index=False))


# --------------------------------
# 4. Measure DuckDB query time
# --------------------------------

start_time = time.perf_counter()

con.execute(f"""
SELECT
    department,
    AVG(average_salary) AS avg_salary
FROM '{parquet_file}'
GROUP BY department
""").fetchall()

duckdb_time = time.perf_counter() - start_time

print(f"\nDuckDB query time: {duckdb_time:.6f} seconds")


# --------------------------------
# Close connection
# --------------------------------

con.close()

print("\nDuckDB analysis completed successfully!")