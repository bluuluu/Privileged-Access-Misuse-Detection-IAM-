from __future__ import annotations

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class RuleConfig:
    business_hours_start: time = time(hour=8)
    business_hours_end: time = time(hour=18)
    dormant_days_threshold: int = 30


@dataclass(frozen=True)
class RiskWeights:
    outside_business_hours: int = 20
    new_location: int = 25
    dormant_admin: int = 30


RULE_CONFIG = RuleConfig()
RISK_WEIGHTS = RiskWeights()
