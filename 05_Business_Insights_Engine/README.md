# Experiment 05 — Business Insights Engine

## Aim

To analyze real online retail transactions in PostgreSQL using JOIN, GROUP BY, HAVING, and aggregate functions, and to display the results through a small Flask interface.

## Software used

- PostgreSQL 16
- pgAdmin 4 or the `psql` command-line tool
- Python 3 with Flask, Pandas, OpenPyXL, and Psycopg

## Dataset

The experiment uses the **Online Retail** dataset from the UCI Machine Learning Repository.

- Source: https://archive.ics.uci.edu/dataset/352/online+retail
- DOI: https://doi.org/10.24432/C5BW33
- License: CC BY 4.0
- File: `data/Online Retail.xlsx`
- Period: 1 December 2010 to 9 December 2011
- Original rows: 541,909
- Imported staging rows: 541,909
- Imported order-item rows: 541,909
- Excluded rows: 0

The dataset contains transaction line items. An invoice can therefore appear on many rows.

## Database schema

- `raw_retail`: preserves every original line with a generated `raw_id`, load status, and optional exclusion reason.
- `customers`: one row per known customer and a deterministic representative country.
- `products`: one row per stock code and a deterministic representative description.
- `invoices`: one row per invoice with customer, date, country, and cancellation status.
- `order_items`: one row per source line, linked to its invoice and product.

Primary keys uniquely identify records. Foreign keys connect order items to invoices and products, and invoices to known customers. `invoice_no` and `stock_code` remain text because the source includes letters and unusual codes. Money uses `NUMERIC(14,4)`.

## Data-cleaning rules

- Every source row is retained in `raw_retail` and `order_items`.
- The source contains 5,268 repeated rows beyond their first occurrence. They are preserved as separate line records with different generated IDs.
- Missing customer IDs remain `NULL`; 135,080 rows have no customer ID.
- Missing descriptions remain traceable; 1,454 rows have no description.
- Cancellation invoices are identified when `invoice_no` begins with `C`; 9,288 rows are cancellations.
- Negative quantities and non-positive prices are preserved. They are excluded only from completed-sales calculations.
- Forty-three invoice numbers have more than one timestamp. The earliest timestamp is used for the invoice header while every original timestamp remains in staging.
- Eight customers occur with more than one country. The most frequent country is selected, with alphabetical order used to break ties.
- Six hundred and fifty stock codes have description variants. The most frequent non-empty description is selected, with alphabetical order used to break ties.
- Invoice country is stored on `invoices`, so country analysis still includes invoices with missing customer IDs.

## SQL concepts demonstrated

`JOIN` combines related invoices, products, customers, and order items. `GROUP BY` creates summaries for months, countries, products, and customers. `HAVING` filters grouped results after aggregation. `SUM`, `AVG`, and `COUNT(DISTINCT ...)` calculate revenue, average order value, and order counts without counting an invoice once per line item.

The ten predefined analyses are:

1. Total completed sales revenue
2. Monthly sales revenue
3. Top 10 products by revenue
4. Revenue by country
5. Orders per customer
6. Average order value
7. Products sold using JOIN
8. Countries exceeding £100,000 revenue using HAVING
9. Customers exceeding £10,000 spending using HAVING
10. Monthly order counts using GROUP BY

Completed revenue excludes cancellation invoices, non-positive quantities, and non-positive prices. Revenue is `quantity × unit_price` and is reported in GBP. Order counts use distinct invoice numbers.

## Setup

Create the database and install the Python packages:

```bash
createdb retail_db
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
psql -d retail_db -f 01_database.sql
```

Set PostgreSQL credentials and import the official Excel file:

```bash
export PGHOST=127.0.0.1
export PGPORT=5432
export PGDATABASE=retail_db
export PGUSER=your_postgresql_user
export PGPASSWORD=your_postgresql_password
python import_data.py
```

Run all analysis queries with:

```bash
psql -d retail_db -f 02_analysis_queries.sql
```

Launch the interface:

```bash
python app.py
```

Open http://127.0.0.1:5005 in a browser. The interface accepts only the ten predefined read-only queries.

## Actual observations

- Completed sales revenue is **£10,666,684.54**.
- November 2011 has the highest monthly revenue at **£1,509,496.33**.
- The United Kingdom contributes **£9,025,222.08** from 18,019 completed orders.
- Six countries exceed £100,000 in completed revenue.
- Average completed order value is **£534.40**.
- `DOTCOM POSTAGE` is the highest-revenue product code in this calculation at **£206,248.77**.

## Screenshots

- `screenshots/01_total_sales.png`
- `screenshots/02_monthly_revenue.png`
- `screenshots/03_top_products.png`
- `screenshots/04_country_analysis.png`
- `screenshots/05_having_query.png`

## Conclusion

This experiment converts a real line-item dataset into a relational PostgreSQL database without silently losing source records. The queries demonstrate how joins and grouped calculations produce useful business insights while handling cancellations, missing values, and repeated invoice lines correctly.
