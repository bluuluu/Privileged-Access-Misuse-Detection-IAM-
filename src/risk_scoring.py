from __future__ import annotations

import pandas as pd

from .config import RISK_WEIGHTS


def score_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a per-event risk score based on which rules triggered.
    """
    scored = df.copy()
    scored["risk_score_event"] = (
        scored["rule_outside_business_hours"].astype(int) * RISK_WEIGHTS.outside_business_hours
        + scored["rule_new_location"].astype(int) * RISK_WEIGHTS.new_location
        + scored["rule_dormant_admin_use"].astype(int) * RISK_WEIGHTS.dormant_admin
    ).clip(upper=100)
    return scored


def _tier(score: float) -> str:
    if score >= 80:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def summarize_user_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate event risk into a per-user view.
    """
    summary = (
        df.groupby("user").agg(
            total_events=("timestamp", "count"),
            privileged_events=("is_privileged", "sum"),
            outside_hours_hits=("rule_outside_business_hours", "sum"),
            new_location_hits=("rule_new_location", "sum"),
            dormant_admin_hits=("rule_dormant_admin_use", "sum"),
            total_risk_score=("risk_score_event", "sum"),
        )
    ).reset_index()

    summary["risk_tier"] = summary["total_risk_score"].apply(_tier)
    return summary.sort_values("total_risk_score", ascending=False)
