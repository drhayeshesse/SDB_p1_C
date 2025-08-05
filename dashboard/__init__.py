# Dashboard Module
# Web interface and API for smoke detection system

# dashboard/__init__.py
"""
Dashboard package initialization.
Only exports blueprints for use in dashboard.app.
"""

from .routes import home, api, metrics, events, settings as settings_routes, stream

__all__ = [
    "home",
    "api",
    "metrics",
    "events",
    "settings_routes",
    "stream",
]