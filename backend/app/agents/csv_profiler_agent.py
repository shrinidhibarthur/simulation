"""
Step 4 — CSV Profiler Agent.
Reads CSV, extracts column statistics, sends stats (not raw data) to Gemini,
which suggests Beta/Lognormal distributions for each column.
PII columns are stripped before the Gemini call.
"""
import io
import re

import numpy as np
import pandas as pd

from app.models.simulation import Simulation

PII_PATTERNS = re.compile(r"\b(email|phone|customer_id|loyalty_id|ssn|dob|birth|address)\b", re.I)

PROFILER_PROMPT = """
You are a statistical distribution expert for e-commerce data at Albertsons.

Column statistics from a data export (raw data NOT included — only summary stats):
{column_stats_json}

Recommend probability distributions for Monte Carlo simulation.

Rules:
- Conversion rates, CTR, click rates (values 0-1): recommend Beta(alpha, beta)
- AOV, revenue, margin, spend (positive values, right-skewed): recommend Lognormal(mu, sigma)
- Counts, inventory levels: recommend Normal(mu, sigma) or Poisson(lambda)

For each column return:
- column_name
- distribution_type: "Beta" | "Lognormal" | "Normal" | "Poisson" | "skip"
- params: dict with distribution parameters (alpha/beta for Beta, mu/sigma for others)
- rationale: one sentence

Also identify which columns map to these Albertsons KPIs:
- cvr_column, aov_column, rpv_column, margin_column, stockout_column

Return ONLY this JSON:
{{
  "column_mappings": [...],
  "kpi_column_map": {{"cvr_column": "...", "aov_column": "...", "rpv_column": "...", "margin_column": "...", "stockout_column": "..."}}
}}
No markdown. No explanation.
"""


def _profile_dataframe(df: pd.DataFrame) -> dict:
    stats = {}
    for col in df.columns:
        if PII_PATTERNS.search(col):
            continue
        s = df[col]
        numeric_s = pd.to_numeric(s, errors="coerce")
        null_rate = float(s.isna().mean())
        if numeric_s.notna().sum() > 0:
            stats[col] = {
                "dtype": str(s.dtype),
                "null_rate": round(null_rate, 4),
                "mean": float(numeric_s.mean()),
                "std": float(numeric_s.std()),
                "min": float(numeric_s.min()),
                "max": float(numeric_s.max()),
                "p5": float(np.percentile(numeric_s.dropna(), 5)),
                "p95": float(np.percentile(numeric_s.dropna(), 95)),
                "n_unique": int(s.nunique()),
                "n_rows": int(len(s)),
            }
        else:
            stats[col] = {
                "dtype": str(s.dtype),
                "null_rate": round(null_rate, 4),
                "n_unique": int(s.nunique()),
                "n_rows": int(len(s)),
                "sample_values": s.dropna().head(3).tolist(),
            }
    return stats


async def profile_csv(sim: Simulation, file_path: str, content: bytes) -> dict:
    import json
    from app.agents.gemini_client import generate_json

    df = pd.read_csv(io.BytesIO(content), nrows=10_000)
    column_stats = _profile_dataframe(df)
    stats_json = json.dumps(column_stats, indent=2)

    prompt = PROFILER_PROMPT.format(column_stats_json=stats_json)
    result = await generate_json(prompt)

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_stats": column_stats,
        "distribution_suggestions": result.get("column_mappings", []),
        "kpi_column_map": result.get("kpi_column_map", {}),
    }
