#!/usr/bin/env python3
"""
FHDS Quick Check — raw /dev/hidraw open/write test.
Target a specific hidraw node to verify read/write permissions.
"""

import os, sys, glob

# ── Pick target ───────────────────────────────────────────────────────

target = None
if len(sys.argv) > 1:
    target = sys.argv[1]
else:
    # Auto-detect: find the first DualSense hidraw node
    for node in sorted(glob.glob("/dev/hidraw*")):
        try:
            name = os.path.basename(node)
            uevent = f"/sys/class/hidraw/{name}/device/uevent"
            with open(uevent) as f:
                fields = dict(l.strip().split("=", 1) for l in f if "=" in l)
            bus, vid, pid = (int(p, 16) for p in fields["HID_ID"].split(":"))
            if vid == 0x054C and pid in (0x0CE6, 0x0DF2):
                target = node
                break
        except (OSError, KeyError, ValueError, IndexError):
            continue

if not target:
    print("✗ No DualSense hidraw node found. Connected via USB?")
    print("  Usage: python scripts/quick_check.py /dev/hidrawN")
    sys.exit(1)

print(f"Target: {target}")

# ── 1. Open ───────────────────────────────────────────────────────────

try:
    fd = os.open(target, os.O_RDWR | os.O_NONBLOCK)
    print(f"✓ open OK  (fd={fd})")
except PermissionError:
    print(f"✗ open FAILED: Permission denied")
    print(f"  Fix: sudo usermod -a -G input deck && reboot")
    sys.exit(1)
except OSError as e:
    print(f"✗ open FAILED: {e}")
    sys.exit(1)

# ── 2. Write empty report ─────────────────────────────────────────────

try:
    buf = bytearray(64)
    buf[0] = 0x02   # HID report ID (USB gamepad output)
    buf[1] = 0x0C   # valid_flag0: enable R+L trigger effects
    n = os.write(fd, bytes(buf))
    print(f"✓ write OK  ({n} bytes)")
except OSError as e:
    print(f"✗ write FAILED: {e}")

os.close(fd)
