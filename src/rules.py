from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import pandas as pd

from .config import RULE_CONFIG


def flag_outside_business_hours(df: pd.DataFrame) -> pd.Series:
    start = RULE_CONFIG.business_hours_start
    end = RULE_CONFIG.business_hours_end

    def is_outside(ts: datetime) -> bool:
        t = ts.time()
        return not (start <= t <= end)

    return df["timestamp"].apply(is_outside) & df["is_privileged"]


def flag_new_locations(df: pd.DataFrame) -> pd.Series:
    """
    Flag privileged logins when the location has not been seen before for that user.
    The first login for a user establishes the baseline and is not flagged.
    """
    seen_locations: dict[str, set[str]] = defaultdict(set)
    flags: dict[int, bool] = {}

    df_sorted = df.sort_values("timestamp")
    for idx, row in df_sorted.iterrows():
        user = row["user"]
        location = row["location"]
        if not row["is_privileged"]:
            flags[idx] = False
            continue

        is_new = len(seen_locations[user]) > 0 and location not in seen_locations[user]
        flags[idx] = is_new
        seen_locations[user].add(location)

    return pd.Series(flags).reindex(df.index, fill_value=False)


def flag_dormant_admin_use(df: pd.DataFrame) -> pd.Series:
    """
    Flag privileged logins that occur after a long period of inactivity for that user.
    """
    last_seen: dict[str, datetime] = {}
    flags: dict[int, bool] = {}
    threshold_days = RULE_CONFIG.dormant_days_threshold

    df_sorted = df.sort_values("timestamp")
    for idx, row in df_sorted.iterrows():
        user = row["user"]
        if not row["is_privileged"]:
            flags[idx] = False
            continue

        last_ts = last_seen.get(user)
        is_dormant = bool(
            last_ts and (row["timestamp"] - last_ts).days >= threshold_days
        )
        flags[idx] = is_dormant
        last_seen[user] = row["timestamp"]

    return pd.Series(flags).reindex(df.index, fill_value=False)


def apply_rules(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["rule_outside_business_hours"] = flag_outside_business_hours(enriched)
    enriched["rule_new_location"] = flag_new_locations(enriched)
    enriched["rule_dormant_admin_use"] = flag_dormant_admin_use(enriched)
    return enriched
