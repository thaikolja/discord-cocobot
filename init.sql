-- Database initialization script for cocobot
-- This file is run once when the PostgreSQL container is first created

-- Create the cocobot database (though it's already created by the POSTGRES_DB env var)
-- CREATE DATABASE cocobot;

-- Create tables (these would normally be created by SQLAlchemy migrations)
-- Since we're using SQLAlchemy, the tables will be created when the app starts
-- This file can contain any additional setup if needed

-- Example: Create an initial admin user (uncomment and customize if needed)
-- INSERT INTO users (discord_id, username, discriminator, is_premium, created_at, updated_at) 
-- VALUES ('123456789', 'admin', '0000', true, NOW(), NOW())
-- ON CONFLICT (discord_id) DO NOTHING;

-- Example: Set initial settings (uncomment and customize if needed)
-- INSERT INTO bot_settings (key, value, description) 
-- VALUES ('bot_version', '2.4.0', 'Current bot version')
-- ON CONFLICT (key) DO NOTHING;

-- Additional initialization can go here