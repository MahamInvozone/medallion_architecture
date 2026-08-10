import pandas as pd


# --------------------------------
# File paths
# --------------------------------

input_file = "data/silver/cleaned_data.parquet"
output_file = "data/gold/department_summary.parquet"


# --------------------------------
# 1. Read Silver data
# --------------------------------

df = pd.read_parquet(input_file)

print("Silver data loaded")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# --------------------------------
# 2. Group by department
# --------------------------------

department_summary = (
    df.groupby("department")
    .agg(
        employee_count=("employee_id", "count"),

        average_salary=("salary", "mean"),

        total_salary=("salary", "sum"),

        average_bonus=("annual_bonus", "mean"),

        average_performance=("performance_score", "mean"),

        excellent_count=(
            "employee_rating",
            lambda x: (x == "Excellent").sum()
        ),

        good_count=(
            "employee_rating",
            lambda x: (x == "Good").sum()
        ),

        satisfactory_count=(
            "employee_rating",
            lambda x: (x == "Satisfactory").sum()
        ),

        needs_improvement_count=(
            "employee_rating",
            lambda x: (x == "Needs Improvement").sum()
        ),
    )
    .reset_index()
)


# --------------------------------
# 3. Round numerical values
# --------------------------------

department_summary["average_salary"] = (
    department_summary["average_salary"].round(2)
)

department_summary["total_salary"] = (
    department_summary["total_salary"].round(2)
)

department_summary["average_bonus"] = (
    department_summary["average_bonus"].round(2)
)

department_summary["average_performance"] = (
    department_summary["average_performance"].round(2)
)


# --------------------------------
# 4. Sort by total salary
# --------------------------------

department_summary = department_summary.sort_values(
    "total_salary",
    ascending=False
)


# --------------------------------
# 5. Save Gold data as Parquet
# --------------------------------

department_summary.to_parquet(
    output_file,
    index=False
)


# --------------------------------
# 6. Display results
# --------------------------------
print("\n" + "=" * 100)
print("GOLD LAYER - DEPARTMENT SUMMARY")
print("=" * 100)

print("\nEach row represents one department.\n")

for _, row in department_summary.iterrows():

    print("-" * 100)

    print(f"Department              : {row['department']}")
    print(f"Employee Count           : {row['employee_count']}")
    print(f"Average Salary           : ${row['average_salary']:,.2f}")
    print(f"Total Salary             : ${row['total_salary']:,.2f}")
    print(f"Average Bonus            : ${row['average_bonus']:,.2f}")
    print(f"Average Performance      : {row['average_performance']:.2f}")
    print(f"Excellent Rating         : {row['excellent_count']}")
    print(f"Good Rating              : {row['good_count']}")
    print(f"Satisfactory Rating      : {row['satisfactory_count']}")
    print(f"Needs Improvement       : {row['needs_improvement_count']}")

print("-" * 100)

print("\nTotal Departments:", len(department_summary))
print("Total Columns:", len(department_summary.columns))

print("\nGold Parquet file saved to:")
print(output_file)