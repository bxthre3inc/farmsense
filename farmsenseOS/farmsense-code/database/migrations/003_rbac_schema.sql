-- Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'FARMER';

-- Insert Admin and Auditor Users
INSERT INTO users (email, api_key, tier, role) VALUES
('admin@farmsense.demo', 'demo-admin-key', 'ENTERPRISE', 'ADMIN'),
('audit@farmsense.demo', 'demo-audit-key', 'FREE', 'AUDITOR')
ON CONFLICT (email) DO UPDATE SET role = EXCLUDED.role;
