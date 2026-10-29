"""Source-to-standard mapping: from a small CSV or from the Athena vocabularies."""

import logging
from pathlib import Path

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)


def load_mapping_csv(path: Path) -> pd.DataFrame:
    """Read a mapping file with columns icd10, concept_id, concept_name, domain_id."""
    return pd.read_csv(path)


def build_mapping_from_athena(vocab_dir: Path, codes: list[str]) -> pd.DataFrame:
    """Map ICD10 codes to standard concepts with the 'Maps to' relationship.

    Athena files are tab-separated and have no quoting. Only the codes in `codes` are
    looked up. If a code maps to more than one standard concept, the lowest concept_id
    is kept and the code is logged (see README, limitations).
    """
    con = duckdb.connect()
    for table in ("CONCEPT", "CONCEPT_RELATIONSHIP"):
        path = (vocab_dir / f"{table}.csv").as_posix()
        con.execute(
            f"CREATE VIEW {table.lower()} AS SELECT * FROM read_csv('{path}', "
            "delim='\\t', quote='', header=true, all_varchar=true)"
        )
    con.register("source_codes", pd.DataFrame({"icd10": sorted(set(codes))}))

    mapping = con.execute("""
        SELECT s.concept_code               AS icd10,
               CAST(t.concept_id AS BIGINT) AS concept_id,
               t.concept_name,
               t.domain_id
        FROM source_codes c
        JOIN concept s
          ON s.concept_code = c.icd10
         AND s.vocabulary_id = 'ICD10'
        JOIN concept_relationship r
          ON r.concept_id_1 = s.concept_id
         AND r.relationship_id = 'Maps to'
         AND coalesce(r.invalid_reason, '') = ''
        JOIN concept t
          ON t.concept_id = r.concept_id_2
         AND t.standard_concept = 'S'
        ORDER BY icd10, concept_id
    """).df()
    con.close()

    multi = mapping.loc[mapping.duplicated("icd10", keep=False), "icd10"].unique()
    if len(multi):
        logger.warning(
            "%d codes map to more than one standard concept, keeping the first: %s",
            len(multi), sorted(multi),
        )
    logger.info("Mapped %d of %d source codes with Athena", mapping["icd10"].nunique(),
                len(set(codes)))
    return mapping.drop_duplicates("icd10", keep="first").reset_index(drop=True)
