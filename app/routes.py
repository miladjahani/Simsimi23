"""
Milijon Railway Panel - Route Registration
All Flask routes for the panel: dashboard, inbounds, clients, subscriptions,
settings, servers, status page, and API endpoints.
"""

import json
import os
import uuid
from datetime import datetime, timezone

from flask import (
    Blueprint,
    Flask,
    Response,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from app.config import Config
from app.database import db
from app.generator import (
    generate_clash_config,
    generate_links_for_client,
    generate_singbox_config,
    generate_subscription_content,
)
from app.proxy_engine import (
    generate_inbound_settings,
    get_all_combinations,
    get_protocol_info,
    get_transport_info,
)


def register_routes(app: Flask):
    @app.context_processor
    def inject_globals():
        return {
            "panel_name": "Milijon Railway",
            "panel_version": Config.PANEL_VERSION,
            "protocols": Config.PROTOCOLS,
            "transports": Config.TRANSPORTS,
            "protocol_transports": Config.PROTOCOL_TRANSPORTS,
            "supported_clients": Config.SUPPORTED_CLIENTS,
        }

    # --- Pages ---

    @app.route("/")
    def dashboard():
        stats = db.get_stats()
        inbounds = db.get_inbounds()
        clients = db.get_clients()
        servers = db.get_servers()
        traffic = db.get_traffic_logs(limit=20)
        return render_template(
            "dashboard.html",
            stats=stats,
            inbounds=inbounds,
            clients=clients,
            servers=servers,
            traffic=traffic,
            active_page="dashboard",
        )

    @app.route("/inbounds")
    def inbounds_page():
        protocol = request.args.get("protocol")
        transport = request.args.get("transport")
        inbounds = db.get_inbounds(protocol=protocol, transport=transport)
        combos = get_all_combinations()
        return render_template(
            "inbounds.html",
            inbounds=inbounds,
            combos=combos,
            protocol_info=get_protocol_info(),
            transport_info=get_transport_info(),
            active_page="inbounds",
        )

    @app.route("/clients")
    def clients_page():
        clients = db.get_clients()
        inbounds = db.get_inbounds()
        return render_template(
            "clients.html",
            clients=clients,
            inbounds=inbounds,
            active_page="clients",
        )

    @app.route("/subscriptions")
    def subscriptions_page():
        subs = db.get_subscriptions()
        settings = db.get_settings(category="subscription")
        return render_template(
            "subscriptions.html",
            subs=subs,
            settings=settings,
            active_page="subscriptions",
        )

    @app.route("/servers")
    def servers_page():
        servers = db.get_servers()
        return render_template(
            "servers.html",
            servers=servers,
            active_page="servers",
        )

    @app.route("/settings")
    def settings_page():
        settings = db.get_settings()
        return render_template(
            "settings.html",
            settings=settings,
            active_page="settings",
        )

    @app.route("/status")
    def status_page():
        servers = db.get_servers()
        inbounds = db.get_inbounds()
        return render_template(
            "status.html",
            servers=servers,
            inbounds=inbounds,
            active_page="status",
        )

    # --- Inbounds API ---

    @app.route("/api/inbounds", methods=["POST"])
    def create_inbound():
        data = request.json
        protocol = data.get("protocol")
        transport = data.get("transport")
        tag = data.get("tag", f"{protocol}-{transport}")
        listen_ip = data.get("listen_ip", "0.0.0.0")
        listen_port = data.get("listen_port", 443)
        custom_settings = data.get("settings", {})
        settings = generate_inbound_settings(protocol, transport, custom_settings)
        inbound = db.create_inbound(
            {
                "tag": tag,
                "protocol": protocol,
                "transport": transport,
                "listen_ip": listen_ip,
                "listen_port": listen_port,
                "settings": json.dumps(settings),
                "is_active": True,
            }
        )
        return jsonify(inbound), 201

    @app.route("/api/inbounds/<inbound_id>", methods=["PUT"])
    def update_inbound(inbound_id):
        data = request.json
        update = {}
        for k in ("tag", "listen_ip", "listen_port", "is_active"):
            if k in data:
                update[k] = data[k]
        if "settings" in data:
            update["settings"] = json.dumps(data["settings"])
        inbound = db.update_inbound(inbound_id, update)
        return jsonify(inbound)

    @app.route("/api/inbounds/<inbound_id>", methods=["DELETE"])
    def delete_inbound(inbound_id):
        db.delete_inbound(inbound_id)
        return jsonify({"ok": True})

    # --- Clients API ---

    @app.route("/api/clients", methods=["POST"])
    def create_client():
        data = request.json
        client = db.create_client(
            {
                "email": data.get("email", ""),
                "inbound_ids": data.get("inbound_ids", []),
                "enable": data.get("enable", True),
                "total_gb": data.get("total_gb", 0),
                "used_gb": 0,
                "expiry_days": data.get("expiry_days", 0),
                "tg_id": data.get("tg_id", ""),
            }
        )
        return jsonify(client), 201

    @app.route("/api/clients/<client_id>", methods=["PUT"])
    def update_client(client_id):
        data = request.json
        update = {}
        for k in ("email", "inbound_ids", "enable", "total_gb", "expiry_days", "tg_id"):
            if k in data:
                update[k] = data[k]
        client = db.update_client(client_id, update)
        return jsonify(client)

    @app.route("/api/clients/<client_id>", methods=["DELETE"])
    def delete_client(client_id):
        db.delete_client(client_id)
        return jsonify({"ok": True})

    @app.route("/api/clients/<client_id>/reset", methods=["POST"])
    def reset_client_traffic(client_id):
        db.reset_client_traffic(client_id)
        return jsonify({"ok": True})

    @app.route("/api/clients/<client_id>/links")
    def get_client_links(client_id):
        client = db.get_client(client_id)
        if not client:
            abort(404)
        inbounds = db.get_inbounds()
        host = request.host_url.rstrip("/").split("://")[-1].split(":")[0]
        links = []
        for inbound in inbounds:
            if inbound["id"] in (client.get("inbound_ids") or []):
                link = generate_links_for_client(client, inbound, host)
                links.append({"inbound": inbound, "link": link})
        return jsonify({"client": client, "links": links})

    # --- Subscriptions ---

    @app.route("/sub/<sub_id>")
    def subscription(sub_id):
        sub = db.get_subscription(sub_id)
        if not sub:
            abort(404)
        client = sub.get("clients")
        if not client:
            abort(404)
        db.update_subscription_check(sub_id)
        inbounds = db.get_inbounds()
        host = request.host_url.rstrip("/").split("://")[-1].split(":")[0]
        content = generate_subscription_content(client, inbounds, host)
        return Response(content, mimetype="text/plain")

    @app.route("/sub/<sub_id>/clash")
    def subscription_clash(sub_id):
        sub = db.get_subscription(sub_id)
        if not sub:
            abort(404)
        client = sub.get("clients")
        if not client:
            abort(404)
        inbounds = db.get_inbounds()
        host = request.host_url.rstrip("/").split("://")[-1].split(":")[0]
        config = generate_clash_config(client, inbounds, host)
        return Response(
            config,
            mimetype="text/yaml",
            headers={"Content-Disposition": "attachment; filename=config.yaml"},
        )

    @app.route("/sub/<sub_id>/singbox")
    def subscription_singbox(sub_id):
        sub = db.get_subscription(sub_id)
        if not sub:
            abort(404)
        client = sub.get("clients")
        if not client:
            abort(404)
        inbounds = db.get_inbounds()
        host = request.host_url.rstrip("/").split("://")[-1].split(":")[0]
        config = generate_singbox_config(client, inbounds, host)
        return Response(
            config,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=config.json"},
        )

    # --- Servers API ---

    @app.route("/api/servers", methods=["POST"])
    def create_server():
        data = request.json
        server = db.create_server(
            {
                "name": data.get("name", ""),
                "address": data.get("address", ""),
                "port": data.get("port", 443),
                "server_type": data.get("server_type", "worker"),
                "is_online": True,
                "cpu_usage": 0,
                "mem_usage": 0,
                "net_usage": 0,
                "version": data.get("version", "1.0.0"),
            }
        )
        return jsonify(server), 201

    @app.route("/api/servers/<server_id>", methods=["PUT"])
    def update_server(server_id):
        data = request.json
        server = db.update_server(server_id, data)
        return jsonify(server)

    @app.route("/api/servers/<server_id>", methods=["DELETE"])
    def delete_server(server_id):
        db.delete_server(server_id)
        return jsonify({"ok": True})

    # --- Settings API ---

    @app.route("/api/settings", methods=["PUT"])
    def update_settings():
        data = request.json
        for key, value in data.items():
            category = "panel"
            if key.startswith("sub_"):
                category = "subscription"
            elif key.startswith("tg_"):
                category = "telegram"
            elif key.startswith("session_") or key.startswith("enable_"):
                category = "security"
            db.set_setting(key, value, category)
        return jsonify({"ok": True})

    # --- Status API ---

    @app.route("/api/status")
    def api_status():
        servers = db.get_servers()
        inbounds = db.get_inbounds()
        return jsonify(
            {
                "servers": [
                    {
                        "name": s["name"],
                        "address": s["address"],
                        "port": s["port"],
                        "online": s["is_online"],
                        "cpu": s["cpu_usage"],
                        "mem": s["mem_usage"],
                        "net": s["net_usage"],
                        "version": s["version"],
                    }
                    for s in servers
                ],
                "inbounds": [
                    {
                        "tag": i["tag"],
                        "protocol": i["protocol"],
                        "transport": i["transport"],
                        "active": i["is_active"],
                    }
                    for i in inbounds
                ],
            }
        )
