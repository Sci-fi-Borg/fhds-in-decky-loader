"""
DualSense Manager — simplified wrapper for Decky plugin.
Handles controller discovery, connection, and trigger effect writing.
"""

import logging
import time
from . import _hidraw as hid

log = logging.getLogger("fhds.dualsense")

VENDOR_ID = 0x054C
PRODUCT_IDS = (0x0CE6, 0x0DF2)

_TRIG_FLAGS = 0x04 | 0x08
_MIN_WRITE_MS = 0.2  # at most 5 writes/sec to preserve Steam rumble

USB = {"rid": 0x02, "flags": 1, "r": 11, "l": 22, "size": 64, "bt": False}
BT  = {"rid": 0x31, "flags": 2, "r": 12, "l": 23, "size": 78, "bt": True}


class DualSenseManager:

    def __init__(self):
        self._dev: hid.device | None = None
        self._layout = USB
        self.connected = False
        self._last_write = 0.0
        self._last_left: tuple | None = None
        self._last_right: tuple | None = None

    def try_connect(self) -> bool:
        if self.connected:
            return True
        devices = hid.enumerate(VENDOR_ID, 0)
        for d in devices:
            if d.get("product_id") in PRODUCT_IDS:
                try:
                    dev = hid.device()
                    dev.open_path(d["path"])
                    self._dev = dev
                    self._layout = BT if d.get("bus_type") == 5 else USB
                    self.connected = True
                    path = d["path"].decode() if isinstance(d["path"], bytes) else d["path"]
                    log.info("DualSense connected: %s (%s)", path, "BT" if self._layout["bt"] else "USB")
                    return True
                except OSError as e:
                    log.debug("Cannot open %s: %s", d.get("path"), e)
        return False

    def set_triggers(self, left_effect, right_effect):
        if not self.connected or self._dev is None:
            return
        # Don't write when both triggers are neutral (mode 0x00)
        if left_effect[0] == 0x00 and right_effect[0] == 0x00:
            return

        # Rate limit — at most 5 writes/sec to preserve Steam rumble
        now = time.monotonic()
        if now - self._last_write < _MIN_WRITE_MS:
            # Skip if unchanged; if changed, cache for next tick
            if left_effect == self._last_left and right_effect == self._last_right:
                return
            self._last_left = left_effect
            self._last_right = right_effect
            return
        self._last_left = left_effect
        self._last_right = right_effect
        self._last_write = now

        lay = self._layout
        buf = bytearray(lay["size"])
        buf[0] = lay["rid"]
        if lay["bt"]:
            buf[1] = 0x02
        buf[lay["flags"]] = _TRIG_FLAGS

        mode_r, params_r = right_effect
        pos = lay["r"]
        buf[pos] = mode_r
        for i, v in enumerate(params_r[:10]):
            buf[pos + 1 + i] = min(max(v, 0), 255)

        mode_l, params_l = left_effect
        pos = lay["l"]
        buf[pos] = mode_l
        for i, v in enumerate(params_l[:10]):
            buf[pos + 1 + i] = min(max(v, 0), 255)

        try:
            self._dev.write(bytes(buf))
        except OSError as e:
            log.warning("Write failed: %s", e)
            self.connected = False
            self._dev = None

    def disconnect(self):
        if self._dev:
            self._dev.close()
            self._dev = None
        self.connected = False
