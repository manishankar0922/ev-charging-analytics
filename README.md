# ⚡ EV Charging Analytics Pipeline

An end-to-end data engineering and analytics pipeline for Electric Vehicle (EV) charging session data collected from the **Caltech Adaptive Charging Network (ACN-Data) API**. 

This repository provides automated data ingestion with fault-tolerant retries, duplicate analysis, cleaning and deduplication, and data quality validation.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Repository Structure](#-repository-structure)
- [Dataset Summary](#-dataset-summary)
- [Data Dictionary](#-data-dictionary)
- [Prerequisites & Requirements](#-prerequisites--requirements)
- [Quick Start Guide](#-quick-start-guide)
  - [1. Clone and Set Up Environment](#1-clone-and-set-up-environment)
  - [2. Configure API Token](#2-configure-api-token)
- [Step-by-Step Pipeline Execution](#-step-by-step-pipeline-execution)
  - [Step 1: Data Ingestion (`fetch_data.py`)](#step-1-data-ingestion-fetch_datapy)
  - [Step 2: Data Quality Inspection (`inspectData.py`)](#step-2-data-quality-inspection-inspectdatapy)
  - [Step 3: Cleaning & Deduplication (`CleanDataSet.py`)](#step-3-cleaning--deduplication-cleandatasetpy)
  - [Step 4: Quality Verification (`checkClean.py`)](#step-4-quality-verification-checkcleanpy)
- [Analytical Insights & Use Cases](#-analytical-insights--use-cases)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 📖 Overview

The **Adaptive Charging Network (ACN)** at the California Institute of Technology (Caltech) is a live testbed designed for smart EV charging research. 

This project solves common challenges when working with real-world EV charging APIs:
- **Resilient Ingestion**: Handles network timeouts, HTTP 5xx errors, rate limits, and paged API responses with automatic retries and checkpointing.
- **Data Deduplication**: API pagination and session updates frequently produce overlapping records. The pipeline detects and strips duplicates based on unique session keys.
- **Ready-for-Analysis Export**: Standardizes JSON payloads into a clean tabular CSV format suitable for machine learning, demand forecasting, and operational dashboards.

---

## 🏗️ Architecture & Data Flow

```text
       ┌────────────────────────┐
       │ Caltech ACN-Data API   │
       │ (REST / JSON Endpoints)│
       └───────────┬────────────┘
                   │
                   ▼ [fetch_data.py] (Token auth, pagination, retries)
       ┌────────────────────────┐
       │   raw_sessions.json    │  (13,425 raw session records)
       └───────────┬────────────┘
                   │
                   ▼ [inspectData.py] (Duplicate audit, nulls, profiling)
                   │
                   ▼ [CleanDataSet.py] (Deduplication by sessionID)
       ┌────────────────────────┐
       │   clean_sessions.csv   │  (10,025 clean, unique records)
       └───────────┬────────────┘
                   │
                   ▼ [checkClean.py] (Integrity check, schema verification)
       ┌────────────────────────┐
       │ Downstream Analytics & │
       │ Machine Learning Models│
       └────────────────────────┘
```

---

## 📂 Repository Structure

```text
ev-charging-analytics/
├── .env.example             # Template for API credentials
├── .gitignore               # Excludes secrets (.env) and caches
├── requirements.txt         # Python package dependencies
├── README.md                # Comprehensive documentation
└── ingestion/
    ├── fetch_data.py        # Automated API data extractor with retry logic
    ├── inspectData.py       # Data exploration & duplicate diagnostics
    ├── CleanDataSet.py      # Cleans raw JSON and writes clean CSV
    ├── checkClean.py        # Validates schema and integrity of clean CSV
    ├── raw_sessions.json    # Ingested raw API responses (JSON)
    └── clean_sessions.csv   # Cleaned, deduplicated tabular dataset (CSV)
```

### Module Breakdown

| Script / File | Purpose | Key Inputs / Outputs |
| :--- | :--- | :--- |
| **`fetch_data.py`** | Fetches paginated sessions from Caltech API, persists intermediate progress to disk, retries failed requests. | **In:** `.env` (`ACN_API_TOKEN`)<br>**Out:** `raw_sessions.json` |
| **`inspectData.py`** | Audits raw data shape, columns, missing fields, and prints sample duplicates for inspection. | **In:** `raw_sessions.json`<br>**Out:** Terminal audit report |
| **`CleanDataSet.py`** | Deduplicates entries based on `sessionID` and saves the cleaned dataset. | **In:** `raw_sessions.json`<br>**Out:** `clean_sessions.csv` |
| **`checkClean.py`** | Quick sanity check verifying row count, column datatypes, and missing values in the final CSV. | **In:** `clean_sessions.csv`<br>**Out:** Validation summary |

---

## 📊 Dataset Summary

The current pipeline run captures and processes real EV charging sessions from the Caltech site:

| Metric | Value |
| :--- | :--- |
| **Raw Records Ingested** | `13,425` |
| **Duplicate Records Detected** | `3,400` |
| **Clean Unique Sessions** | `10,025` |
| **Active Charging Stations** | `54` stations |
| **Total Energy Delivered** | `89,136.87 kWh` |
| **Average Energy Delivered** | `8.89 kWh / session` |
| **Primary Timezone** | `America/Los_Angeles` |

---

## 🗂️ Data Dictionary

The cleaned output file (`clean_sessions.csv`) contains 13 columns:

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `_id` | `string` | Internal MongoDB ObjectId from the source database. | `5bc90cb9f9af8b0d7fe77cd2` |
| `sessionID` | `string` | Unique identifier for each charging session. Used as primary key for deduplication. | `2_39_78_362_2018-04-25 11:08:04.400812` |
| `stationID` | `string` | Unique identifier for the EVSE / charging station unit. | `2-39-78-362` |
| `spaceID` | `string` | Identifier for the physical parking stall or bay. | `CA-496` |
| `siteID` | `integer` | Identifier for the site location (`2` represents Caltech). | `2` |
| `clusterID` | `integer` | Identifier for the local transformer or electrical cluster. | `39` |
| `connectionTime` | `string (datetime)` | Timestamp when the vehicle was physically plugged into the station. | `Wed, 25 Apr 2018 11:08:04 GMT` |
| `disconnectTime` | `string (datetime)` | Timestamp when the vehicle was unplugged and departed. | `Wed, 25 Apr 2018 13:20:10 GMT` |
| `doneChargingTime` | `string (datetime)` | Timestamp when the vehicle battery reached full charge / stopped drawing power. | `Wed, 25 Apr 2018 13:21:10 GMT` |
| `kWhDelivered` | `float` | Total electrical energy delivered during the session (in kilowatt-hours). | `7.932` |
| `timezone` | `string` | Geographical timezone of the charging site. | `America/Los_Angeles` |
| `userID` | `string` | Anonymized user account identifier (can be empty/null). | `null` |
| `userInputs` | `string (JSON)` | Optional parameters provided by the driver (requested energy, expected departure time). | `null` |

---

## ⚙️ Prerequisites & Requirements

- **Python**: Version `3.8` or higher
- **Free API Access**: Caltech ACN Data API account & token (registration is free at [ev.caltech.edu](https://ev.caltech.edu))
- **Libraries**:
  - `requests` (HTTP client for API extraction)
  - `python-dotenv` (Secure environment variable loading)
  - `pandas` (Data processing, deduplication, CSV export)

---

## 🚀 Quick Start Guide

### 1. Clone and Set Up Environment

Open your terminal and run:

```bash
# Clone the repository
git clone https://github.com/manishankar0922/ev-charging-analytics.git
cd ev-charging-analytics

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux / macOS:
source venv/bin/activate
# On Windows (cmd/powershell):
# venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Configure API Token

1. Sign up or log in at [https://ev.caltech.edu](https://ev.caltech.edu) to obtain your personal API token.
2. Copy `.env.example` to create your private `.env` file:

```bash
cp .env.example .env
```

3. Open `.env` in any editor and replace the placeholder with your actual token:

```env
ACN_API_TOKEN=your_actual_token_here
```

*(Note: `.env` is listed in `.gitignore` and will never be committed to git.)*

---

## 🔄 Step-by-Step Pipeline Execution

All operational scripts are located inside the `ingestion/` directory.

> 💡 **Path Notice**: Navigate into the `ingestion` folder before executing scripts so input and output files are read and written to the expected locations:
> ```bash
> cd ingestion
> ```

---

### Step 1: Data Ingestion (`fetch_data.py`)

Harvests session records page-by-page from the Caltech ACN API endpoint:

```bash
python fetch_data.py
```

**Features & Capabilities**:
- **Automatic Checkpointing**: If `raw_sessions.json` already exists, the script reads existing records and appends new pages without re-downloading from scratch.
- **Configurable Page Ranges**:
  - `START_PAGE = 220`
  - `LAST_PAGE = 1257`
- **Fault-Tolerant Retries**: Automatically handles HTTP 500/502/503 errors, request timeouts, and connection dropouts by waiting 10 seconds before retrying the same page.
- **Immediate Disk Sync**: Dumps updated JSON to `raw_sessions.json` after every single page to avoid losing data if interrupted.

---

### Step 2: Data Quality Inspection (`inspectData.py`)

Inspects the downloaded raw data to understand dataset shape, missing fields, and duplicate occurrences:

```bash
python inspectData.py
```

**Output Includes**:
- Total rows and column list.
- Missing values count per column (`userID`, `userInputs`).
- Duplicate session count by `sessionID`.
- Detailed inspection of duplicate session rows (revealing identical start/end times and energy delivered).

---

### Step 3: Cleaning & Deduplication (`CleanDataSet.py`)

Performs deduplication and exports clean data into CSV:

```bash
python CleanDataSet.py
```

**Operations Performed**:
1. Reads `raw_sessions.json`.
2. Applies pandas `drop_duplicates(subset="sessionID")`.
3. Exports the clean dataframe to `clean_sessions.csv`.

---

### Step 4: Quality Verification (`checkClean.py`)

Performs validation on the newly generated CSV file:

```bash
python checkClean.py
```

**Verification Checklist**:
- Confirms shape: `(10025, 13)`
- Checks column data types (`float64` for `kWhDelivered`, `int64` for `siteID`/`clusterID`, `object` for timestamps)
- Displays preview of the first 5 records

---

## 📈 Analytical Insights & Use Cases

Once the clean CSV (`clean_sessions.csv`) is generated, you can use it for multiple data science and business analytics projects:

1. **Idle Time Analysis (Dwell vs Charging Time)**:
   - Compare `disconnectTime - connectionTime` (Total Stay) against `doneChargingTime - connectionTime` (Active Charging).
   - Identifies how long fully charged vehicles remain plugged in, blocking stations for other drivers.

2. **Peak Demand & Load Forecasting**:
   - Extract the hour of the day from `connectionTime` to discover arrival peaks (typically 8:00 AM - 10:00 AM in campus/workplace environments).
   - Predict grid load and schedule adaptive charging rates.

3. **Station Utilization & Availability**:
   - Calculate occupancy rates per `stationID` and `spaceID` to detect high-demand charging hubs vs underutilized chargers.

4. **Energy Consumption Analytics**:
   - Distribution of `kWhDelivered` across days of the week, weekends vs weekdays, and seasonal trends.

---

## ❓ Troubleshooting & FAQs

### Q1: `ValueError: ACN_API_TOKEN is not set. Please add it to your .env file.`
- **Cause**: The `.env` file does not exist or does not contain `ACN_API_TOKEN`.
- **Solution**: Ensure you have created `.env` with `ACN_API_TOKEN=your_token` in the root or `ingestion/` directory, or export it in your shell: `export ACN_API_TOKEN="your_token"`.

### Q2: `FileNotFoundError: [Errno 2] No such file or directory: 'raw_sessions.json'`
- **Cause**: Running `CleanDataSet.py` or `inspectData.py` from the root directory instead of inside `ingestion/`.
- **Solution**: Make sure you `cd ingestion` before executing the script, or provide the relative path `ingestion/raw_sessions.json`.

### Q3: `ModuleNotFoundError: No module named 'pandas'` (or `requests` / `dotenv`)
- **Cause**: Packages are not installed in the active environment.
- **Solution**: Activate your virtual environment and run `pip install -r requirements.txt`.

### Q4: The API request times out or returns 500 error
- **Cause**: Temporary Caltech API server slowdown or rate limit.
- **Solution**: `fetch_data.py` has built-in retry logic. It will automatically wait 10 seconds and attempt the request again.

---

## 📜 License & Acknowledgments

- **Data Source**: Caltech Adaptive Charging Network ([ACN-Data](https://ev.caltech.edu/dataset)).
- **Citation**: Z. Lee, D. Johansson, S. H. Low, "ACN-Data: Analysis and Applications of an Open EV Charging Dataset", *ACM e-Energy*, 2019.
- **License**: MIT License. Free for academic, educational, and commercial analytics.
