-- Detection rules in SQL (PostgreSQL dialect).
-- Business hours: 08:00 - 18:00 local time; Dormant threshold: 30 days.

WITH ordered AS (
    SELECT
        event_time,
        user_principal_name,
        account_type,
        is_privileged,
        location,
        ip_address,
        successful,
        mfa_used,
        LAG(event_time) OVER (PARTITION BY user_principal_name ORDER BY event_time) AS prev_event_time
    FROM login_events
),
detections AS (
    SELECT
        ordered.*,
        -- Privileged logins outside business hours
        CASE
            WHEN is_privileged
                 AND EXTRACT(HOUR FROM event_time)::INT NOT BETWEEN 8 AND 18 THEN TRUE
            ELSE FALSE
        END AS rule_outside_business_hours,

        -- Privileged logins from locations the user has never used before
        CASE
            WHEN is_privileged
                 AND NOT EXISTS (
                    SELECT 1
                    FROM login_events l2
                    WHERE l2.user_principal_name = ordered.user_principal_name
                      AND l2.event_time < ordered.event_time
                      AND l2.location = ordered.location
                 )
                 AND EXISTS (
                    SELECT 1
                    FROM login_events l3
                    WHERE l3.user_principal_name = ordered.user_principal_name
                      AND l3.event_time < ordered.event_time
                 )
            THEN TRUE
            ELSE FALSE
        END AS rule_new_location,

        -- Dormant privileged accounts being used after long inactivity
        CASE
            WHEN is_privileged
                 AND prev_event_time IS NOT NULL
                 AND event_time - prev_event_time > INTERVAL '30 days'
            THEN TRUE
            ELSE FALSE
        END AS rule_dormant_admin_use
    FROM ordered
),
risk_rollup AS (
    SELECT
        user_principal_name,
        COUNT(*) AS total_events,
        SUM(is_privileged::INT) AS privileged_events,
        SUM(rule_outside_business_hours::INT) AS outside_hours_hits,
        SUM(rule_new_location::INT) AS new_location_hits,
        SUM(rule_dormant_admin_use::INT) AS dormant_admin_hits,
        SUM(
            CASE WHEN rule_outside_business_hours THEN 20 ELSE 0 END
            + CASE WHEN rule_new_location THEN 25 ELSE 0 END
            + CASE WHEN rule_dormant_admin_use THEN 30 ELSE 0 END
        ) AS total_risk_score
    FROM detections
    GROUP BY user_principal_name
)

-- Result 1: event-level detections
SELECT * FROM detections;

-- Result 2: user-level risk rollup
SELECT * FROM risk_rollup ORDER BY total_risk_score DESC;
