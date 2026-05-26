#!/usr/bin/env python3
"""
FHDS Full Integration Test
Tests the complete pipeline: UDP telemetry → effects engine → DualSense triggers.
Run in desktop mode. Forza Horizon must be running with Data Out enabled.
"""

import sys, os, time
sys.path.insert(0, "/home/deck/fhds-in-decky-loader")

print("=== FHDS Full Integration Test ===")
print("Make sure Forza Horizon is running with Data Out enabled (UDP 127.0.0.1:5300)")
print()

# ── 1. Load settings ─────────────────────────────────────────────────

from fhds_engine import settings
settings.load_or_default()
print(f"Settings loaded: {len(settings.to_dict())} keys")

# ── 2. Open UDP listener ─────────────────────────────────────────────

from fhds_engine.forzahorizon.udp_listener import UDPListener
print("Starting UDP listener on port 5300...")
udp = UDPListener("127.0.0.1", 5300, timeout=1.0)
udp.__enter__()
print("UDP listener ready")
print()

# ── 3. Connect to controller ─────────────────────────────────────────

from fhds_engine.dualsense import DualSenseManager
mgr = DualSenseManager()
print("Searching for DualSense...")
if mgr.try_connect():
    print("✓ DualSense connected!")
else:
    print("✗ No DualSense found — is it plugged in via USB?")
    udp.__exit__(None, None, None)
    sys.exit(1)
print()

# ── 4. Main loop ─────────────────────────────────────────────────────

from fhds_engine.forzahorizon.effects import EffectsEngine
engine = EffectsEngine()
packet_count = 0
start = time.time()

print("Waiting for Forza UDP data...")
print("Get in a car and start driving. Press Ctrl+C to stop.")
print()

last_print = 0
try:
    while packet_count < 500 and time.time() - start < 60:
        pkt, addr = udp.recv_latest()
        if pkt is None:
            continue
        packet_count += 1
        t = udp.parse_packet(pkt)
        if t and t.get("on"):
            left, right = engine.compute_effects(t)
            mgr.set_triggers(left, right)

            # Print status every 2 seconds
            now = time.time()
            if now - last_print >= 2:
                L_force = left[1][0] if left[0] else 0
                R_force = right[1][0] if right[0] else 0
                print(f"  pkt#{packet_count:04d}: speed={t['speed']:6.0f} km/h  "
                      f"rpm={t['rpm']:7.0f}  gear={t['gear']}  "
                      f"brake={t['brake']:3d}  L={L_force:3d}  R={R_force:3d}")
                last_print = now

        # Also reconnect if controller was lost
        if not mgr.connected:
            mgr.try_connect()

except KeyboardInterrupt:
    print("\nInterrupted by user")

elapsed = time.time() - start
print(f"\nProcessed {packet_count} packets in {elapsed:.1f}s "
      f"({packet_count/elapsed:.0f} pps)")
mgr.disconnect()
udp.__exit__(None, None, None)
print("Done — triggers should have been active during the test")
