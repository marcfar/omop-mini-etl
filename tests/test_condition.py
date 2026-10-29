import pytest 
import pandas as pd
from omop_etl.transformers.condition import transform_condition


def test_unmapped_code_gets_concept_zero(source_diagnoses, mapping):
    out = transform_condition(source_diagnoses, mapping)
    row = out.loc[out["condition_source_value"] == "XX.99"]
    assert row["condition_concept_id"].item() == 0

def test_duplicates_are_removed(source_diagnoses, mapping):
    out = transform_condition(source_diagnoses, mapping)
    assert len(out) == 3    # 4 source rows, rows 1 and 2 are the same diagnosis


def test_duplicates_are_removed(source_diagnoses, mapping):
    out = transform_condition(source_diagnoses, mapping)
    assert len(out) == 3    # 4 source rows, rows 1 and 2 are the same diagnosis



@pytest.mark.parametrize(
    "person_id, expected",
    [(1, "E11.9"), (2, "I10"), (3,"XX.99")]
)
def test_condition_source_value_keeps_original_code(source_diagnoses, mapping, person_id, expected):
    out = transform_condition(source_diagnoses,mapping)
    assert out.loc[
        out['person_id'] == person_id, "condition_source_value"
        ].item() == expected

@pytest.mark.parametrize(
    "person_id, expected",
    [
        (1, pd.Timestamp("2015-03-10")),
        (2, pd.Timestamp("2018-01-01")),
        (3, pd.Timestamp("2020-05-05")),
    ],
)
def test_date_is_parsed_correctly(source_diagnoses, mapping, person_id, expected):
    out = transform_condition(source_diagnoses,mapping)
    assert out.loc[
        out['person_id'] == person_id, "condition_start_date"
        ].item() == expected    
# TODO: test the date is parsed correctly from YYYYMMDD

