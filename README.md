# OMOP mini ETL

A small ETL that converts **synthetic** primary care data into the
[OMOP Common Data Model](https://ohdsi.github.io/CommonDataModel/) (v5.4 table and column names).

I built it to learn OMOP. In my current job I maintain the ETL of a primary care database
into the ConcePTION CDM, where source codes are kept and harmonised in each study. The main
new part for me in OMOP is the vocabulary mapping to standard concepts, so this project
focuses on that.

## What it does

| Source file | OMOP table | Main rules |
| --- | --- | --- |
| `patients.csv` | `person` | Sex `H`/`D` to gender concepts, unknown to 0. Race and ethnicity are not recorded in Spain, so 0 |
| `patients.csv` | `observation_period` | One period per patient, from registration to exit date |
| `diagnoses.csv` | `condition_occurrence` | Exact duplicates removed, dates parsed from `YYYYMMDD`, ICD10 mapped to standard concepts |

The pipeline has four steps:

1. **Read** the source CSV files and the vocabulary mapping.
2. **Transform** each table with a pure function.
3. **Check** each table (unique ids, no nulls in required columns). A failed check stops the ETL.
4. **Load** the tables into a DuckDB database and write a data quality report.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux / macOS: source .venv/bin/activate
pip install -e ".[dev]"

python data/generate_source.py    # creates synthetic data in data/source/
pytest                            # unit tests
omop-etl                          # runs the ETL with the small manual mapping
```

### With the real OHDSI vocabularies

Download the vocabularies from [Athena](https://athena.ohdsi.org) (ICD10, SNOMED and their
dependencies), unzip them in a folder (for example `vocab/`) and run:

```bash
omop-etl --vocab vocab/
```

The ETL reads `CONCEPT.csv` and `CONCEPT_RELATIONSHIP.csv` with DuckDB, without loading them
into memory, and maps each ICD10 code with the `Maps to` relationship to a standard concept.
The vocabulary files are not in this repository (size and licence).

Output:

- `omop.duckdb`: the OMOP tables.
- `quality_report.md`: row counts, unmapped codes, conditions outside the observation
  period, and codes whose standard concept is not in the Condition domain.

## Project structure

```text
src/omop_etl/
    cli.py              # entry point: read, transform, check, load, report
    vocabulary.py       # mapping from a small CSV or from the Athena files
    transformers/       # one module per source: pure functions, no I/O
    checks.py           # data quality checks, used with DataFrame.pipe()
    report.py           # markdown quality report
    constants.py        # OMOP concept ids with readable names
tests/                  # pytest, with small hand-made datasets
data/                   # synthetic data generator and small manual mapping
```

## Design decisions

- **Transformations are pure functions.** They receive DataFrames and return DataFrames,
  without reading or writing files. This makes them easy to test with a few rows.
- **Unmapped codes are kept.** They get `concept_id = 0`, and the original code stays in
  `condition_source_value`. The report lists the most frequent unmapped codes, so they can
  be mapped first.
- **The merge with the vocabulary cannot change the number of rows silently.** It is a left
  join with `validate="many_to_one"`, and all output columns are built from the merged table.
- **Exact duplicates** (same patient, code and date) are removed before mapping.
- **Quality checks stop the ETL.** It is better to fail with a clear message than to load a
  wrong table.
- **Idempotent load.** Tables are created with `CREATE OR REPLACE`, so running the ETL twice
  gives the same result.
- **No magic numbers.** Concept ids like 8507 (male) are named constants.
- **Configuration from the command line**, not hard-coded paths.

## Limitations and next steps

- **One standard concept per source code.** If an ICD10 code maps to more than one standard
  concept, the ETL keeps the first one and logs a warning. OMOP would create one row per
  standard concept.
- **Domain routing.** All diagnoses go to `condition_occurrence`. In OMOP, the domain of the
  standard concept decides the table (for example `observation`). The report lists these
  codes.
- **Events outside the observation period** are loaded and reported, not removed. With the
  synthetic data many of them are outside, because dates are random.
- **Next tables:** `drug_exposure` (ATC to RxNorm / RxNorm Extension ingredients),
  `measurement` (local lab codes to LOINC), and `drug_era`.
- **Next checks:** run the OHDSI
  [Data Quality Dashboard](https://github.com/OHDSI/DataQualityDashboard) and Achilles on the
  result.
- For large volumes, more of the transformation could run as SQL inside the database.
