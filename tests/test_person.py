import pytest
import pandas as pd

from omop_etl.constants import GENDER_FEMALE, GENDER_MALE, NO_MATCHING_CONCEPT
from omop_etl.transformers.person import transform_person, transform_observation_period


def test_one_row_per_patient(source_patients):
    out = transform_person(source_patients)
    assert len(out) == len(source_patients)


@pytest.mark.parametrize(
    "patient_id, expected",
    [(1, GENDER_MALE), (2, GENDER_FEMALE), (3, NO_MATCHING_CONCEPT)],
)
def test_gender_mapping(source_patients, patient_id, expected):
    out = transform_person(source_patients)
    assert out.loc[out["person_id"] == patient_id, "gender_concept_id"].item() == expected


@pytest.mark.parametrize(
    "patient_id, expected",
    [(1, 1980), (2, 1975), (3, 2001)],
)
def test_year_of_birth(source_patients, patient_id, expected):
    out = transform_person(source_patients)
    assert out.loc[out["person_id"] == patient_id, "year_of_birth"].item() == expected


@pytest.mark.parametrize(
    "patient_id, expected",
    [(1, "05"), (2, "12"), (3, "01")],
)
def test_month_of_birth(source_patients, patient_id, expected):
    out = transform_person(source_patients)
    assert out.loc[out["person_id"] == patient_id, "month_of_birth"].item() == int(expected)


@pytest.mark.parametrize(
    "patient_id, expected",
    [(1, "01"), (2, "31"), (3, "15")],
)
def test_day_of_birth(source_patients, patient_id, expected):
    out = transform_person(source_patients)
    assert out.loc[out["person_id"] == patient_id, "day_of_birth"].item() == int(expected)


def test_one_observation_period_per_patient(source_patients):
    out = transform_observation_period(source_patients)
    assert out["observation_period_id"].nunique() == len(source_patients)


@pytest.mark.parametrize(
    "observation_period_id, expected",
    [
        (1, pd.Timestamp("2010-01-01")),
        (2, pd.Timestamp("2012-06-15")),
        (3, pd.Timestamp("2015-03-01")),
    ],
)
def test_observation_period_start_date(source_patients, observation_period_id, expected):
    out = transform_observation_period(source_patients)
    assert (
        out.loc[
            out["observation_period_id"] == observation_period_id, "observation_period_start_date"
        ].item()
        == expected
    )


@pytest.mark.parametrize(
    "observation_period_id, expected",
    [
        (1, pd.Timestamp("2020-12-31")),
        (2, pd.Timestamp("2023-06-14")),
        (3, pd.Timestamp("2024-02-28")),
    ],
)
def test_observation_period_end_date(source_patients, observation_period_id, expected):
    out = transform_observation_period(source_patients)
    assert (
        out.loc[
            out["observation_period_id"] == observation_period_id, "observation_period_end_date"
        ].item()
        == expected
    )
