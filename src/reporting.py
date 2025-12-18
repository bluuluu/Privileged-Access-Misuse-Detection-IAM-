from __future__ import annotations

from pathlib import Path
import pandas as pd


def export_events(scored_df: pd.DataFrame, output_dir: Path) -> None:
    """
    Write detailed events and rule hits to CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    scored_df["any_rule_triggered"] = (
        scored_df["rule_outside_business_hours"]
        | scored_df["rule_new_location"]
        | scored_df["rule_dormant_admin_use"]
    )

    detections = scored_df[scored_df["any_rule_triggered"]].copy()
    detections.to_csv(output_dir / "detections.csv", index=False)
    scored_df.to_csv(output_dir / "all_events_with_scores.csv", index=False)


def export_user_risk(summary_df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_dir / "user_risk_scores.csv", index=False)
