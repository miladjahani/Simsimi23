"""
Milijon Railway - VPN/Proxy Management Panel
Entry point for the Flask application.
Designed for Railway deployment.
"""

import os
import sys
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 2095))
    app.run(host="0.0.0.0", port=port, debug=False)
