"""Source diagnoses -> OMOP condition_occurrence."""

import pandas as pd

from omop_etl.constants import NO_MATCHING_CONCEPT, TYPE_EHR


def transform_condition(diagnoses: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Return the OMOP condition_occurrence table.

    Output columns: condition_occurrence_id, person_id, condition_concept_id,
    condition_start_date, condition_type_concept_id, condition_source_value.

    Rules:
    - remove exact duplicates (same patient, code and date)
    - dates come as text YYYYMMDD
    - map icd10 with `mapping` (columns icd10, concept_id); unmapped -> NO_MATCHING_CONCEPT
    - keep the original code in condition_source_value
    - the number of rows must not change in the merge (validate it)
    """
    clean = diagnoses.drop_duplicates(subset=["patient_id", "icd10", "diag_date"])
    merged = clean.merge(
        mapping[["icd10", "concept_id"]], on="icd10", how="left", validate="many_to_one"
    )

    return pd.DataFrame(
        {
            "condition_occurrence_id": range(1, len(merged) + 1),
            "person_id": merged["patient_id"],
            "condition_concept_id": merged["concept_id"]
            .fillna(NO_MATCHING_CONCEPT)
            .astype("int64"),
            "condition_start_date": pd.to_datetime(merged["diag_date"], format="%Y%m%d"),
            "condition_type_concept_id": TYPE_EHR,
            "condition_source_value": merged["icd10"].astype(str),
        }
    )
