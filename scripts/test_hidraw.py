#!/usr/bin/env python3
"""
FHDS Desktop Mode Sanity Test
Test hidraw enumeration and write access to DualSense on Steam Deck.
Run in desktop mode with DualSense connected via USB.
"""

import sys, os
sys.path.insert(0, "/home/deck/fhds-in-decky-loader")

print("=== FHDS hidraw Sanity Test ===")
print()

# ── 1. Enumerate DualSense hidraw devices ────────────────────────────

from fhds_engine.dualsense._hidraw import enumerate

devices = enumerate(0x054C, 0)
print(f"hidraw devices found: {len(devices)}")
for d in devices:
    path = d["path"].decode() if isinstance(d["path"], bytes) else d["path"]
    bus_name = {0: "PCI", 1: "ISAPNP", 2: "USB", 3: "HIL", 4: "Bluetooth", 5: "Virtual"}.get(d["bus_type"], f"bus={d['bus_type']}")
    print(f"  {path}  pid={d['product_id']:#06x}  bus={bus_name}  serial={d.get('serial_number', 'none')}")
print()

# ── 2. Try opening and writing to the first device ───────────────────

if not devices:
    print("✗ No DualSense found!")
    print("  Check: is the controller plugged in via USB cable?")
    print("  Check: does the controller light up when connected?")
    print("  Run: lsusb | grep -i sony")
    sys.exit(1)

from fhds_engine.dualsense._hidraw import device

for i, dev_info in enumerate(devices):
    path = dev_info["path"]
    d = device()
    try:
        d.open_path(path)
        print(f"[{i}] ✓ Opened {path}")

        # Write a minimal HID output report (trigger flags only, no effects)
        # Report ID 0x02 = USB gamepad output, 64 bytes
        buf = bytearray(64)
        buf[0] = 0x02       # report ID
        buf[1] = 0x0C       # valid_flag0: R trigger (0x04) | L trigger (0x08)
        # All other bytes are 0 = no trigger effect, no rumble
        d.write(bytes(buf))
        print(f"    ✓ Write test passed (empty report)")

        d.close()
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        try:
            d.close()
        except Exception:
            pass

print()
print("If all devices show ✓, the hidraw layer is working.")
print("Next step: run the full integration test (test_full.py)")
print("Then: switch to gaming mode and re-run via SSH to compare.")
