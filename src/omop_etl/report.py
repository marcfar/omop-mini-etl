"""Markdown data quality report, written after each run."""

import pandas as pd


def quality_report(tables: dict[str, pd.DataFrame], mapping: pd.DataFrame) -> str:
    cond = tables["condition_occurrence"]
    obs = tables["observation_period"]
    lines = ["# Data quality report", "", "## Row counts", "", "| Table | Rows |", "| --- | --- |"]
    lines += [f"| {name} | {len(df):,} |" for name, df in tables.items()]

    # 1. Unmapped source codes
    unmapped = cond.loc[cond["condition_concept_id"] == 0, "condition_source_value"]
    pct = len(unmapped) / len(cond) if len(cond) else 0.0
    lines += [
        "", "## Unmapped conditions", "",
        f"{len(unmapped):,} of {len(cond):,} records ({pct:.1%}) have condition_concept_id = 0.",
    ]
    top = unmapped.value_counts().head(10)
    if not top.empty:
        lines += ["", "| Source code | Records |", "| --- | --- |"]
        lines += [f"| {code} | {n:,} |" for code, n in top.items()]

    # 2. Events outside the observation period
    periods = obs[["person_id", "observation_period_start_date", "observation_period_end_date"]]
    merged = cond.merge(periods, on="person_id", how="left", validate="many_to_one")
    outside = (
        merged["observation_period_start_date"].isna()
        | (merged["condition_start_date"] < merged["observation_period_start_date"])
        | (merged["condition_start_date"] > merged["observation_period_end_date"])
    )
    lines += [
        "", "## Conditions outside the observation period", "",
        (
            f"{outside.sum():,} records ({outside.mean():.1%}). They are loaded and reported "
            "here; a production ETL would decide whether to drop them."
        ),
    ]

    # 3. Mapped codes whose standard concept is not in the Condition domain
    if "domain_id" in mapping.columns:
        other = mapping.loc[mapping["domain_id"] != "Condition"]
        lines += ["", "## Codes mapped outside the Condition domain", ""]
        if other.empty:
            lines.append("None.")
        else:
            lines += ["| Source code | Concept | Domain |", "| --- | --- | --- |"]
            lines += [
                f"| {r.icd10} | {r.concept_id} {r.concept_name} | {r.domain_id} |"
                for r in other.itertuples()
            ]
    return "\n".join(lines) + "\n"
