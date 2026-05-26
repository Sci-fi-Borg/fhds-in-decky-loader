"""
FHDS Decky Plugin - Main entry point.
Forza Horizon DualSense adaptive trigger effects for Steam Deck.
"""

import os
import asyncio
import logging

# Decky plugin module
import decky

_paused = False  # global pause flag for trigger writes

# ---------------------------------------------------------------------------
# Plugin lifecycle — Decky calls these methods on load / unload / uninstall
# ---------------------------------------------------------------------------

class Plugin:
    """FHDS Trigger Effects — Decky plugin backend."""

    # ── state ──────────────────────────────────────────────────────────
    engine_task: asyncio.Task | None = None
    loop: asyncio.AbstractEventLoop | None = None

    # ── public API (callable from TypeScript via @decky/api) ───────────

    async def get_status(self) -> dict:
        """Return current engine status for the frontend."""
        return {
            "running": self.engine_task is not None and not self.engine_task.done(),
            "controller_connected": False,  # updated by engine
            "udp_receiving": False,         # updated by engine
            "error": None,
        }

    async def add(self, left: int, right: int) -> int:
        decky.logger.info(f"[FHDS] add({left}, {right})")
        return left + right

    async def ping(self, _: str = "") -> str:
        decky.logger.info("[FHDS] ping received")
        return "pong"

    async def get_settings(self) -> dict:
        """Return current settings."""
        decky.logger.info("[FHDS] get_settings called")
        try:
            from fhds_engine import settings
            return settings.to_dict()
        except Exception:
            return {}

    async def pause_writes(self, *args, **kwargs):
        """Toggle trigger writes on/off for testing."""
        # Accept {pause: bool}, (bool,), or pause=True
        val = False
        if args and isinstance(args[0], dict):
            val = args[0].get("pause", False)
        elif args:
            val = bool(args[0])
        elif "pause" in kwargs:
            val = kwargs["pause"]
        decky.logger.info(f"[FHDS] pause_writes = {val}")
        global _paused
        _paused = val
        if val and hasattr(self, '_manager') and self._manager and self._manager.connected:
            # Clear with M_OFF=0x00 (neutral, not reset)
            self._manager.set_triggers((0x00, [0]*10), (0x00, [0]*10))
            decky.logger.info("[FHDS] Triggers cleared")

    async def update_setting(self, *args, **kwargs) -> bool:
        """Update a single setting. Accepts (key, value) or {key, value} dict."""
        key = ""
        value = None
        # Try keyword args: update_setting(key="x", value=1)
        if "key" in kwargs:
            key = kwargs["key"]
            value = kwargs["value"] if "value" in kwargs else kwargs.get("key")
        # Try positional: update_setting("x", 1)
        elif len(args) >= 1:
            key = str(args[0])
            value = args[1] if len(args) >= 2 else None
        # Try single dict: update_setting({"key": "x", "value": 1})
        if not key and len(args) == 1 and isinstance(args[0], dict):
            key = args[0].get("key", "")
            value = args[0].get("value")
        if not key:
            decky.logger.error(f"[FHDS] update_setting called with unknown signature: args={args} kwargs={kwargs}")
            return False
        try:
            from fhds_engine import settings
            settings.set(key, value)
            settings.save()
            decky.logger.info(f"[FHDS] Setting updated: {key} = {value}")
            return True
        except Exception as e:
            decky.logger.error(f"[FHDS] Failed to update setting {key}: {e}")
            return False

    async def reset_settings(self) -> bool:
        """Reset all settings to defaults."""
        try:
            from fhds_engine import settings
            settings.reset()
            settings.save()
            return True
        except Exception as e:
            decky.logger.error(f"Failed to reset settings: {e}")
            return False

    # ── lifecycle ─────────────────────────────────────────────────────

    async def _main(self):
        """Called when plugin is loaded. Start the engine."""
        self.loop = asyncio.get_event_loop()
        decky.logger.info("[FHDS] Plugin loaded — starting engine")

        # Ensure our module directory is in the path
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        if plugin_dir not in os.sys.path:
            os.sys.path.insert(0, plugin_dir)

        # Start the FHDS engine in background
        self.engine_task = self.loop.create_task(self._run_engine())

    async def _unload(self):
        """Called when plugin is stopped (but not uninstalled)."""
        decky.logger.info("[FHDS] Plugin unloading — stopping engine")
        if self.engine_task:
            self.engine_task.cancel()
            self.engine_task = None

    async def _uninstall(self):
        """Called after _unload during uninstall."""
        decky.logger.info("[FHDS] Plugin uninstalled")
        # Clean up settings if needed
        try:
            from fhds_engine import settings
            settings_dir = settings._file_path()
            if settings_dir and os.path.exists(settings_dir):
                os.remove(settings_dir)
        except Exception:
            pass

    async def _migration(self):
        """Migrate old settings/data if needed."""
        pass

    # ── engine runner ─────────────────────────────────────────────────

    async def _run_engine(self):
        """Async wrapper around the FHDS engine main loop."""
        try:
            from fhds_engine.dualsense import DualSenseManager
            from fhds_engine.forzahorizon.udp_listener import UDPListener
            from fhds_engine.forzahorizon.effects import EffectsEngine
            from fhds_engine import settings

            decky.logger.info("[FHDS] Engine starting...")

            # Load settings
            settings.load_or_default()
            udp_host = settings.get('udp_host', '127.0.0.1')
            udp_port = settings.get('udp_port', 5300)
            loop = asyncio.get_event_loop()

            with UDPListener(udp_host, udp_port) as udp:
                manager = DualSenseManager()
                self._manager = manager
                engine = EffectsEngine()

                decky.logger.info("[FHDS] Engine running")

                while True:
                    await asyncio.sleep(0.001)
                    if not manager.connected:
                        manager.try_connect()

                    # Offload blocking recv to thread pool
                    pkt_addr = await loop.run_in_executor(None, udp.recv_latest)
                    pkt, addr = pkt_addr if pkt_addr else (None, None)
                    if pkt is None:
                        continue

                    telemetry = UDPListener.parse_packet(pkt)
                    if telemetry and manager.connected and not _paused:
                        left, right = engine.compute_effects(telemetry)
                        manager.set_triggers(left, right)

        except asyncio.CancelledError:
            decky.logger.info("[FHDS] Engine task cancelled")
        except Exception as e:
            decky.logger.error(f"[FHDS] Engine error: {e}")
            import traceback
            decky.logger.error(traceback.format_exc())
