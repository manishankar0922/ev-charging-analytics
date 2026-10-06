import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("ACN_API_TOKEN")
BASE_URL = "https://ev.caltech.edu/api/v1/sessions/caltech"
OUTPUT_FILE = "raw_sessions.json"

# Last successful page was 219
START_PAGE = 220
LAST_PAGE = 1257


if not TOKEN:
    raise ValueError(
        "ACN_API_TOKEN is not set. Please add it to your .env file."
    )


# --------------------------------------------------
# LOAD EXISTING DATA
# --------------------------------------------------

if os.path.exists(OUTPUT_FILE):

    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        all_sessions = json.load(file)

    print(
        f"Resuming with {len(all_sessions)} existing sessions"
    )

else:

    all_sessions = []

    print("No existing data found. Starting fresh.")


# --------------------------------------------------
# FETCH PAGES
# --------------------------------------------------

for page in range(START_PAGE, LAST_PAGE + 1):

    url = f"{BASE_URL}?page={page}&pretty"

    while True:

        print(f"\nFetching page {page}...")

        try:

            response = requests.get(
                url,
                auth=(TOKEN, ""),
                timeout=60
            )

            print(
                f"Status for page {page}: "
                f"{response.status_code}"
            )

            # ------------------------------------------
            # SUCCESS
            # ------------------------------------------

            if response.status_code == 200:
                break

            # ------------------------------------------
            # SERVER ERROR
            # ------------------------------------------

            print(
                f"Server returned {response.status_code}."
            )

            print("Retrying in 10 seconds...")

            time.sleep(10)

        # ----------------------------------------------
        # TIMEOUT
        # ----------------------------------------------

        except requests.exceptions.Timeout:

            print(
                f"Timeout on page {page}."
            )

            print(
                "Retrying in 10 seconds..."
            )

            time.sleep(10)

        # ----------------------------------------------
        # OTHER NETWORK ERROR
        # ----------------------------------------------

        except requests.exceptions.RequestException as error:

            print(
                f"Network error on page {page}:"
            )

            print(error)

            print(
                "Retrying in 10 seconds..."
            )

            time.sleep(10)


    # --------------------------------------------------
    # CONVERT RESPONSE TO JSON
    # --------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        print(
            f"Invalid JSON received on page {page}."
        )

        print(
            "Retrying this page in 10 seconds..."
        )

        time.sleep(10)

        continue


    # --------------------------------------------------
    # EXTRACT SESSIONS
    # --------------------------------------------------

    sessions = data.get("_items", [])


    if not sessions:

        print(
            f"No sessions received on page {page}."
        )

        print(
            "Retrying this page in 10 seconds..."
        )

        time.sleep(10)

        continue


    # --------------------------------------------------
    # ADD TO COLLECTION
    # --------------------------------------------------

    all_sessions.extend(sessions)


    # --------------------------------------------------
    # SAVE IMMEDIATELY
    # --------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_sessions,
            file,
            ensure_ascii=False
        )


    print(
        f"Saved {len(all_sessions)} sessions"
    )


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print("\n================================")
print("INGESTION COMPLETE")
print("================================")

print(
    f"Total collected: {len(all_sessions)}"
)

print(
    "Expected total: 31424"
)