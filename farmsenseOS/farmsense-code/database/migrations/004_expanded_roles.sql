-- Insert C-Suite and Stakeholder Users
INSERT INTO users (email, api_key, tier, role) VALUES
('csu@farmsense.demo', 'demo-research-key', 'ENTERPRISE', 'RESEARCHER'),
('money@farmsense.demo', 'demo-investor-key', 'PRO', 'INVESTOR'),
('grant@farmsense.demo', 'demo-grant-key', 'FREE', 'REVIEWER')
ON CONFLICT (email) DO UPDATE SET role = EXCLUDED.role;
