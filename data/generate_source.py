"""Generate synthetic source data (never real patient data)."""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "source"
rng = np.random.default_rng(42)
N_PATIENTS = 10_000
N_DIAG = 60_000

patients = pd.DataFrame(
    {
        "patient_id": np.arange(1, N_PATIENTS + 1),
        "sex": rng.choice(["H", "D", ""], N_PATIENTS, p=[0.49, 0.50, 0.01]),
        "birth_date": pd.Timestamp("1930-01-01")
        + pd.to_timedelta(rng.integers(0, 90 * 365, N_PATIENTS), unit="D"),
        "entry_date": pd.Timestamp("2006-01-01")
        + pd.to_timedelta(rng.integers(0, 15 * 365, N_PATIENTS), unit="D"),
    }
)
patients["exit_date"] = patients["entry_date"] + pd.to_timedelta(
    rng.integers(365, 10 * 365, N_PATIENTS), unit="D"
)

diagnoses = pd.DataFrame(
    {
        "patient_id": rng.integers(1, N_PATIENTS + 1, N_DIAG),
        "icd10": rng.choice(["E11.9", "I10", "J45", "E78.5", "F32.9", "XX.99"], N_DIAG),
        "diag_date": (
            pd.Timestamp("2006-01-01")
            + pd.to_timedelta(rng.integers(0, 20 * 365, N_DIAG), unit="D")
        ).strftime("%Y%m%d"),
    }
)
diagnoses = pd.concat([diagnoses, diagnoses.sample(500, random_state=1)])  # duplicates on purpose
diagnoses.insert(0, "diag_id", np.arange(1, len(diagnoses) + 1))

OUT.mkdir(exist_ok=True)
patients.to_csv(OUT / "patients.csv", index=False)
diagnoses.to_csv(OUT / "diagnoses.csv", index=False)
print(f"patients: {len(patients):,} rows, diagnoses: {len(diagnoses):,} rows")
