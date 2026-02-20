-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR NOT NULL UNIQUE,
    api_key VARCHAR NOT NULL UNIQUE,
    tier VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Create index on api_key for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

-- Insert Demo Users
INSERT INTO users (email, api_key, tier) VALUES
('free@farmsense.demo', 'demo-free-key', 'FREE'),
('basic@farmsense.demo', 'demo-basic-key', 'BASIC'),
('pro@farmsense.demo', 'demo-pro-key', 'PRO'),
('ent@farmsense.demo', 'demo-enterprise-key', 'ENTERPRISE')
ON CONFLICT (email) DO NOTHING;
