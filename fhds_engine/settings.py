"""
Settings management for FHDS Decky plugin.
Stores configuration in decky's settings directory.
"""

import json
import os
import logging

log = logging.getLogger("fhds.settings")

DEFAULTS = {
    # ── UDP ──────────────────────────────────────────────────────────
    "udp_host": "127.0.0.1",
    "udp_port": 5300,

    # ── Controller ───────────────────────────────────────────────────
    "reconnect_interval": 2.0,
    "input_idle_timeout": 5.0,

    # ── Effects: Brake (left trigger) ────────────────────────────────
    "brake_enabled": True,
    "brake_max_force": 180,
    "brake_curve": 2.0,
    "brake_min_force": 10,
    "abs_enabled": True,
    "abs_frequency": 28,
    "abs_amplitude": 90,
    "handbrake_force": 200,

    # ── Effects: Throttle (right trigger) ────────────────────────────
    "throttle_enabled": True,
    "throttle_max_force": 130,
    "throttle_curve": 1.8,
    "throttle_min_force": 5,
    "gear_shift_enabled": True,
    "gear_shift_amplitude": 180,
    "gear_shift_duration_ms": 80,
    "rev_limiter_enabled": True,
    "rev_limiter_frequency": 28,
    "rev_limiter_amplitude": 100,
    "rev_limiter_threshold": 0.92,
}

_SETTINGS: dict = {}
_file: str | None = None


def _file_path() -> str:
    """Persistent settings path — survives plugin updates and sleep."""
    global _file
    if _file:
        return _file
    _file = os.path.join(os.path.expanduser("~"), ".config", "fhds-decky", "settings.json")
    return _file


def load_or_default():
    """Load settings from file, falling back to defaults."""
    global _SETTINGS
    _SETTINGS = dict(DEFAULTS)
    path = _file_path()
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                loaded = json.load(f)
            _SETTINGS.update(loaded)
            log.info("Settings loaded from %s", path)
    except Exception as e:
        log.warning("Could not load settings (%s), using defaults", e)


def save():
    """Write current settings to file."""
    path = _file_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(_SETTINGS, f, indent=2)
    log.info("Settings saved to %s", path)


def reset():
    """Reset all settings to defaults."""
    global _SETTINGS
    _SETTINGS = dict(DEFAULTS)


def get(key: str, default=None):
    """Get a setting value, with optional fallback."""
    val = _SETTINGS.get(key, DEFAULTS.get(key))
    return val if val is not None else default


def set(key: str, value):
    """Set a single setting."""
    _SETTINGS[key] = value


def to_dict() -> dict:
    """Return all settings as a dict."""
    return dict(_SETTINGS)
