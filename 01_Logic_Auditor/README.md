# Experiment 01 — The Logic Auditor

## Aim

To compare a file-based CSV/Pandas workflow with a relational SQLite database for six common retrieval tasks, while separating end-to-end cost from warm-query cost.

## Learning objectives

- Create identical structured data in CSV and SQLite.
- Express equivalent selection, filtering, sorting, aggregation, and counting operations.
- Validate results before comparing timings.
- Use repeated measurements and descriptive statistics responsibly.
- Explain how file parsing, connections, caching, and indexes affect a microbenchmark.

## Software requirements

- Python 3.10 or later
- Pandas 2.0 or later
- Matplotlib 3.7 or later
- SQLite through Python's standard-library `sqlite3` module

The recorded run used Python 3.14.7, Pandas 3.0.6, SQLite 3.53.4, and macOS 27.0 on ARM64. Exact timings will vary by computer and run.

## Introduction

CSV is a portable, human-readable text format. It has no intrinsic schema, indexes, constraints, or query engine, so Pandas must parse the file before operating on its rows. It is convenient for exchange and small analytical datasets.

SQLite is an embedded relational database. It stores typed table rows, supports constraints and indexes, and evaluates SQL without a separate database server. Its query planner can avoid scanning an entire table when an appropriate index is available.

## Dataset schema

The fixed seed `202601` generates 10,000 fictional Indian university-style records. No external data is downloaded.

| Field | Representation | Rule |
|---|---|---|
| `student_id` | text | Unique `STU00001`–`STU10000`; primary key in SQLite |
| `full_name` | text | Deterministically sampled first and last names |
| `department` | text | One of six engineering/technology departments |
| `semester` | integer | 1–8 |
| `cgpa` | real | 0–10 (generated distribution is 4–10), two decimals |
| `city` | text | One of 15 Indian cities |
| `admission_year` | integer | Derived consistently from semester |

SQLite adds `NOT NULL` and range constraints. A named unique index, `idx_students_student_id`, supports primary-key lookup (the primary key also creates an automatic unique index).

## Methodology

For each scenario, the Pandas result and SQLite result are sorted deterministically and compared with `pandas.testing.assert_frame_equal`; floating-point aggregates use a tight tolerance. Timing begins only after equivalence is established.

Two categories are measured independently:

1. **End-to-end retrieval:** CSV parsing plus the Pandas operation, versus opening SQLite, executing a parameterized query, fetching the result, and closing the connection.
2. **Warm query:** the operation on an already-loaded DataFrame, versus a query using an already-open SQLite connection.

Each operation receives 5 unmeasured warm-up iterations followed by 30 measured repetitions using `time.perf_counter_ns()`. Results report median, arithmetic mean, and sample standard deviation in milliseconds. The chart uses a zero baseline; bars show medians and error bars show standard deviation.

## Benchmark scenarios

1. Primary-key lookup for `STU05000`
2. Students with CGPA greater than 8.5
3. Computer Science students in semester 4
4. Top 10 by CGPA, breaking ties by ascending student ID
5. Average CGPA grouped by department
6. Student count grouped by department

SQL filter values are passed as parameters rather than interpolated into query strings.

## Execution

Run from the `01_Logic_Auditor` directory. A virtual environment is recommended.

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Or on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install and execute the complete reproducible workflow:

```bash
python -m pip install -r requirements.txt
python run_experiment.py
python -m unittest discover -s tests -v
```

The single entry point regenerates the CSV, recreates SQLite, runs and validates all benchmarks, writes the result CSV, and creates the chart. Individual stages are also available:

```bash
python src/generate_data.py
python src/database.py
python src/benchmark.py
python src/visualize.py
```

### Faculty demonstration interface

Flask is included in `requirements.txt`. After installing the requirements, start the dashboard from this directory:

```bash
python app.py
```

Open `http://127.0.0.1:5001`. Show the existing measured table and chart, choose one of the six scenarios, and select **Run benchmark**. The demonstration performs real measurements, verifies that Pandas and SQLite return matching results, and does not overwrite `benchmark_results.csv`.

## Actual measured results

These are measurements from the verified local run described above. All values are milliseconds; `SD` is sample standard deviation across 30 measurements.

### End-to-end retrieval

| Scenario | System | Median | Mean | SD |
|---|---:|---:|---:|---:|
| Primary-key lookup | CSV/Pandas | 3.867 | 3.873 | 0.024 |
| Primary-key lookup | SQLite | 0.181 | 0.181 | 0.007 |
| CGPA > 8.5 | CSV/Pandas | 3.977 | 4.042 | 0.240 |
| CGPA > 8.5 | SQLite | 1.812 | 1.824 | 0.051 |
| Department + semester | CSV/Pandas | 3.962 | 3.970 | 0.036 |
| Department + semester | SQLite | 0.914 | 0.915 | 0.007 |
| Top 10 by CGPA | CSV/Pandas | 6.071 | 6.203 | 0.356 |
| Top 10 by CGPA | SQLite | 0.612 | 0.897 | 1.171 |
| Average CGPA by department | CSV/Pandas | 4.663 | 4.662 | 0.031 |
| Average CGPA by department | SQLite | 1.613 | 1.671 | 0.162 |
| Count by department | CSV/Pandas | 4.724 | 4.725 | 0.029 |
| Count by department | SQLite | 1.540 | 1.542 | 0.010 |

### Warm-query retrieval

| Scenario | System | Median | Mean | SD |
|---|---:|---:|---:|---:|
| Primary-key lookup | Pandas | 0.461 | 0.462 | 0.003 |
| Primary-key lookup | SQLite | 0.121 | 0.121 | 0.002 |
| CGPA > 8.5 | Pandas | 0.447 | 0.447 | 0.004 |
| CGPA > 8.5 | SQLite | 1.578 | 1.577 | 0.008 |
| Department + semester | Pandas | 0.537 | 0.538 | 0.005 |
| Department + semester | SQLite | 0.683 | 0.684 | 0.006 |
| Top 10 by CGPA | Pandas | 2.501 | 2.502 | 0.008 |
| Top 10 by CGPA | SQLite | 0.459 | 0.459 | 0.003 |
| Average CGPA by department | Pandas | 1.163 | 1.194 | 0.082 |
| Average CGPA by department | SQLite | 1.417 | 1.429 | 0.036 |
| Count by department | Pandas | 1.220 | 1.221 | 0.006 |
| Count by department | SQLite | 1.398 | 1.398 | 0.008 |

Full-precision results and environment metadata are in [`results/benchmark_results.csv`](results/benchmark_results.csv).

## Performance chart

![End-to-end and warm-query performance comparison](results/performance_comparison.png)

## Analysis and observations

- In this run, SQLite had lower end-to-end median time in every scenario because CSV/Pandas repeatedly parsed the entire text file.
- The indexed SQLite primary-key lookup had the lowest SQLite median in both categories. The index lets SQLite seek to one identifier instead of scanning every row.
- Warm Pandas was faster for broad filtering, the two-condition filter, and both grouped calculations; its columnar in-memory operations avoided file parsing and SQL-to-DataFrame conversion.
- Warm SQLite was faster for the indexed lookup and top-10 ordering in this particular run.
- The relatively large end-to-end SQLite standard deviation for top-10 retrieval shows why a median and repeated samples are more informative than one timing.
- OS file cache, SQLite page cache, interpreter state, background activity, hardware, and library versions all influence these small timings. Warm-up reduces first-use effects but does not eliminate noise.

The two categories answer different questions and must not be combined into one speedup claim. End-to-end results describe a fresh retrieval lifecycle; warm results describe repeated work after setup costs have already been paid.

## Advantages and disadvantages

| System | Advantages | Disadvantages |
|---|---|---|
| CSV/Pandas | Portable; readable; simple exchange; excellent in-memory analytical API | Full parse on each cold read; no built-in constraints, transactions, or indexes; concurrent updates are awkward |
| SQLite | SQL, constraints, transactions, indexes, selective retrieval, single-file deployment | Less human-readable; schema/query knowledge required; fetched results still incur conversion cost; not designed as a high-concurrency client/server database |

## Limitations

This is a local educational microbenchmark, not a universal database performance conclusion. It uses only 10,000 rows, one synthetic schema, one machine, one process, short operations, and 30 samples. It excludes writes, joins, concurrent clients, memory measurement, very large datasets, network databases, prepared-statement-specific analysis, and randomized benchmark ordering. File and page caches mean “end-to-end” is not the same as a guaranteed cold disk read. Pandas and SQLite also return results through different execution engines even though their logical outputs are verified as equivalent.

## Conclusion

Storage and execution context matter. SQLite's indexing and ability to query without reparsing CSV made it strong for end-to-end and selective retrieval here, while an already-loaded Pandas DataFrame was competitive or faster for several broad in-memory operations. A fair comparison therefore reports the complete lifecycle and warm state separately, validates semantics first, and treats the observed timings as local evidence rather than a general law.
