"""
Type stubs for the decky module.
For development reference only — the real module is provided by Decky Loader at runtime.
"""

from typing import Any, Callable

# ── Logging ────────────────────────────────────────────────────────────

class Logger:
    def debug(self, msg: str, *args: Any) -> None: ...
    def info(self, msg: str, *args: Any) -> None: ...
    def warning(self, msg: str, *args: Any) -> None: ...
    def error(self, msg: str, *args: Any) -> None: ...
    def critical(self, msg: str, *args: Any) -> None: ...

logger: Logger

# ── Event emission ─────────────────────────────────────────────────────

async def emit(event_name: str, *args: Any) -> None: ...

# ── Paths ──────────────────────────────────────────────────────────────

DECKY_USER_HOME: str   # ~/.steam/steam (or equivalent)
DECKY_HOME: str        # ~/homebrew
DECKY_PLUGIN_DIR: str  # Plugin's own directory
DECKY_LOG_DIR: str     # Plugin log directory
DECKY_SETTINGS_DIR: str  # Plugin settings directory
DECKY_RUNTIME_DIR: str   # Plugin runtime data directory

# ── Migration helpers ──────────────────────────────────────────────────

def migrate_logs(old_path: str) -> None: ...
def migrate_settings(*old_paths: str) -> None: ...
def migrate_runtime(*old_paths: str) -> None: ...
