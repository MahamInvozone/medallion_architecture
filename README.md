# Medallion Architecture Data Engineering Pipeline

## Overview

This project demonstrates a simple **Medallion Architecture** data pipeline using **Bronze, Silver, and Gold layers**.

The pipeline takes raw employee data from the Bronze layer, cleans and transforms it in the Silver layer, and then creates business-level aggregated data in the Gold layer.

The project also demonstrates:

* Pandas data manipulation
* Data cleaning and transformation
* Handling missing values
* Filtering and standardization
* GroupBy and aggregation
* Parquet file storage
* DuckDB SQL queries
* Pandas vs DuckDB performance comparison

---

## 1. Medallion Architecture

The Medallion Architecture organizes data into three layers:

```text
                RAW EMPLOYEE DATA
                       │
                       ▼
              ┌─────────────────┐
              │     BRONZE      │
              │   Raw CSV Data  │
              └────────┬────────┘
                       │
                 Cleaning &
                 Transformation
                       │
                       ▼
              ┌─────────────────┐
              │     SILVER      │
              │ Cleaned Parquet │
              │      Data       │
              └────────┬────────┘
                       │
                Aggregation &
                Business Logic
                       │
                       ▼
              ┌─────────────────┐
              │      GOLD       │
              │ Business Summary│
              │     Parquet     │
              └─────────────────┘
```

### Bronze Layer

The Bronze layer contains the original/raw data.

In this project:

```text
data/bronze/sample_data.csv
```

The raw dataset contains:

* 2,011 rows
* 50 columns

The dataset intentionally contains some data-quality issues such as:

* Missing values
* Inconsistent casing
* Extra whitespace
* Duplicate/header records
* Numeric values stored as strings
* Date values stored as strings
* Inconsistent employee rating values

The Bronze layer preserves the raw source data before major transformations.

---

## 2. Bronze → Silver

The Bronze-to-Silver pipeline is implemented in:

```text
scripts/bronze_to_silver.py
```

### Input

```text
data/bronze/sample_data.csv
```

### Output

```text
data/silver/cleaned_data.parquet
```

### Transformations performed

The following transformations were performed while creating the Silver layer.

### 2.1 Remove accidental header records

An accidental header-like record was present inside the dataset.

It was removed using:

```python
df = df[df["employee_id"] != "employee_id"].copy()
```

This reduced the dataset from 2,011 rows to 1,011 rows before duplicate removal.

---

### 2.2 Clean column names

Column names were standardized by:

* Removing whitespace
* Converting names to lowercase
* Replacing spaces with underscores

Example:

```text
Employee ID
```

becomes:

```text
employee_id
```

---

### 2.3 Remove unnecessary whitespace

String columns were stripped using:

```python
df[column] = df[column].str.strip()
```

This removes unwanted spaces before and after text values.

---

### 2.4 Standardize department names

The raw data contained inconsistent department names such as:

```text
HR
hr
Human Resources
```

and different casing such as:

```text
IT
it
```

These values were standardized so that the same department is represented consistently.

For example:

```text
hr → Human Resources
human resources → Human Resources
```

This prevents the same department from being treated as multiple groups during Gold-layer aggregation.

---

### 2.5 Standardize employee ratings

The raw dataset contained different versions of the same rating:

```text
Excellent
EXCELLENT
good
Good
satisfactory
Needs Improvement
```

These values were standardized into:

```text
Excellent
Good
Satisfactory
Needs Improvement
```

---

### 2.6 Convert numeric columns

Several columns were originally stored as strings.

Examples include:

```text
age
salary
annual_bonus
tax_rate
performance_score
attendance_percentage
overtime_hours
project_count
training_hours
employee_rating
```

Numeric columns were converted using:

```python
pd.to_numeric(..., errors="coerce")
```

This allows numerical calculations such as:

* Average
* Sum
* Aggregation
* Sorting

---

### 2.7 Handle missing numeric values

Missing numeric values were converted to `0` for the selected numeric columns.

This ensures that numerical calculations can be performed without errors.

---

### 2.8 Convert date columns

Date-related fields were converted from strings into Pandas datetime values.

Examples:

```text
date_of_birth
hire_date
last_promotion_date
last_updated
```

The conversion was performed using:

```python
pd.to_datetime(..., errors="coerce")
```

---

### 2.9 Handle missing text values

Selected text columns with missing values were filled with:

```text
Unknown
```

This was applied to fields such as:

```text
full_name
manager_name
emergency_contact
emergency_phone
workstation_id
laptop_assigned
remarks
```

---

### 2.10 Remove duplicate records

Duplicate records were removed using:

```python
df.drop_duplicates()
```

The Bronze dataset contained duplicate records, and after cleaning and deduplication the Silver layer contained:

```text
Rows: 1,010
Columns: 50
```

---

## 3. Silver Layer

The cleaned dataset is stored as:

```text
data/silver/cleaned_data.parquet
```

The Silver layer contains cleaned and structured employee data.

The data now contains appropriate data types such as:

```text
salary                float64
annual_bonus          float64
performance_score     float64
age                   float64
hire_date             datetime
last_updated          datetime
```

while categorical/text fields remain string-based.

The Silver layer is intended to be cleaner and more reliable than the raw Bronze data.

---

# 4. Silver → Gold

The Silver-to-Gold pipeline is implemented in:

```text
scripts/silver_to_gold.py
```

### Input

```text
data/silver/cleaned_data.parquet
```

### Output

```text
data/gold/department_summary.parquet
```

The Gold layer contains business-level summaries instead of individual employee records.

---

## 5. Pandas GroupBy and Aggregation

The Gold layer groups employees by:

```text
department
```

The following metrics are calculated:

### Employee count

Number of employees in each department.

```python
employee_count=("employee_id", "count")
```

### Average salary

Average salary for each department.

```python
average_salary=("salary", "mean")
```

### Total salary

Total salary paid across each department.

```python
total_salary=("salary", "sum")
```

### Average bonus

Average annual bonus for each department.

```python
average_bonus=("annual_bonus", "mean")
```

### Average performance

Average performance score for each department.

```python
average_performance=("performance_score", "mean")
```

### Employee rating counts

The Gold layer also counts:

```text
Excellent
Good
Satisfactory
Needs Improvement
```

for each department.

---

## 6. Gold Layer Results

The final Gold dataset contains:

```text
10 departments
10 columns
```

Example results include:

| Department       | Employees | Average Salary |  Total Salary |
| ---------------- | --------: | -------------: | ------------: |
| Operations       |       111 |     $73,657.09 | $8,175,937.37 |
| Customer Support |       107 |     $74,156.16 | $7,934,709.13 |
| Finance          |       106 |     $73,572.16 | $7,798,648.91 |
| Sales            |       101 |     $71,985.78 | $7,270,563.55 |
| Human Resources  |        98 |     $73,363.06 | $7,189,580.12 |
| IT               |        99 |     $72,598.79 | $7,187,280.61 |
| Product          |       100 |     $71,030.15 | $7,103,015.09 |
| Engineering      |        96 |     $73,619.15 | $7,067,438.06 |
| Legal            |        97 |     $70,381.02 | $6,826,959.28 |
| Marketing        |        95 |     $70,229.66 | $6,671,817.26 |

The department with the highest average salary in this dataset was:

```text
Customer Support
Average Salary: $74,156.16
```

---

# 7. Why Parquet Was Used

The processed Silver and Gold data was stored in **Parquet** format.

Files:

```text
data/silver/cleaned_data.parquet
data/gold/department_summary.parquet
```

Parquet is a columnar storage format commonly used in Data Engineering and analytical workloads.

Compared with CSV, Parquet provides advantages such as:

* Columnar storage
* Efficient analytical queries
* Better compression
* Preservation of data types
* Efficient reading of selected columns
* Good integration with analytical engines such as DuckDB

CSV stores data primarily as text, while Parquet stores structured data in a column-oriented binary format.

---

# 8. DuckDB

DuckDB was used to query the Parquet data using SQL.

The DuckDB implementation is located in:

```text
scripts/duckdb_queries.py
```

DuckDB can query a Parquet file directly.

Example:

```sql
SELECT
    department,
    employee_count,
    average_salary,
    total_salary
FROM 'data/gold/department_summary.parquet'
ORDER BY total_salary DESC;
```

This allows analytical SQL queries without first manually loading the complete Parquet file into a Pandas DataFrame.

---

# 9. DuckDB Query Result

DuckDB successfully queried the Gold Parquet file.

The query identified:

```text
Highest average salary department:
Customer Support

Average salary:
$74,156.16
```

The DuckDB query execution time measured during the experiment was:

```text
0.002509 seconds
```

---

# 10. Pandas vs DuckDB

A separate script was created:

```text
scripts/pandas_vs_duckdb.py
```

The same analytical operation was performed using both Pandas and DuckDB.

### Pandas

Pandas loaded the Parquet file into a DataFrame and then performed the required operations.

Measured time:

```text
0.138125 seconds
```

### DuckDB

DuckDB queried the Parquet file directly using SQL.

Measured time:

```text
0.030443 seconds
```

### Comparison

| Tool   |   Execution Time |
| ------ | ---------------: |
| Pandas | 0.138125 seconds |
| DuckDB | 0.030443 seconds |

For this particular test:

```text
DuckDB was faster than Pandas.
```

The dataset is relatively small, so these timings should be considered an observation from this experiment rather than a universal performance benchmark.

---

# 11. Pandas Techniques Used

This project demonstrates several common Pandas data manipulation techniques.

### Reading data

```python
pd.read_csv()
pd.read_parquet()
```

### Filtering

```python
df[df["employee_id"] != "employee_id"]
```

### String cleaning

```python
.str.strip()
.str.lower()
```

### Numeric conversion

```python
pd.to_numeric()
```

### Date conversion

```python
pd.to_datetime()
```

### Missing-value handling

```python
.fillna()
```

### Removing duplicates

```python
.drop_duplicates()
```

### Grouping

```python
df.groupby("department")
```

### Aggregation

```python
.agg()
```

### Sorting

```python
.sort_values()
```

---

# 12. Project Structure

```text
Medallion_Architecture/
│
├── data/
│   ├── bronze/
│   │   └── sample_data.csv
│   │
│   ├── silver/
│   │   └── cleaned_data.parquet
│   │
│   └── gold/
│       └── department_summary.parquet
│
├── scripts/
│   ├── check_data.py
│   ├── bronze_to_silver.py
│   ├── silver_to_gold.py
│   ├── duckdb_queries.py
│   └── pandas_vs_duckdb.py
│
├── .venv/
│
└── README.md
```

---

# 13. How to Run the Project

## Step 1 — Activate virtual environment

```bash
source .venv/bin/activate
```

---

## Step 2 — Install required packages

```bash
pip install pandas pyarrow duckdb
```

---

## Step 3 — Run Bronze → Silver

```bash
python scripts/bronze_to_silver.py
```

This creates:

```text
data/silver/cleaned_data.parquet
```

---

## Step 4 — Run Silver → Gold

```bash
python scripts/silver_to_gold.py
```

This creates:

```text
data/gold/department_summary.parquet
```

---

## Step 5 — Run DuckDB queries

```bash
python scripts/duckdb_queries.py
```

---

## Step 6 — Compare Pandas and DuckDB

```bash
python scripts/pandas_vs_duckdb.py
```

---

# 14. Key Observations

### Bronze Layer

The Bronze layer preserves raw source data. The data may contain missing values, inconsistent formatting, duplicate records, and incorrect data types.

### Silver Layer

The Silver layer improves data quality by cleaning text, standardizing categories, converting data types, handling missing values, removing duplicates, and storing the result in Parquet format.

### Gold Layer

The Gold layer transforms cleaned employee data into business-level information. GroupBy and aggregation were used to produce department-level salary, bonus, performance, and rating metrics.

### Parquet

Parquet was used because it is a columnar format that is well suited to analytical workloads and preserves structured data types more effectively than CSV.

### DuckDB

DuckDB provides a SQL-based analytical interface and can query Parquet files directly.

### Performance

In this experiment:

```text
Pandas  = 0.138125 seconds
DuckDB  = 0.030443 seconds
```

DuckDB was faster for the tested query.

However, the dataset was relatively small, so the performance difference should not be interpreted as a general benchmark for all workloads.

---

# 15. Final Data Flow

The complete pipeline can be summarized as:

```text
                 RAW CSV
                    │
                    ▼
          ┌─────────────────┐
          │     BRONZE      │
          │ sample_data.csv │
          └────────┬────────┘
                   │
                   │ Clean
                   │ Transform
                   │ Deduplicate
                   ▼
          ┌─────────────────────┐
          │       SILVER        │
          │ cleaned_data.parquet│
          └──────────┬──────────┘
                     │
                     │ GroupBy
                     │ Aggregate
                     │ Business Logic
                     ▼
          ┌─────────────────────────┐
          │          GOLD           │
          │ department_summary      │
          │       .parquet          │
          └───────────┬─────────────┘
                      │
                      ▼
                  DuckDB
                      │
                      ▼
                 SQL Analysis
                      │
                      ▼
             Business Insights
```

---

# Conclusion

This project demonstrates a complete small-scale Data Engineering workflow using the **Medallion Architecture**.

The raw employee data was first stored in the Bronze layer, cleaned and standardized in the Silver layer, and then transformed into department-level business summaries in the Gold layer.

Pandas was used for data cleaning and manipulation, Parquet was used for efficient structured storage, and DuckDB was used to query the Parquet data using SQL.

The project also demonstrated a practical performance comparison between Pandas and DuckDB, where DuckDB was faster for the tested analytical query.
