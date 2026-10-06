import pandas as pd

# Load raw data
df = pd.read_json("raw_sessions.json")

print("Raw rows:", len(df))

# Remove duplicate charging sessions
df = df.drop_duplicates(subset="sessionID")

print("After deduplication:", len(df))

# Save cleaned dataset
df.to_csv("clean_sessions.csv", index=False)

print("Clean dataset saved successfully.")