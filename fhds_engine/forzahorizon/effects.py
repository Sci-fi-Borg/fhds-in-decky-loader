"""
Forza Horizon → DualSense trigger effects.
Uses simple HID modes that don't interfere with Steam rumble.
"""

import time, math

# HID modes
M_OFF = 0x00
M_RIGID_A = 0x02
M_VIBRATE = 0x06
M_RIGID_ZONES = 0x21


def off():
    return (M_OFF, [0]*10)


def rigid_force(f):
    return (M_RIGID_A, [max(0, min(255, int(f))), 0,0,0,0,0,0,0,0,0])


def rigid_zones(zones_0_8):
    """Per-zone resistance: 10 strengths 0-8. Packed into 6+4 bytes."""
    strengths = [max(0, min(8, int(s))) for s in zones_0_8[:10]]
    active = packed = 0
    for i, s in enumerate(strengths):
        if s > 0:
            active |= 1 << i
            packed |= (s - 1) << (3 * i)
    return (M_RIGID_ZONES, [
        active & 0xFF, (active >> 8) & 0xFF,
        packed & 0xFF, (packed >> 8) & 0xFF,
        (packed >> 16) & 0xFF, (packed >> 24) & 0xFF,
        0, 0, 0, 0,
    ])


def progressive(f):
    """Map 0-255 force to a 10-zone progressive ramp, top-heavy."""
    s = max(1, min(8, int(f * 8 / 255)))
    return rigid_zones([
        int(s * 0.3), int(s * 0.5), int(s * 0.7),
        int(s * 0.85), s, s, s, s, s, s,
    ])


def vibe(freq, amp):
    return (M_VIBRATE, [max(0, min(255, int(freq))), max(0, min(255, int(amp))), 0,0,0,0,0,0,0,0])


def _ramp(value, deadzone, baseline, max_f, curve, ceiling=255):
    if value < deadzone:
        return baseline
    r = min(1.0, (value - deadzone) / max(ceiling - deadzone, 1))
    return baseline + (max_f - baseline) * (r ** curve)


def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


class EffectsEngine:

    def __init__(self):
        self._prev_gear = 0
        self._shift_at = 0.0
        self._settings = None

    def _s(self):
        if self._settings is None:
            from .. import settings as s
            self._settings = s
        return self._settings

    def compute_effects(self, t: dict) -> tuple:
        s = self._s()
        now = time.monotonic()
        brake = t.get("brake", 0)
        accel = t.get("accel", 0)
        speed = t.get("speed", 0)
        gear = t.get("gear", 0)
        rpm = t.get("rpm", 0)
        max_rpm = t.get("max_rpm", 8000)

        # Left — Brake
        if s.get("brake_enabled", True):
            curve = s.get("brake_curve", 2.0)
            force = _ramp(brake, deadzone=0, baseline=s.get("brake_min_force", 15),
                          max_f=s.get("brake_max_force", 180), curve=curve, ceiling=255)
            if t.get("handbrake", 0) > 0:
                force = s.get("handbrake_force", 200)

            if s.get("abs_enabled", True) and brake > 50:
                slip = max(abs(t.get("tire_slip_ratio_fl", 0)), abs(t.get("tire_slip_ratio_fr", 0)),
                           abs(t.get("tire_slip_ratio_rl", 0)), abs(t.get("tire_slip_ratio_rr", 0)))
                if slip > 0.3:
                    freq = s.get("abs_frequency", 28)
                    amp = _clamp(s.get("abs_amplitude", 90))
                    return off(), vibe(freq, amp)

            left = progressive(force)
        else:
            left = off()

        # Right — Throttle
        if not s.get("throttle_enabled", True):
            return left, off()

        if s.get("gear_shift_enabled", True) and gear > 0 and gear != self._prev_gear and self._prev_gear > 0 and speed > 3:
            self._shift_at = now
        self._prev_gear = gear
        dur = s.get("gear_shift_duration_ms", 80) / 1000.0
        if now - self._shift_at < dur:
            return left, vibe(60, _clamp(s.get("gear_shift_amplitude", 180)))

        if s.get("rev_limiter_enabled", True) and max_rpm > 0:
            ratio = rpm / max_rpm
            if ratio > s.get("rev_limiter_threshold", 0.92):
                freq = s.get("rev_limiter_frequency", 28)
                amp = _clamp(s.get("rev_limiter_amplitude", 100))
                amp = int(amp * (0.6 + 0.4 * (ratio - 0.92) / 0.08))
                return left, vibe(freq, _clamp(amp))

        curve = s.get("throttle_curve", 1.8)
        force = _ramp(accel, deadzone=0, baseline=s.get("throttle_min_force", 8),
                      max_f=s.get("throttle_max_force", 130), curve=curve, ceiling=255)
        right = progressive(force)

        return left, right
