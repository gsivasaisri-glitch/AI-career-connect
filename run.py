"""
run.py — Application Entry Point
=================================
This is the single file you execute to start the server.
It imports the application factory, creates the app instance,
and runs the Flask development server.

Usage:
    python run.py          # defaults to development
    FLASK_ENV=prod python run.py
"""

import os
from app import create_app

env = os.getenv("FLASK_ENV", "dev")
app = create_app(env)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", True))