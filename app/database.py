"""
Milijon Railway Panel - Database Layer
Handles all Supabase/PostgreSQL operations.
Uses the Supabase REST API via the anon key for all CRUD operations.
"""

import json
import uuid
from datetime import datetime, timedelta, timezone

from flask import current_app, g

try:
    from supabase import create_client, Client
except ImportError:
    Client = None
    create_client = None


class Database:
    """Wrapper around Supabase client for panel operations."""

    def __init__(self):
        self.client = None

    def init_app(self, app):
        url = app.config["SUPABASE_URL"]
        key = app.config["SUPABASE_ANON_KEY"]
        if create_client and url and key:
            self.client = create_client(url, key)
        else:
            app.logger.warning("Supabase client not initialized - missing credentials")

    def _table(self, name):
        if self.client is None:
            raise RuntimeError("Database not initialized")
        return self.client.table(name)

    # --- Inbounds ---

    def get_inbounds(self, protocol=None, transport=None):
        q = self._table("inbounds").select("*").order("created_at", desc=False)
        if protocol:
            q = q.eq("protocol", protocol)
        if transport:
            q = q.eq("transport", transport)
        res = q.execute()
        return res.data

    def get_inbound(self, inbound_id):
        res = self._table("inbounds").select("*").eq("id", inbound_id).execute()
        return res.data[0] if res.data else None

    def create_inbound(self, data):
        data["id"] = str(uuid.uuid4())
        res = self._table("inbounds").insert(data).execute()
        return res.data[0] if res.data else None

    def update_inbound(self, inbound_id, data):
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = self._table("inbounds").update(data).eq("id", inbound_id).execute()
        return res.data[0] if res.data else None

    def delete_inbound(self, inbound_id):
        self._table("inbounds").delete().eq("id", inbound_id).execute()

    # --- Clients ---

    def get_clients(self, active_only=False):
        q = self._table("clients").select("*").order("created_at", desc=True)
        if active_only:
            q = q.eq("enable", True)
        res = q.execute()
        return res.data

    def get_client(self, client_id):
        res = self._table("clients").select("*").eq("id", client_id).execute()
        return res.data[0] if res.data else None

    def get_client_by_uuid(self, client_uuid):
        res = self._table("clients").select("*").eq("uuid", client_uuid).execute()
        return res.data[0] if res.data else None

    def create_client(self, data):
        data["id"] = str(uuid.uuid4())
        data["uuid"] = str(uuid.uuid4())
        data["sub_id"] = uuid.uuid4().hex[:16]
        if data.get("expiry_days") and data["expiry_days"] > 0:
            data["expiry_date"] = (
                datetime.now(timezone.utc) + timedelta(days=data["expiry_days"])
            ).isoformat()
        res = self._table("clients").insert(data).execute()
        client = res.data[0] if res.data else None

        if client:
            self._table("subscriptions").insert(
                {
                    "sub_id": client["sub_id"],
                    "client_id": client["id"],
                    "name": client["email"],
                }
            ).execute()
        return client

    def update_client(self, client_id, data):
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        if data.get("expiry_days") and data["expiry_days"] > 0:
            data["expiry_date"] = (
                datetime.now(timezone.utc) + timedelta(days=data["expiry_days"])
            ).isoformat()
        res = self._table("clients").update(data).eq("id", client_id).execute()
        return res.data[0] if res.data else None

    def delete_client(self, client_id):
        self._table("clients").delete().eq("id", client_id).execute()

    def reset_client_traffic(self, client_id):
        self._table("clients").update({"used_gb": 0}).eq("id", client_id).execute()

    # --- Subscriptions ---

    def get_subscriptions(self):
        res = (
            self._table("subscriptions")
            .select("*, clients(*)")
            .order("created_at", desc=True)
            .execute()
        )
        return res.data

    def get_subscription(self, sub_id):
        res = (
            self._table("subscriptions")
            .select("*, clients(*)")
            .eq("sub_id", sub_id)
            .execute()
        )
        return res.data[0] if res.data else None

    def update_subscription_check(self, sub_id):
        self._table("subscriptions").update(
            {
                "last_check": datetime.now(timezone.utc).isoformat(),
                "update_count": 1,
            }
        ).eq("sub_id", sub_id).execute()

    # --- Servers ---

    def get_servers(self):
        res = self._table("servers").select("*").order("created_at", desc=False).execute()
        return res.data

    def get_server(self, server_id):
        res = self._table("servers").select("*").eq("id", server_id).execute()
        return res.data[0] if res.data else None

    def create_server(self, data):
        data["id"] = str(uuid.uuid4())
        res = self._table("servers").insert(data).execute()
        return res.data[0] if res.data else None

    def update_server(self, server_id, data):
        res = self._table("servers").update(data).eq("id", server_id).execute()
        return res.data[0] if res.data else None

    def delete_server(self, server_id):
        self._table("servers").delete().eq("id", server_id).execute()

    # --- Settings ---

    def get_settings(self, category=None):
        q = self._table("settings").select("*")
        if category:
            q = q.eq("category", category)
        res = q.execute()
        return {s["key"]: s["value"] for s in res.data}

    def get_setting(self, key):
        res = self._table("settings").select("*").eq("key", key).execute()
        return res.data[0]["value"] if res.data else None

    def set_setting(self, key, value, category="panel"):
        existing = self._table("settings").select("*").eq("key", key).execute()
        if existing.data:
            self._table("settings").update(
                {"value": json.dumps(value), "updated_at": datetime.now(timezone.utc).isoformat()}
            ).eq("key", key).execute()
        else:
            self._table("settings").insert(
                {
                    "id": str(uuid.uuid4()),
                    "key": key,
                    "value": json.dumps(value),
                    "category": category,
                }
            ).execute()

    # --- Traffic Logs ---

    def get_traffic_logs(self, client_id=None, limit=100):
        q = self._table("traffic_logs").select("*, clients(email), inbounds(tag)").order(
            "recorded_at", desc=True
        ).limit(limit)
        if client_id:
            q = q.eq("client_id", client_id)
        res = q.execute()
        return res.data

    def add_traffic_log(self, data):
        data["id"] = str(uuid.uuid4())
        self._table("traffic_logs").insert(data).execute()

    # --- Stats ---

    def get_stats(self):
        inbounds = self.get_inbounds()
        clients = self.get_clients()
        servers = self.get_servers()
        active_clients = [c for c in clients if c.get("enable")]
        total_used = sum(c.get("used_gb", 0) for c in clients)
        total_limit = sum(c.get("total_gb", 0) for c in clients if c.get("total_gb", 0) > 0)
        online_servers = [s for s in servers if s.get("is_online")]

        return {
            "total_inbounds": len(inbounds),
            "active_inbounds": len([i for i in inbounds if i.get("is_active")]),
            "total_clients": len(clients),
            "active_clients": len(active_clients),
            "total_servers": len(servers),
            "online_servers": len(online_servers),
            "total_used_gb": total_used,
            "total_limit_gb": total_limit,
        }


db = Database()
