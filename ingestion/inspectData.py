import pandas as pd

df = pd.read_json("raw_sessions.json")

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())
print("\nDuplicate session IDs:", df["sessionID"].duplicated().sum())

print("\nUnique session IDs:", df["sessionID"].nunique())

duplicates = df[df["sessionID"].duplicated(keep=False)]

print("\nDuplicate session examples:")
print(
    duplicates[
        ["sessionID", "stationID", "connectionTime", "kWhDelivered"]
    ].head(20)
)

session = "2_39_127_19_2018-07-25 01:33:24.468000"

print("\nAll records for this session:")
print(
    df[df["sessionID"] == session][
        [
            "_id",
            "sessionID",
            "stationID",
            "connectionTime",
            "disconnectTime",
            "kWhDelivered",
            "doneChargingTime"
        ]
    ].to_string(index=False)
)

clean_df = df.drop_duplicates(subset="sessionID")

print("\nBefore deduplication:", len(df))
print("After deduplication:", len(clean_df))
print("Duplicates removed:", len(df) - len(clean_df))