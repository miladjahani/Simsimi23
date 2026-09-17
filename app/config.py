"""
Milijon Railway Panel - Configuration
Centralized configuration for the panel, database, and deployment.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "milijon-railway-secret-2024")

    # Supabase
    SUPABASE_URL = os.environ.get("SUPABASE_URL", os.environ.get("VITE_SUPABASE_URL", ""))
    SUPABASE_ANON_KEY = os.environ.get(
        "SUPABASE_ANON_KEY", os.environ.get("VITE_SUPABASE_ANON_KEY", "")
    )
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL", "")

    # Panel
    PANEL_NAME = "Milijon Railway"
    PANEL_VERSION = "3.0.0"
    PANEL_PORT = int(os.environ.get("PORT", 2095))

    # Supported protocols and transports
    PROTOCOLS = ["vless", "vmess", "trojan", "shadowsocks"]
    TRANSPORTS = ["ws", "grpc", "h2", "tcp"]

    # Protocol + Transport combinations
    PROTOCOL_TRANSPORTS = [
        {"protocol": "vless", "transport": "ws", "name": "VLESS + WebSocket"},
        {"protocol": "vmess", "transport": "ws", "name": "VMess + WebSocket"},
        {"protocol": "trojan", "transport": "ws", "name": "Trojan + WebSocket"},
        {
            "protocol": "shadowsocks",
            "transport": "ws",
            "name": "Shadowsocks + v2ray-plugin (WebSocket)",
        },
        {"protocol": "vless", "transport": "grpc", "name": "VLESS + gRPC"},
        {"protocol": "vmess", "transport": "grpc", "name": "VMess + gRPC"},
        {"protocol": "trojan", "transport": "grpc", "name": "Trojan + gRPC"},
        {"protocol": "vless", "transport": "h2", "name": "VLESS + HTTP/2 (H2)"},
        {"protocol": "vmess", "transport": "h2", "name": "VMess + HTTP/2 (H2)"},
        {"protocol": "shadowsocks", "transport": "tcp", "name": "Shadowsocks + TCP"},
        {"protocol": "trojan", "transport": "tcp", "name": "Trojan + TCP"},
        {"protocol": "vless", "transport": "tcp", "name": "VLESS + TCP"},
    ]

    # Supported clients
    SUPPORTED_CLIENTS = [
        {"id": "v2rayng", "name": "v2rayNG", "platform": "Android", "icon": "android"},
        {"id": "v2rayn", "name": "v2rayN", "platform": "Windows", "icon": "windows"},
        {"id": "v2rayl", "name": "V2RayU", "platform": "macOS", "icon": "apple"},
        {"id": "shadowrocket", "name": "Shadowrocket", "platform": "iOS", "icon": "ios"},
        {"id": "nekobox", "name": "NekoBox", "platform": "Android", "icon": "cat"},
        {
            "id": "nekoboxplus",
            "name": "NekoBoxPlus",
            "platform": "Android",
            "icon": "cat-plus",
        },
        {"id": "exclave", "name": "Exclave", "platform": "iOS", "icon": "shield"},
        {"id": "clash", "name": "Clash Meta", "platform": "Cross", "icon": "clash"},
        {"id": "singbox", "name": "sing-box", "platform": "Cross", "icon": "box"},
        {"id": "hiddify", "name": "Hiddify", "platform": "Cross", "icon": "ghost"},
        {"id": "streisand", "name": "Streisand", "platform": "iOS", "icon": "music"},
        {"id": "v2raytun", "name": "V2RayTun", "platform": "iOS", "icon": "tunnel"},
    ]

    # Network security
    TLS_VERSIONS = ["1.0", "1.1", "1.2", "1.3"]
    CIPHER_SUITES = [
        "TLS_AES_128_GCM_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
    ]

    # Fallbacks
    ALLOW_NONE = True
