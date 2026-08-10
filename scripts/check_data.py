import pandas as pd

df = pd.read_csv("data/bronze/sample_data.csv")

print(df.head())
print()
print("Shape:", df.shape)
print()
print(df.info())