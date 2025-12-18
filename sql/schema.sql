-- Table for AD / Azure AD style login events.
CREATE TABLE IF NOT EXISTS login_events (
    event_time TIMESTAMP NOT NULL,
    user_principal_name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    is_privileged BOOLEAN NOT NULL,
    location TEXT,
    ip_address TEXT,
    successful BOOLEAN,
    mfa_used BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_login_events_user_time
    ON login_events (user_principal_name, event_time);

CREATE INDEX IF NOT EXISTS idx_login_events_privileged
    ON login_events (is_privileged);
