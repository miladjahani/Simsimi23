"""
Milijon Railway Panel - Config Link Generator
Generates VLESS, VMess, Trojan, and Shadowsocks config links
for all supported transports (WS, gRPC, H2, TCP).
Produces vmess:// (base64 JSON), vless://, trojan://, ss:// URIs,
plus subscription links and client-specific configs.
"""

import base64
import json
import urllib.parse
from datetime import datetime, timezone


def _b64(s):
    """Base64 encode a string for vmess/ss links."""
    return base64.b64encode(s.encode("utf-8")).decode("utf-8").rstrip("=")


def _safe_b64_decode(s):
    """Safe base64 decode with padding fix."""
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    try:
        return base64.b64decode(s).decode("utf-8")
    except Exception:
        return ""


def generate_vless_link(
    uuid_str,
    host,
    port,
    transport="ws",
    remark="VLESS",
    path="",
    host_header="",
    sni="",
    tls="",
    flow="",
    alpn="",
    fingerprint="",
    service_name="",
    mode="",
):
    """Generate a vless:// link."""
    params = {}
    if transport == "ws":
        params["type"] = "ws"
        if path:
            params["path"] = path
        if host_header:
            params["host"] = host_header
    elif transport == "grpc":
        params["type"] = "grpc"
        if service_name:
            params["serviceName"] = service_name
        if mode:
            params["mode"] = mode
    elif transport == "h2":
        params["type"] = "http"
        if path:
            params["path"] = path
        if host_header:
            params["host"] = host_header
    elif transport == "tcp":
        params["type"] = "tcp"

    if tls:
        params["security"] = tls
        if sni:
            params["sni"] = sni
        if alpn:
            params["alpn"] = alpn
        if fingerprint:
            params["fp"] = fingerprint
    else:
        params["security"] = "none"

    if flow:
        params["flow"] = flow

    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    fragment = urllib.parse.quote(remark)
    return f"vless://{uuid_str}@{host}:{port}?{query}#{fragment}"


def generate_vmess_link(
    uuid_str,
    host,
    port,
    transport="ws",
    remark="VMess",
    aid=0,
    net="ws",
    path="",
    host_header="",
    tls="",
    sni="",
    alpn="",
    service_name="",
    mode="",
):
    """Generate a vmess:// link (base64-encoded JSON)."""
    vmess_config = {
        "v": "2",
        "ps": remark,
        "add": host,
        "port": str(port),
        "id": uuid_str,
        "aid": str(aid),
        "scy": "auto",
        "net": "ws" if transport == "ws" else ("tcp" if transport == "tcp" else ("grpc" if transport == "grpc" else "h2")),
        "type": "none",
        "host": host_header or "",
        "path": path or "/",
        "tls": tls or "",
        "sni": sni or "",
        "alpn": alpn or "",
    }
    if transport == "grpc":
        vmess_config["net"] = "grpc"
        vmess_config["path"] = service_name or ""
        vmess_config["mode"] = mode or "gun"
    elif transport == "h2":
        vmess_config["net"] = "h2"
        vmess_config["path"] = path or "/"
        vmess_config["host"] = host_header or host

    return "vmess://" + _b64(json.dumps(vmess_config, separators=(",", ":")))


def generate_trojan_link(
    password,
    host,
    port,
    transport="ws",
    remark="Trojan",
    path="",
    host_header="",
    sni="",
    alpn="",
    fingerprint="",
    service_name="",
    mode="",
):
    """Generate a trojan:// link."""
    params = {}
    if transport == "ws":
        params["type"] = "ws"
        if path:
            params["path"] = path
        if host_header:
            params["host"] = host_header
    elif transport == "grpc":
        params["type"] = "grpc"
        if service_name:
            params["serviceName"] = service_name
        if mode:
            params["mode"] = mode
    elif transport == "h2":
        params["type"] = "http"
        if path:
            params["path"] = path
        if host_header:
            params["host"] = host_header
    elif transport == "tcp":
        params["type"] = "tcp"

    params["security"] = sni or "tls"
    if sni:
        params["sni"] = sni
    if alpn:
        params["alpn"] = alpn
    if fingerprint:
        params["fp"] = fingerprint

    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    fragment = urllib.parse.quote(remark)
    return f"trojan://{password}@{host}:{port}?{query}#{fragment}"


def generate_ss_link(
    method,
    password,
    host,
    port,
    transport="ws",
    remark="Shadowsocks",
    path="",
    host_header="",
):
    """Generate an ss:// link."""
    userinfo = _b64(f"{method}:{password}")
    params = {}
    if transport == "ws":
        params["plugin"] = "v2ray-plugin"
        if path:
            params["mode"] = "websocket"
            params["path"] = path
            if host_header:
                params["host"] = host_header

    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote) if params else ""
    fragment = urllib.parse.quote(remark)
    if query:
        return f"ss://{userinfo}@{host}:{port}?{query}#{fragment}"
    return f"ss://{userinfo}@{host}:{port}#{fragment}"


def generate_links_for_client(client, inbound, host):
    """Generate the appropriate link for a client+inbound combo."""
    protocol = inbound["protocol"]
    transport = inbound["transport"]
    settings = inbound.get("settings", {})
    if isinstance(settings, str):
        settings = json.loads(settings)

    remark = f"{client.get('email', 'client')}-{inbound.get('tag', '')}"
    port = inbound.get("listen_port", 443)
    path = settings.get("path", "/")
    host_header = settings.get("host", "")
    sni = settings.get("sni", host)
    tls = settings.get("tls", "tls" if transport in ("ws", "grpc", "h2") else "")
    alpn = settings.get("alpn", "")
    fingerprint = settings.get("fp", "chrome")
    service_name = settings.get("serviceName", "")
    mode = settings.get("mode", "gun")
    flow = settings.get("flow", "")

    if protocol == "vless":
        return generate_vless_link(
            client["uuid"],
            host,
            port,
            transport=transport,
            remark=remark,
            path=path,
            host_header=host_header,
            sni=sni,
            tls=tls,
            flow=flow,
            alpn=alpn,
            fingerprint=fingerprint,
            service_name=service_name,
            mode=mode,
        )
    elif protocol == "vmess":
        return generate_vmess_link(
            client["uuid"],
            host,
            port,
            transport=transport,
            remark=remark,
            path=path,
            host_header=host_header,
            tls=tls,
            sni=sni,
            alpn=alpn,
            service_name=service_name,
            mode=mode,
        )
    elif protocol == "trojan":
        password = settings.get("password", client["uuid"])
        return generate_trojan_link(
            password,
            host,
            port,
            transport=transport,
            remark=remark,
            path=path,
            host_header=host_header,
            sni=sni,
            alpn=alpn,
            fingerprint=fingerprint,
            service_name=service_name,
            mode=mode,
        )
    elif protocol == "shadowsocks":
        method = settings.get("method", "aes-256-gcm")
        password = settings.get("password", client["uuid"])
        return generate_ss_link(
            method,
            password,
            host,
            port,
            transport=transport,
            remark=remark,
            path=path,
            host_header=host_header,
        )
    return ""


def generate_subscription_content(client, inbounds, host):
    """Generate base64-encoded subscription content for a client."""
    links = []
    for inbound in inbounds:
        if inbound["id"] in (client.get("inbound_ids") or []):
            link = generate_links_for_client(client, inbound, host)
            if link:
                links.append(link)
    content = "\n".join(links)
    return _b64(content)


def generate_clash_config(client, inbounds, host):
    """Generate a Clash Meta config for the client."""
    proxies = []
    for inbound in inbounds:
        if inbound["id"] not in (client.get("inbound_ids") or []):
            continue
        settings = inbound.get("settings", {})
        if isinstance(settings, str):
            settings = json.loads(settings)
        port = inbound.get("listen_port", 443)
        name = f"{inbound['protocol']}-{inbound['transport']}-{inbound.get('tag', '')}"
        protocol = inbound["protocol"]
        transport = inbound["transport"]

        if protocol == "vless":
            proxy = {
                "name": name,
                "type": "vless",
                "server": host,
                "port": port,
                "uuid": client["uuid"],
                "network": "ws" if transport == "ws" else ("grpc" if transport == "grpc" else "tcp"),
                "tls": transport in ("ws", "grpc", "h2"),
                "udp": True,
            }
            if transport == "ws":
                proxy["ws-opts"] = {"path": settings.get("path", "/"), "headers": {"Host": settings.get("host", host)}}
            elif transport == "grpc":
                proxy["grpc-opts"] = {"grpc-service-name": settings.get("serviceName", "")}
            if settings.get("sni"):
                proxy["servername"] = settings["sni"]
            proxies.append(proxy)
        elif protocol == "vmess":
            proxy = {
                "name": name,
                "type": "vmess",
                "server": host,
                "port": port,
                "uuid": client["uuid"],
                "alterId": 0,
                "cipher": "auto",
                "network": "ws" if transport == "ws" else ("grpc" if transport == "grpc" else "tcp"),
                "tls": transport in ("ws", "grpc", "h2"),
                "udp": True,
            }
            if transport == "ws":
                proxy["ws-opts"] = {"path": settings.get("path", "/"), "headers": {"Host": settings.get("host", host)}}
            elif transport == "grpc":
                proxy["grpc-opts"] = {"grpc-service-name": settings.get("serviceName", "")}
            proxies.append(proxy)
        elif protocol == "trojan":
            proxy = {
                "name": name,
                "type": "trojan",
                "server": host,
                "port": port,
                "password": settings.get("password", client["uuid"]),
                "sni": settings.get("sni", host),
                "udp": True,
            }
            if transport == "ws":
                proxy["network"] = "ws"
                proxy["ws-opts"] = {"path": settings.get("path", "/"), "headers": {"Host": settings.get("host", host)}}
            elif transport == "grpc":
                proxy["network"] = "grpc"
                proxy["grpc-opts"] = {"grpc-service-name": settings.get("serviceName", "")}
            proxies.append(proxy)
        elif protocol == "shadowsocks":
            proxy = {
                "name": name,
                "type": "ss",
                "server": host,
                "port": port,
                "cipher": settings.get("method", "aes-256-gcm"),
                "password": settings.get("password", client["uuid"]),
                "udp": True,
            }
            proxies.append(proxy)

    proxy_names = [p["name"] for p in proxies]
    config = {
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "PROXY",
                "type": "select",
                "proxies": proxy_names + ["DIRECT"],
            }
        ],
        "rules": [
            "GEOIP,CN,DIRECT",
            "MATCH,PROXY",
        ],
    }
    return json.dumps(config, indent=2, ensure_ascii=False)


def generate_singbox_config(client, inbounds, host):
    """Generate a sing-box config for the client."""
    outbounds = []
    for inbound in inbounds:
        if inbound["id"] not in (client.get("inbound_ids") or []):
            continue
        settings = inbound.get("settings", {})
        if isinstance(settings, str):
            settings = json.loads(settings)
        port = inbound.get("listen_port", 443)
        protocol = inbound["protocol"]
        transport = inbound["transport"]
        tag = f"{protocol}-{transport}-{inbound.get('tag', '')}"

        if protocol == "vless":
            ob = {
                "type": "vless",
                "tag": tag,
                "server": host,
                "server_port": port,
                "uuid": client["uuid"],
                "tls": {"enabled": transport in ("ws", "grpc", "h2"), "server_name": settings.get("sni", host)},
            }
            if transport == "ws":
                ob["transport"] = {"type": "ws", "path": settings.get("path", "/"), "headers": {"Host": settings.get("host", host)}}
            elif transport == "grpc":
                ob["transport"] = {"type": "grpc", "service_name": settings.get("serviceName", "")}
        elif protocol == "vmess":
            ob = {
                "type": "vmess",
                "tag": tag,
                "server": host,
                "server_port": port,
                "uuid": client["uuid"],
                "security": "auto",
                "alter_id": 0,
                "tls": {"enabled": transport in ("ws", "grpc", "h2"), "server_name": settings.get("sni", host)},
            }
            if transport == "ws":
                ob["transport"] = {"type": "ws", "path": settings.get("path", "/"), "headers": {"Host": settings.get("host", host)}}
            elif transport == "grpc":
                ob["transport"] = {"type": "grpc", "service_name": settings.get("serviceName", "")}
        elif protocol == "trojan":
            ob = {
                "type": "trojan",
                "tag": tag,
                "server": host,
                "server_port": port,
                "password": settings.get("password", client["uuid"]),
                "tls": {"enabled": True, "server_name": settings.get("sni", host)},
            }
            if transport == "ws":
                ob["transport"] = {"type": "ws", "path": settings.get("path", "/"), "headers": {"Host": settings.get("host", host)}}
            elif transport == "grpc":
                ob["transport"] = {"type": "grpc", "service_name": settings.get("serviceName", "")}
        elif protocol == "shadowsocks":
            ob = {
                "type": "shadowsocks",
                "tag": tag,
                "server": host,
                "server_port": port,
                "method": settings.get("method", "aes-256-gcm"),
                "password": settings.get("password", client["uuid"]),
            }
        outbounds.append(ob)

    outbounds.append({"type": "direct", "tag": "direct"})
    outbounds.append({"type": "dns", "tag": "dns-out"})
    outbounds.insert(0, {"type": "selector", "tag": "PROXY", "outbounds": [o["tag"] for o in outbounds if o["type"] not in ("direct", "dns")] + ["direct"], "default": outbounds[0]["tag"] if outbounds else "direct"})

    config = {
        "outbounds": outbounds,
        "route": {
            "rules": [
                {"protocol": "dns", "outbound": "dns-out"},
                {"geoip": ["cn"], "outbound": "direct"},
            ],
            "final": "PROXY",
        },
    }
    return json.dumps(config, indent=2, ensure_ascii=False)
