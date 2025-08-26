#Slooze_challenge_data-engineering
## 📂 Project Structure (Final Version)

```
slooze-data-engineering/
│── .venv/                         # Python virtual environment (your local env)
│── data/
│   ├── raw/                       # Unprocessed raw crawl results
│   └── processed/                 # Cleaned & final structured data
│       ├── products.jsonl
│       └── products.csv
│
│── eda/
│   └── eda.py                     # Exploratory Data Analysis script
│
│── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point: runs full crawl + save
│   ├── crawler_indiamart.py       # IndiaMart crawler logic
│   ├── crawler_alibaba.py         # Alibaba crawler logic
│   └── utils.py                   # Common helpers (save/load/clean)
│
│── requirements.txt
│── README.md
```

---

## 🧩 File-by-File Responsibilities

### 1. **`src/crawler_indiamart.py`**

* Crawls IndiaMart categories.
* Uses `requests` + `BeautifulSoup` to parse HTML.
* Extracts product name, price, seller, link.
* Returns a list of dictionaries.

### 2. **`src/crawler_alibaba.py`**

* Same structure as IndiaMart crawler, but adapted for Alibaba.
* Extracts product title, price range, seller, link.
* Handles pagination (more results).

### 3. **`src/utils.py`**

* Helper functions:

  * `save_to_jsonl(data, path)`
  * `save_to_csv(data, path)`
  * `load_jsonl(path)`
  * `clean_text(text)`

### 4. **`src/main.py`**

* The **orchestrator**.
* Calls both crawlers (IndiaMart + Alibaba).
* Merges the product lists.
* Saves them into `data/processed/products.jsonl` and `.csv`.

### 5. **`eda/eda.py`**

* Reads processed data.
* Loads JSONL/CSV into Pandas.
* Prints:

  * Total records
  * Categories available
  * Sample data
  * Null/missing values
* Gives you an overview of dataset quality.

---

## ⚙️ Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

* **Windows (PowerShell):**

  ```bash
  .venv\Scripts\activate
  ```
* **Mac/Linux:**

  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should look like:

```
requests
beautifulsoup4
pandas
```

---

## ▶️ Running the Project

### 1. Run Crawlers (to fetch data)

```bash
python src/main.py
```

**Expected output:**

```
[INFO] Crawling indiamart | category='electronics' up to 120 items
[INFO] Crawling indiamart | category='textiles' up to 120 items
[INFO] Crawling alibaba   | category='electronics' up to 120 items
[INFO] Crawling alibaba   | category='textiles' up to 120 items
[DONE] Saved 240 products.
       JSONL: data\processed\products.jsonl
       CSV  : data\processed\products.csv
```

### 2. Run EDA (to explore data)

```bash
python eda/eda.py
```

**Expected output:**

```
[SUMMARY]
Total records: 240
Categories available: electronics, textiles
Columns: product_name, price, seller, link, source
Missing values:
  price -> 5
  seller -> 2

Sample data:
   product_name              price     seller     source
0  ...
```

---

## 📊 What This Project Does

1. **Scraping Layer**

   * IndiaMart and Alibaba crawlers extract structured product data.
   * Supports multiple categories.
   * Pagination to fetch more than a few results.

2. **Processing Layer**

   * Cleans and structures product data.
   * Saves into:

     * **JSONL** (newline JSON format, good for ML pipelines).
     * **CSV** (easy for Excel/BI tools).

3. **Analysis Layer (EDA)**

   * Quick summary of scraped dataset.
   * Helps validate data quality before deeper analysis.

---

## ✅ Improvements Already in Place

* Works for **multiple sources** (IndiaMart + Alibaba).
* Saves in **two formats** for flexibility.
* EDA for quick data sanity check.
* Scalable: you can add new crawlers (e.g., Amazon, Flipkart) just by adding a new file in `src/`.

---


