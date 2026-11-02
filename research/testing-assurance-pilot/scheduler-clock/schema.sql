-- Independent immutable-UTC Cloudflare Cron observation history.
-- Retained beyond GitHub's run-log retention.
CREATE TABLE IF NOT EXISTS ticks (
  scheduled_ms INTEGER PRIMARY KEY,
  observed_ms INTEGER NOT NULL,
  last_seen_ms INTEGER NOT NULL,
  cron TEXT NOT NULL,
  duplicate_count INTEGER NOT NULL DEFAULT 0,
  dispatch_status TEXT NOT NULL,
  http_code INTEGER,
  error_code TEXT
);
