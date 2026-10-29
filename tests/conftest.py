import pandas as pd
import pytest


@pytest.fixture
def source_patients():
    return pd.DataFrame(
        {
            "patient_id": [1, 2, 3],
            "sex": ["H", "D", ""],
            "birth_date": pd.to_datetime(["1980-05-01", "1975-12-31", "2001-01-15"]),
            "entry_date": pd.to_datetime(["2010-01-01", "2012-06-15", "2015-03-01"]),
            "exit_date": pd.to_datetime(["2020-12-31", "2023-06-14", "2024-02-28"]),
        }
    )


@pytest.fixture
def source_diagnoses():
    return pd.DataFrame(
        {
            "diag_id": [1, 2, 3, 4],
            "patient_id": [1, 1, 2, 3],
            "icd10": ["E11.9", "E11.9", "I10", "XX.99"],
            "diag_date": ["20150310", "20150310", "20180101", "20200505"],  # rows 1-2 duplicated
        }
    )


@pytest.fixture
def mapping():
    return pd.DataFrame({"icd10": ["E11.9", "I10"], "concept_id": [201826, 320128]})
