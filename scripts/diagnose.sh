#!/bin/bash
# =============================================================================
# FHDS Diagnostic Script for Steam Deck
# Run this in both Desktop Mode and Gaming Mode (via SSH) to compare output.
#
# Usage:
#   chmod +x diagnose.sh
#   ./diagnose.sh                    # basic check
#   ./diagnose.sh --gaming           # gaming mode specific checks
#   ./diagnose.sh --compare          # show both mode recommendations
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  FHDS Decky Plugin — Steam Deck Diagnostic${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo ""

# ── 1. System Info ──────────────────────────────────────────────────────

echo -e "${YELLOW}[1/7] System Information${NC}"
echo "  Kernel: $(uname -r)"
echo "  User: $(whoami)"
echo "  Groups: $(groups)"
echo "  Session: $(echo $XDG_SESSION_TYPE)"
echo "  Steam running: $(pgrep -c steam || echo 'no')"
echo "  Gamescope running: $(pgrep -c gamescope || echo 'no')"
echo ""

# ── 2. hidraw Devices ───────────────────────────────────────────────────

echo -e "${YELLOW}[2/7] /dev/hidraw* Devices${NC}"
HIDRAW_COUNT=$(ls /dev/hidraw* 2>/dev/null | wc -l)
echo "  Total hidraw nodes: $HIDRAW_COUNT"

for dev in /dev/hidraw*; do
    [ -e "$dev" ] || continue
    BASENAME=$(basename "$dev")
    UEVENT="/sys/class/hidraw/$BASENAME/device/uevent"
    if [ -f "$UEVENT" ]; then
        HID_ID=$(grep HID_ID "$UEVENT" 2>/dev/null | cut -d= -f2)
        HID_NAME=$(grep HID_NAME "$UEVENT" 2>/dev/null | cut -d= -f2)
        HID_UNIQ=$(grep HID_UNIQ "$UEVENT" 2>/dev/null | cut -d= -f2)
        # Check if it's a DualSense (Sony VID=054C)
        if echo "$HID_ID" | grep -qi "054C"; then
            echo -e "  ${GREEN}$dev → $HID_NAME (DualSense!)${NC}"
            echo "    HID_ID: $HID_ID"
            echo "    UNIQ: $HID_UNIQ"
        else
            echo "  $dev → $HID_NAME"
            echo "    HID_ID: $HID_ID"
        fi
    else
        echo "  $dev → (no uevent)"
    fi
done
echo ""

# ── 3. Permissions ──────────────────────────────────────────────────────

echo -e "${YELLOW}[3/7] Device Permissions${NC}"
for dev in /dev/hidraw*; do
    [ -e "$dev" ] || continue
    PERMS=$(ls -la "$dev" | awk '{print $1, $3, $4}')
    echo "  $dev: $PERMS"
    
    # Check if we can read it
    if [ -r "$dev" ]; then
        echo -e "    ${GREEN}✓ Readable${NC}"
    else
        echo -e "    ${RED}✗ Not readable${NC}"
    fi
    if [ -w "$dev" ]; then
        echo -e "    ${GREEN}✓ Writable${NC}"
    else
        echo -e "    ${RED}✗ Not writable${NC}"
    fi
done
echo ""

# ── 4. Processes Holding hidraw ─────────────────────────────────────────

echo -e "${YELLOW}[4/7] Processes Accessing hidraw${NC}"
if command -v fuser &>/dev/null; then
    for dev in /dev/hidraw*; do
        [ -e "$dev" ] || continue
        USERS=$(fuser "$dev" 2>/dev/null || true)
        if [ -n "$USERS" ]; then
            echo "  $dev:"
            for pid in $USERS; do
                CMD=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
                echo "    PID $pid → $CMD"
            done
        fi
    done
else
    echo "  (fuser not available — install psmisc)"
fi
echo ""

# ── 5. UDP Port 5300 ────────────────────────────────────────────────────

echo -e "${YELLOW}[5/7] UDP Port 5300 Status${NC}"
if command -v ss &>/dev/null; then
    UDP_LISTEN=$(ss -uln | grep ':5300' || true)
elif command -v netstat &>/dev/null; then
    UDP_LISTEN=$(netstat -uln | grep ':5300' || true)
else
    UDP_LISTEN=""
fi

if [ -n "$UDP_LISTEN" ]; then
    echo -e "  ${GREEN}Port 5300 is in use (UDP listener active)${NC}"
    echo "  $UDP_LISTEN"
else
    echo -e "  ${YELLOW}Port 5300 is free (no UDP listener)${NC}"
fi
echo ""

# ── 6. hid-playstation Driver ───────────────────────────────────────────

echo -e "${YELLOW}[6/7] hid-playstation Kernel Module${NC}"
if lsmod | grep -q hid_playstation; then
    echo -e "  ${GREEN}hid-playstation loaded${NC}"
else
    echo -e "  ${YELLOW}hid-playstation not loaded${NC}"
fi

# Check dmesg for DualSense events
echo "  Recent DualSense kernel messages:"
dmesg 2>/dev/null | grep -i dualsens | tail -5 || echo "  (none)"
echo ""

# ── 7. Gaming Mode Specific ─────────────────────────────────────────────

echo -e "${YELLOW}[7/7] Decky Plugin Environment${NC}"
if [ -d "$HOME/homebrew" ]; then
    echo -e "  ${GREEN}Decky Loader found at ~/homebrew${NC}"
    if [ -d "$HOME/homebrew/logs" ]; then
        echo "  Latest FHDS logs:"
        find "$HOME/homebrew/logs" -name "*fhds*" -type f 2>/dev/null | head -3
        echo "  (run 'cat <logfile>' to read)"
    fi
else
    echo -e "  ${YELLOW}Decky Loader not found (expected on Steam Deck)${NC}"
fi
echo ""

# ── Summary ─────────────────────────────────────────────────────────────

echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Quick Assessment${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"

DUALSENSE_FOUND=$(grep -l "054C" /sys/class/hidraw/*/device/uevent 2>/dev/null | wc -l)
HIDRAW_ACCESSIBLE=false
for dev in /dev/hidraw*; do
    [ -e "$dev" ] || continue
    if [ -w "$dev" ]; then
        HIDRAW_ACCESSIBLE=true
        break
    fi
done

if [ "$DUALSENSE_FOUND" -gt 0 ]; then
    echo -e "  ${GREEN}✓ DualSense detected ($DUALSENSE_FOUND interface(s))${NC}"
else
    echo -e "  ${RED}✗ No DualSense found — is it connected?${NC}"
    echo "    Try: USB cable connection (not Bluetooth) for testing"
fi

if $HIDRAW_ACCESSIBLE; then
    echo -e "  ${GREEN}✓ hidraw devices are writable${NC}"
else
    echo -e "  ${RED}✗ hidraw devices not writable — check udev rules${NC}"
    echo "    Run: sudo usermod -a -G input $USER"
fi

echo ""
echo "If DualSense is found AND hidraw is writable, the plugin should work."
echo "If it doesn't work in Gaming Mode, compare this output with Desktop Mode."
echo ""
echo "Run in Gaming Mode via SSH:"
echo "  ssh deck@steamdeck 'bash -s' < ./diagnose.sh"
