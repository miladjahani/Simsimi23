/*
# Milijon Railway Panel - Complete Database Schema

## Overview
Full schema for a professional VPN/proxy management panel supporting
VLESS, VMess, Trojan, Shadowsocks protocols with WebSocket, gRPC, HTTP/2, TCP transports.
Designed for Railway deployment with Python/Flask backend.

## New Tables

1. `inbounds` - Proxy inbound configurations (listeners)
   - id (uuid, pk)
   - tag (text) - friendly name
   - protocol (text) - vless, vmess, trojan, shadowsocks
   - transport (text) - ws, grpc, h2, tcp
   - listen_ip (text)
   - listen_port (integer)
   - settings (jsonb) - protocol-specific settings (network params, TLS, etc.)
   - is_active (boolean)
   - created_at, updated_at

2. `clients` - End-user accounts/clients
   - id (uuid, pk)
   - uuid (uuid) - unique client identifier for links
   - email (text) - display name / identifier
   - inbound_ids (uuid[]) - which inbounds this client has access to
   - enable (boolean)
   - total_gb (bigint) - data limit in bytes (0 = unlimited)
   - used_gb (bigint) - data used in bytes
   - expiry_days (integer) - days until expiry from creation (0 = unlimited)
   - expiry_date (timestamptz) - computed expiry
   - sub_id (text) - subscription ID for sub links
   - tg_id (text) - Telegram chat ID (optional)
   - created_at, updated_at

3. `subscriptions` - Subscription link records
   - id (uuid, pk)
   - sub_id (text, unique) - token in subscription URL
   - client_id (uuid, fk -> clients)
   - name (text)
   - last_check (timestamptz) - last time sub was fetched
   - update_count (integer) - how many times updated
   - created_at

4. `servers` - Backend server nodes
   - id (uuid, pk)
   - name (text)
   - address (text) - IP or domain
   - port (integer)
   - server_type (text) - master, worker
   - is_online (boolean)
   - cpu_usage (real)
   - mem_usage (real)
   - net_usage (real)
   - version (text)
   - last_seen (timestamptz)
   - created_at

5. `settings` - Panel configuration (key-value)
   - id (uuid, pk)
   - key (text, unique)
   - value (jsonb)
   - category (text) - panel, security, subscription, telegram
   - updated_at

6. `traffic_logs` - Traffic history records
   - id (uuid, pk)
   - client_id (uuid, fk -> clients)
   - inbound_id (uuid, fk -> inbounds)
   - uplink (bigint)
   - downlink (bigint)
   - recorded_at (timestamptz)

## Security
- RLS enabled on all tables
- Single-tenant panel: all tables accessible by anon+authenticated (no sign-in screen)
- Data is intentionally shared for panel operation
*/

-- Inbounds table
CREATE TABLE IF NOT EXISTS inbounds (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tag text NOT NULL,
  protocol text NOT NULL CHECK (protocol IN ('vless', 'vmess', 'trojan', 'shadowsocks')),
  transport text NOT NULL CHECK (transport IN ('ws', 'grpc', 'h2', 'tcp')),
  listen_ip text NOT NULL DEFAULT '0.0.0.0',
  listen_port integer NOT NULL,
  settings jsonb NOT NULL DEFAULT '{}',
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE inbounds ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_crud_inbounds_sel" ON inbounds;
CREATE POLICY "anon_crud_inbounds_sel" ON inbounds FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_crud_inbounds_ins" ON inbounds;
CREATE POLICY "anon_crud_inbounds_ins" ON inbounds FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_inbounds_upd" ON inbounds;
CREATE POLICY "anon_crud_inbounds_upd" ON inbounds FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_inbounds_del" ON inbounds;
CREATE POLICY "anon_crud_inbounds_del" ON inbounds FOR DELETE TO anon, authenticated USING (true);

-- Clients table
CREATE TABLE IF NOT EXISTS clients (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  uuid uuid NOT NULL DEFAULT gen_random_uuid(),
  email text NOT NULL,
  inbound_ids uuid[] NOT NULL DEFAULT '{}',
  enable boolean NOT NULL DEFAULT true,
  total_gb bigint NOT NULL DEFAULT 0,
  used_gb bigint NOT NULL DEFAULT 0,
  expiry_days integer NOT NULL DEFAULT 0,
  expiry_date timestamptz,
  sub_id text UNIQUE,
  tg_id text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_crud_clients_sel" ON clients;
CREATE POLICY "anon_crud_clients_sel" ON clients FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_crud_clients_ins" ON clients;
CREATE POLICY "anon_crud_clients_ins" ON clients FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_clients_upd" ON clients;
CREATE POLICY "anon_crud_clients_upd" ON clients FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_clients_del" ON clients;
CREATE POLICY "anon_crud_clients_del" ON clients FOR DELETE TO anon, authenticated USING (true);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sub_id text UNIQUE NOT NULL,
  client_id uuid REFERENCES clients(id) ON DELETE CASCADE,
  name text,
  last_check timestamptz,
  update_count integer NOT NULL DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_crud_subs_sel" ON subscriptions;
CREATE POLICY "anon_crud_subs_sel" ON subscriptions FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_crud_subs_ins" ON subscriptions;
CREATE POLICY "anon_crud_subs_ins" ON subscriptions FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_subs_upd" ON subscriptions;
CREATE POLICY "anon_crud_subs_upd" ON subscriptions FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_subs_del" ON subscriptions;
CREATE POLICY "anon_crud_subs_del" ON subscriptions FOR DELETE TO anon, authenticated USING (true);

-- Servers table
CREATE TABLE IF NOT EXISTS servers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  address text NOT NULL,
  port integer NOT NULL,
  server_type text NOT NULL DEFAULT 'worker' CHECK (server_type IN ('master', 'worker')),
  is_online boolean NOT NULL DEFAULT true,
  cpu_usage real NOT NULL DEFAULT 0,
  mem_usage real NOT NULL DEFAULT 0,
  net_usage real NOT NULL DEFAULT 0,
  version text NOT NULL DEFAULT '1.0.0',
  last_seen timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

ALTER TABLE servers ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_crud_servers_sel" ON servers;
CREATE POLICY "anon_crud_servers_sel" ON servers FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_crud_servers_ins" ON servers;
CREATE POLICY "anon_crud_servers_ins" ON servers FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_servers_upd" ON servers;
CREATE POLICY "anon_crud_servers_upd" ON servers FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_servers_del" ON servers;
CREATE POLICY "anon_crud_servers_del" ON servers FOR DELETE TO anon, authenticated USING (true);

-- Settings table (key-value store)
CREATE TABLE IF NOT EXISTS settings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key text UNIQUE NOT NULL,
  value jsonb NOT NULL DEFAULT '{}',
  category text NOT NULL DEFAULT 'panel',
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_crud_settings_sel" ON settings;
CREATE POLICY "anon_crud_settings_sel" ON settings FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_crud_settings_ins" ON settings;
CREATE POLICY "anon_crud_settings_ins" ON settings FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_settings_upd" ON settings;
CREATE POLICY "anon_crud_settings_upd" ON settings FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_settings_del" ON settings;
CREATE POLICY "anon_crud_settings_del" ON settings FOR DELETE TO anon, authenticated USING (true);

-- Traffic logs table
CREATE TABLE IF NOT EXISTS traffic_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id uuid REFERENCES clients(id) ON DELETE CASCADE,
  inbound_id uuid REFERENCES inbounds(id) ON DELETE CASCADE,
  uplink bigint NOT NULL DEFAULT 0,
  downlink bigint NOT NULL DEFAULT 0,
  recorded_at timestamptz DEFAULT now()
);

ALTER TABLE traffic_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_crud_traffic_sel" ON traffic_logs;
CREATE POLICY "anon_crud_traffic_sel" ON traffic_logs FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "anon_crud_traffic_ins" ON traffic_logs;
CREATE POLICY "anon_crud_traffic_ins" ON traffic_logs FOR INSERT TO anon, authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_traffic_upd" ON traffic_logs;
CREATE POLICY "anon_crud_traffic_upd" ON traffic_logs FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "anon_crud_traffic_del" ON traffic_logs;
CREATE POLICY "anon_crud_traffic_del" ON traffic_logs FOR DELETE TO anon, authenticated USING (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_inbounds_protocol ON inbounds(protocol);
CREATE INDEX IF NOT EXISTS idx_clients_uuid ON clients(uuid);
CREATE INDEX IF NOT EXISTS idx_clients_sub_id ON clients(sub_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_sub_id ON subscriptions(sub_id);
CREATE INDEX IF NOT EXISTS idx_traffic_logs_client ON traffic_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_traffic_logs_recorded ON traffic_logs(recorded_at);

-- Seed default settings
INSERT INTO settings (key, value, category) VALUES
  ('panel_name', '"Milijon Railway"', 'panel'),
  ('panel_port', '2095', 'panel'),
  ('panel_domain', '""', 'panel'),
  ('panel_cert_mode', '"none"', 'panel'),
  ('panel_cert_file', '""', 'panel'),
  ('panel_key_file', '""', 'panel'),
  ('session_timeout', '30', 'security'),
  ('enable_2fa', 'false', 'security'),
  ('sub_domain', '""', 'subscription'),
  ('sub_port', '2095', 'subscription'),
  ('sub_encrypt', 'true', 'subscription'),
  ('sub_update_interval', '24', 'subscription'),
  ('tg_bot_token', '""', 'telegram'),
  ('tg_notify_on_create', 'true', 'telegram'),
  ('tg_notify_on_traffic', 'false', 'telegram')
ON CONFLICT (key) DO NOTHING;

-- Seed sample server
INSERT INTO servers (name, address, port, server_type, is_online, cpu_usage, mem_usage, net_usage, version)
VALUES ('Main Server', '185.199.136.42', 2095, 'master', true, 23.5, 41.2, 128.5, '1.8.0')
ON CONFLICT DO NOTHING;