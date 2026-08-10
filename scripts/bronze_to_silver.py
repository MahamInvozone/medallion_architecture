import pandas as pd


# --------------------------------
# File paths
# --------------------------------

input_file = "data/bronze/sample_data.csv"
output_file = "data/silver/cleaned_data.parquet"


# --------------------------------
# 1. Read Bronze data
# --------------------------------

df = pd.read_csv(input_file)

print("Bronze data loaded")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# --------------------------------
# 2. Remove accidental header rows
# --------------------------------

df = df[df["employee_id"] != "employee_id"].copy()


# --------------------------------
# 3. Clean column names
# --------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# --------------------------------
# 4. Remove whitespace from text
# --------------------------------

for column in df.select_dtypes(include="str").columns:
    df[column] = df[column].str.strip()


# --------------------------------
# 5. Standardize department names
# --------------------------------

df["department"] = (
    df["department"]
    .str.lower()
    .replace({
        "it": "IT",
        "hr": "Human Resources",
        "finance": "Finance",
        "engineering": "Engineering",
        "operations": "Operations",
        "sales": "Sales",
        "marketing": "Marketing",
        "product": "Product",
        "legal": "Legal",
        "human resources": "Human Resources",
        "customer support": "Customer Support",
    })
)


# --------------------------------
# 6. Standardize employee ratings
# --------------------------------

df["employee_rating"] = (
    df["employee_rating"]
    .str.lower()
    .replace({
        "excellent": "Excellent",
        "good": "Good",
        "satisfactory": "Satisfactory",
        "needs improvement": "Needs Improvement",
    })
)


# --------------------------------
# 7. Handle missing text values
# --------------------------------

text_columns = [
    "full_name",
    "manager_name",
    "emergency_contact",
    "emergency_phone",
    "workstation_id",
    "laptop_assigned",
    "remarks",
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].fillna("Unknown")


# --------------------------------
# 8. Numeric columns
# --------------------------------

numeric_columns = [
    "age",
    "years_experience",
    "salary",
    "annual_bonus",
    "tax_rate",
    "performance_score",
    "attendance_percentage",
    "overtime_hours",
    "project_count",
    "training_hours",
    "certification_count",
    "vacation_days",
    "sick_days",
    "office_floor",
]


# --------------------------------
# 9. Clean and convert numeric data
# --------------------------------

for column in numeric_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .astype("str")
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# --------------------------------
# 10. Handle missing numeric values
# --------------------------------

for column in numeric_columns:

    if column in df.columns:
        df[column] = df[column].fillna(0)


# --------------------------------
# 11. Convert date columns
# --------------------------------

date_columns = [
    "date_of_birth",
    "hire_date",
    "last_promotion_date",
    "last_updated",
]

for column in date_columns:

    if column in df.columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )


# --------------------------------
# 12. Remove duplicate records
# --------------------------------

before_duplicates = len(df)

df = df.drop_duplicates()

after_duplicates = len(df)

print(
    "Duplicates removed:",
    before_duplicates - after_duplicates
)


# --------------------------------
# 13. Save Silver data as Parquet
# --------------------------------

df.to_parquet(
    output_file,
    index=False
)


# --------------------------------
# 14. Display results
# --------------------------------

print("\nSilver data created successfully!")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nDepartment counts:")
print(df["department"].value_counts())

print("\nEmployee rating counts:")
print(df["employee_rating"].value_counts())

print("\nSample salary values:")
print(df["salary"].head(10).tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())