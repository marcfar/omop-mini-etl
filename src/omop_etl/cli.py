"""Run the ETL: read source CSVs, transform, check, load into DuckDB and write a report."""

import argparse
import logging
from pathlib import Path

import duckdb
import pandas as pd

from omop_etl.checks import assert_no_nulls, assert_unique
from omop_etl.report import quality_report
from omop_etl.transformers.condition import transform_condition
from omop_etl.transformers.person import transform_observation_period, transform_person
from omop_etl.vocabulary import build_mapping_from_athena, load_mapping_csv

logger = logging.getLogger(__name__)


def run(source_dir: Path, mapping_path: Path, vocab_dir: Path | None, db_path: Path,
        report_path: Path) -> None:
    # 1. Read
    patients = pd.read_csv(
        source_dir / "patients.csv", parse_dates=["birth_date", "entry_date", "exit_date"]
    )
    diagnoses = pd.read_csv(source_dir / "diagnoses.csv", dtype={"diag_date": str})
    logger.info("Read %d patients and %d diagnoses", len(patients), len(diagnoses))

    if vocab_dir:
        mapping = build_mapping_from_athena(vocab_dir, diagnoses["icd10"].unique().tolist())
    else:
        mapping = load_mapping_csv(mapping_path)

    # 2. Transform + check (each check stops the ETL if it fails)
    tables = {
        "person": transform_person(patients)
        .pipe(assert_unique, ["person_id"])
        .pipe(assert_no_nulls, ["person_id", "gender_concept_id", "year_of_birth"]),
        "observation_period": transform_observation_period(patients)
        .pipe(assert_unique, ["person_id"]),
        "condition_occurrence": transform_condition(diagnoses, mapping)
        .pipe(assert_unique, ["condition_occurrence_id"])
        .pipe(assert_no_nulls, ["person_id", "condition_concept_id", "condition_start_date"]),
    }

    # 3. Load (CREATE OR REPLACE: running twice gives the same result)
    with duckdb.connect(str(db_path)) as con:
        for name, df in tables.items():
            con.register("df_view", df)
            con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df_view")
            con.unregister("df_view")
            logger.info("Loaded %d rows into %s", len(df), name)

    # 4. Report
    report_path.write_text(quality_report(tables, mapping), encoding="utf-8")
    logger.info("Quality report written to %s", report_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/source"))
    parser.add_argument("--mapping", type=Path, default=Path("data/icd10_to_standard.csv"),
                        help="Small manual mapping, used when --vocab is not given")
    parser.add_argument("--vocab", type=Path, default=None,
                        help="Folder with the Athena vocabulary files (CONCEPT.csv, ...)")
    parser.add_argument("--db", type=Path, default=Path("omop.duckdb"))
    parser.add_argument("--report", type=Path, default=Path("quality_report.md"))
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    run(args.source, args.mapping, args.vocab, args.db, args.report)


if __name__ == "__main__":
    main()
