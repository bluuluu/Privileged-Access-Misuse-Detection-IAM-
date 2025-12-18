# Privileged Identity Risk Analytics Platform (IAM Advisory)

Python rules engine + SQL patterns to spot privileged access misuse in AD / Azure AD style login logs, then roll up a per-user risk score for dashboards (Power BI / Tableau).

## Features
- Detects privileged logins outside business hours, from new locations, and dormant admin accounts being used.
- Produces event-level detections and per-user risk scores with configurable weights.
- Includes sample data (`data/logins_sample.csv`) plus SQL equivalents for database-native runs.
- Dashboard notes for quickly wiring the outputs into Power BI or Tableau.

## Quickstart
1) Create a venv and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2) Run the demo on the bundled sample data:
   ```bash
   python -m src.main --input data/logins_sample.csv --output-dir outputs
   ```
3) Outputs (written to `outputs/`):
   - `detections.csv`: Only events where a rule triggered.
   - `all_events_with_scores.csv`: Full event list with rule flags and risk score per event.
   - `user_risk_scores.csv`: Aggregated risk per user with tiers (High/Medium/Low).

## Detection rules (default thresholds)
- Business hours: 08:00–18:00 local. Privileged logins outside this window are flagged.
- New location: First login sets the baseline per user. Future privileged logins from unseen locations are flagged.
- Dormant admin use: Privileged logins after ≥30 days of inactivity for that user are flagged.

## Risk scoring
- Weights: outside hours = 20, new location = 25, dormant admin use = 30. Event scores are capped at 100.
- User rollup sums event scores and classifies: `High (>=80)`, `Medium (>=50)`, `Low (<50)`.
- Adjust weights in `src/config.py` if you need stricter or looser scoring.

## Project structure
- `src/` — ingestion, rule logic, scoring, CLI.
- `data/logins_sample.csv` — sample AD/Azure AD style events.
- `sql/` — schema and detection queries (PostgreSQL-friendly).
- `dashboard/README.md` — guidance for Power BI / Tableau wiring.

## Data format
CSV columns expected by the Python pipeline:
```
timestamp,user,account_type,is_privileged,location,ip_address,successful,mfa_used
```
Timestamps should be parseable by pandas (e.g., `YYYY-MM-DD HH:MM:SS`).

## SQL option
If you prefer running detections in-database, see `sql/schema.sql` and `sql/detection_queries.sql` for sample DDL and queries that mirror the Python rules.

## Extending
- Add geo-IP normalization or device fingerprinting to reduce noise from VPNs.
- Plug into SIEM (e.g., Sentinel) to stream detections to tickets.
- Enrich with HR data (join/leave dates) for better dormant-account decisions.
