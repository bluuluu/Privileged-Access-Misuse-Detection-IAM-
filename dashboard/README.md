# Dashboard Notes (Power BI / Tableau)

Use the generated CSVs to build a simple privileged identity risk dashboard.

## Data sources
- `outputs/user_risk_scores.csv`: per-user rollup with counts and risk tier.
- `outputs/detections.csv`: rule-level events for drill-down.
- `outputs/all_events_with_scores.csv`: full event history with scores for trend charts.

## Suggested visuals
- Risk heatmap: `user` on rows, `total_risk_score` on values, conditional color by `risk_tier`.
- Bar chart: `outside_hours_hits`, `new_location_hits`, `dormant_admin_hits` per user.
- Line or area chart: daily count of `any_rule_triggered` to see spikes.
- Table drill-down: show `timestamp`, `user`, `location`, `ip_address`, triggered rules, `risk_score_event`.
- Slicer/filters: `risk_tier`, `account_type`, date range, `mfa_used`.

## Build steps
1) Import the CSVs as separate tables.
2) Create relationships on `user` between detections and the user rollup.
3) Define measures (Power BI) or calculated fields (Tableau), for example:
   - `Total Risk Score = SUM(user_risk_scores[total_risk_score])`
   - `Events Outside Hours = SUM(detections[rule_outside_business_hours])`
4) Add a page with high-level KPIs: number of privileged users, total detections, high-risk users.
5) Add a drill-through page from user -> event list to support investigations.

## Layout tips
- Use a neutral palette with accent colors for severity (green/amber/red).
- Pin a text box summarizing the detection logic and thresholds so auditors know the scope.
