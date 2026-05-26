"""
DualSense HID module for Steam Deck (Linux).
Direct /dev/hidraw access — bypasses libusb-built hidapi.
Adapted from Forza-Horizon-DualSense-Python.
"""

import array
import fcntl
import glob
import os
import logging

log = logging.getLogger("fhds.hidraw")

# ── ioctl helpers ──────────────────────────────────────────────────────

def _ioc(direction: int, type_: int, nr: int, size: int) -> int:
    return (direction << 30) | (size << 16) | (type_ << 8) | nr

_HID_TYPE = ord("H")
_HIDIOCSFEATURE_NR = 0x06
_HIDIOCGFEATURE_NR = 0x07


def enumerate(vendor_id: int = 0, product_id: int = 0) -> list[dict]:
    """Find DualSense hidraw devices by VID/PID."""
    out = []
    for node in sorted(glob.glob("/dev/hidraw*")):
        try:
            with open(f"/sys/class/hidraw/{os.path.basename(node)}/device/uevent") as f:
                fields = dict(l.strip().split("=", 1) for l in f if "=" in l)
            bus, vid, pid = (int(p, 16) for p in fields["HID_ID"].split(":"))
        except (OSError, KeyError, ValueError):
            continue
        if (vendor_id and vid != vendor_id) or (product_id and pid != product_id):
            continue
        serial = fields.get("HID_UNIQ", "").replace(":", "").lower()
        out.append({
            "path": node.encode(),
            "product_id": pid,
            "bus_type": bus,
            "serial_number": serial,
        })
    return out


class device:
    """Thin wrapper around a hidraw file descriptor."""

    _fd: int = -1

    def open_path(self, path):
        """Open hidraw device for read/write."""
        path_str = path.decode() if isinstance(path, bytes) else path
        log.info("Opening hidraw device: %s", path_str)
        self._fd = os.open(path_str, os.O_RDWR | os.O_NONBLOCK)

    def set_nonblocking(self, _nb):
        pass  # We always use O_NONBLOCK

    def write(self, data):
        return os.write(self._fd, bytes(data))

    def get_feature_report(self, report_id, length):
        buf = array.array("B", bytes([report_id]) + bytes(length))
        fcntl.ioctl(self._fd, _ioc(3, _HID_TYPE, _HIDIOCGFEATURE_NR, len(buf)), buf, True)
        return list(buf)

    def send_feature_report(self, data):
        buf = array.array("B", bytes(data))
        return fcntl.ioctl(self._fd, _ioc(3, _HID_TYPE, _HIDIOCSFEATURE_NR, len(buf)), buf, True)

    def read(self, size, timeout_ms=0):
        try:
            return os.read(self._fd, size)
        except (BlockingIOError, OSError):
            return b""

    def close(self):
        if self._fd >= 0:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = -1
