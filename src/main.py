from __future__ import annotations

import argparse
from pathlib import Path

from .ingest import load_login_events
from .rules import apply_rules
from .risk_scoring import score_events, summarize_user_risk
from .reporting import export_events, export_user_risk


def run_pipeline(input_path: Path, output_dir: Path) -> None:
    df = load_login_events(input_path)
    with_rules = apply_rules(df)
    scored = score_events(with_rules)
    user_risk = summarize_user_risk(scored)

    export_events(scored, output_dir)
    export_user_risk(user_risk, output_dir)

    top = user_risk.head(5)
    print("\nTop risky users")
    print(top.to_string(index=False))
    print(f"\nWrote detections to: {output_dir.resolve()}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Privileged Access Misuse Detection (IAM Advisory demo)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/logins_sample.csv"),
        help="Path to login events CSV (default: data/logins_sample.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Where to write detections and risk scores (default: outputs)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_pipeline(args.input, args.output_dir)


if __name__ == "__main__":
    main()
