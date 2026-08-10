import pandas as pd
import duckdb
import time


# --------------------------------
# File path
# --------------------------------

parquet_file = "data/gold/department_summary.parquet"


# ================================================
# PANDAS
# ================================================

start_time = time.perf_counter()

df = pd.read_parquet(parquet_file)

pandas_result = (
    df[
        [
            "department",
            "employee_count",
            "average_salary",
            "total_salary",
        ]
    ]
    .sort_values(
        "total_salary",
        ascending=False
    )
)

pandas_time = time.perf_counter() - start_time


print("\n" + "=" * 80)
print("PANDAS RESULT")
print("=" * 80)

print(pandas_result.to_string(index=False))

print(f"\nPandas time: {pandas_time:.6f} seconds")


# ================================================
# DUCKDB
# ================================================

con = duckdb.connect()

start_time = time.perf_counter()

duckdb_result = con.execute(
    f"""
    SELECT
        department,
        employee_count,
        average_salary,
        total_salary
    FROM '{parquet_file}'
    ORDER BY total_salary DESC
    """
).fetchdf()

duckdb_time = time.perf_counter() - start_time


print("\n" + "=" * 80)
print("DUCKDB RESULT")
print("=" * 80)

print(duckdb_result.to_string(index=False))

print(f"\nDuckDB time: {duckdb_time:.6f} seconds")


# ================================================
# COMPARISON
# ================================================

print("\n" + "=" * 80)
print("PERFORMANCE COMPARISON")
print("=" * 80)

print(f"\nPandas time : {pandas_time:.6f} seconds")
print(f"DuckDB time : {duckdb_time:.6f} seconds")

if pandas_time < duckdb_time:
    print("\nPandas was faster for this query.")

elif duckdb_time < pandas_time:
    print("\nDuckDB was faster for this query.")

else:
    print("\nBoth had approximately the same execution time.")


# ================================================
# Close DuckDB
# ================================================

con.close()