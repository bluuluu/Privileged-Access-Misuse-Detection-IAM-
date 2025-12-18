from __future__ import annotations

from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "user",
    "account_type",
    "is_privileged",
    "location",
    "ip_address",
    "successful",
    "mfa_used",
}


def load_login_events(csv_path: Path) -> pd.DataFrame:
    """
    Load login events CSV into a DataFrame and enforce the expected schema.
    """
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    missing_cols = REQUIRED_COLUMNS.difference(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_cols))}")

    df["is_privileged"] = df["is_privileged"].astype(bool)
    df["successful"] = df["successful"].astype(bool)
    df["mfa_used"] = df["mfa_used"].astype(bool)

    # Clean user/location strings to avoid stray whitespace.
    df["user"] = df["user"].str.strip()
    df["location"] = df["location"].str.strip()

    return df
