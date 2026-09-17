"""
Milijon Railway Panel - Proxy Engine
Manages inbound configurations, protocol settings, and transport parameters.
Generates default settings for each protocol+transport combination.
"""

import json
import uuid
from copy import deepcopy


PROTOCOL_DEFAULTS = {
    "vless": {
        "decryption": "none",
        "fallback": None,
    },
    "vmess": {
        "alterId": 0,
        "security": "auto",
    },
    "trojan": {
        "fallbackPort": 443,
        "fallbacks": [],
    },
    "shadowsocks": {
        "method": "aes-256-gcm",
        "network": "tcp,udp",
    },
}

TRANSPORT_DEFAULTS = {
    "ws": {
        "path": "/milijon-ws",
        "host": "",
        "headers": {},
    },
    "grpc": {
        "serviceName": "milijon-grpc",
        "multiMode": False,
        "mode": "gun",
    },
    "h2": {
        "path": "/milijon-h2",
        "host": "",
        "readBufferSize": 0,
        "writeBufferSize": 0,
    },
    "tcp": {
        "acceptProxyProtocol": False,
        "header": {"type": "none"},
    },
}

TLS_DEFAULTS = {
    "enabled": True,
    "serverName": "",
    "minVersion": "1.2",
    "maxVersion": "1.3",
    "cipherSuites": [],
    "rejectUnknownSNI": False,
    "certificates": [],
}

PROTOCOL_INFO = {
    "vless": {
        "name": "VLESS",
        "description": "Lightweight protocol without encryption, relies on TLS. Best for performance.",
        "security": "TLS-based",
        "speed": "Fast",
        "recommended": True,
    },
    "vmess": {
        "name": "VMess",
        "description": "Encrypted protocol with built-in authentication. Widely supported.",
        "security": "AES-128-GCM",
        "speed": "Fast",
        "recommended": True,
    },
    "trojan": {
        "name": "Trojan",
        "description": "Disguises traffic as HTTPS. Very hard to detect.",
        "security": "TLS + Password",
        "speed": "Fast",
        "recommended": True,
    },
    "shadowsocks": {
        "name": "Shadowsocks",
        "description": "Lightweight encrypted proxy. Simple and effective.",
        "security": "AEAD Ciphers",
        "speed": "Very Fast",
        "recommended": True,
    },
}

TRANSPORT_INFO = {
    "ws": {
        "name": "WebSocket",
        "description": "WebSocket transport. Works well with CDN and reverse proxies.",
        "cdn": True,
        "recommended": True,
    },
    "grpc": {
        "name": "gRPC",
        "description": "gRPC transport. High performance, multiplexed streams.",
        "cdn": False,
        "recommended": True,
    },
    "h2": {
        "name": "HTTP/2",
        "description": "HTTP/2 transport. Requires TLS. Good for high-throughput.",
        "cdn": True,
        "recommended": False,
    },
    "tcp": {
        "name": "TCP",
        "description": "Raw TCP transport. Simplest, lowest overhead.",
        "cdn": False,
        "recommended": False,
    },
}


def get_protocol_defaults(protocol):
    """Get default settings for a protocol."""
    return deepcopy(PROTOCOL_DEFAULTS.get(protocol, {}))


def get_transport_defaults(transport):
    """Get default settings for a transport."""
    return deepcopy(TRANSPORT_DEFAULTS.get(transport, {}))


def get_tls_defaults():
    """Get default TLS settings."""
    return deepcopy(TLS_DEFAULTS)


def generate_inbound_settings(protocol, transport, custom=None):
    """
    Generate complete settings JSON for an inbound.
    Combines protocol defaults, transport defaults, TLS, and custom overrides.
    """
    settings = {}
    settings.update(get_protocol_defaults(protocol))
    settings.update(get_transport_defaults(transport))

    # TLS for transports that need it
    if transport in ("ws", "grpc", "h2"):
        settings["tls"] = "tls"
        settings["sni"] = ""
        settings["alpn"] = "h2,http/1.1"
        settings["fp"] = "chrome"
    else:
        settings["tls"] = ""

    # Protocol-specific
    if protocol == "vless":
        settings["decryption"] = "none"
        if transport == "tcp":
            settings["flow"] = "xtls-rprx-vision"
    elif protocol == "vmess":
        settings["alterId"] = 0
        settings["security"] = "auto"
    elif protocol == "trojan":
        settings["password"] = uuid.uuid4().hex
    elif protocol == "shadowsocks":
        settings["method"] = "aes-256-gcm"
        settings["password"] = uuid.uuid4().hex[:16]

    # Apply custom overrides
    if custom:
        settings.update(custom)

    return settings


def get_protocol_info():
    """Get info about all protocols."""
    return PROTOCOL_INFO


def get_transport_info():
    """Get info about all transports."""
    return TRANSPORT_INFO


def get_all_combinations():
    """Get all supported protocol+transport combinations."""
    combos = []
    for protocol in ["vless", "vmess", "trojan", "shadowsocks"]:
        for transport in ["ws", "grpc", "h2", "tcp"]:
            combo = {
                "protocol": protocol,
                "transport": transport,
                "name": f"{PROTOCOL_INFO[protocol]['name']} + {TRANSPORT_INFO[transport]['name']}",
                "protocol_info": PROTOCOL_INFO[protocol],
                "transport_info": TRANSPORT_INFO[transport],
                "settings": generate_inbound_settings(protocol, transport),
            }
            combos.append(combo)
    return combos


def validate_settings(protocol, transport, settings):
    """Validate inbound settings. Returns (is_valid, errors)."""
    errors = []
    if protocol not in PROTOCOL_DEFAULTS:
        errors.append(f"Unsupported protocol: {protocol}")
    if transport not in TRANSPORT_DEFAULTS:
        errors.append(f"Unsupported transport: {transport}")

    if protocol == "shadowsocks":
        method = settings.get("method", "")
        valid_methods = [
            "aes-256-gcm",
            "aes-128-gcm",
            "chacha20-ietf-poly1305",
            "2022-blake3-aes-256-gcm",
            "2022-blake3-aes-128-gcm",
            "2022-blake3-chacha20-poly1305",
            "none",
        ]
        if method and method not in valid_methods:
            errors.append(f"Invalid cipher method: {method}")

    if transport in ("ws", "h2") and not settings.get("path"):
        errors.append(f"Path is required for {transport} transport")

    if transport == "grpc" and not settings.get("serviceName"):
        errors.append("Service name is required for gRPC transport")

    return len(errors) == 0, errors
