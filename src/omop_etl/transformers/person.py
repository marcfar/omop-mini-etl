"""Source patients -> OMOP person and observation_period."""

import pandas as pd

from omop_etl.constants import GENDER_FEMALE, GENDER_MALE, NO_MATCHING_CONCEPT, TYPE_EHR


def transform_person(patients: pd.DataFrame) -> pd.DataFrame:
    """Return the OMOP person table.

    Output columns: person_id, gender_concept_id, year_of_birth, month_of_birth,
    day_of_birth, race_concept_id, ethnicity_concept_id, person_source_value,
    gender_source_value.

    Rules:
    - sex "H" -> GENDER_MALE, "D" -> GENDER_FEMALE, anything else -> NO_MATCHING_CONCEPT
    - race and ethnicity are not recorded in Spain -> NO_MATCHING_CONCEPT
    """

    return pd.DataFrame(
        {
            "person_id": patients["patient_id"],
            "gender_concept_id": (
                patients["sex"]
                .map({"H": GENDER_MALE, "D": GENDER_FEMALE})
                .fillna(NO_MATCHING_CONCEPT)
                .astype("int64")
            ),
            "year_of_birth": patients["birth_date"].dt.year,
            "month_of_birth": patients["birth_date"].dt.month,
            "day_of_birth": patients["birth_date"].dt.day,
            "race_concept_id": NO_MATCHING_CONCEPT,
            "ethnicity_concept_id": NO_MATCHING_CONCEPT,
            "person_source_value": patients["patient_id"].astype(str),
            "gender_source_value": patients["sex"],
        }
    )


def transform_observation_period(patients: pd.DataFrame) -> pd.DataFrame:
    """Return the OMOP observation_period table.

    Output columns: observation_period_id, person_id, observation_period_start_date,
    observation_period_end_date, period_type_concept_id (= TYPE_EHR).
    """
    return pd.DataFrame(
        {
            "observation_period_id": range(1, len(patients) + 1),
            "person_id": patients["patient_id"],
            "observation_period_start_date": patients["entry_date"],
            "observation_period_end_date": patients["exit_date"],
            "period_type_concept_id": TYPE_EHR,
        }
    )
