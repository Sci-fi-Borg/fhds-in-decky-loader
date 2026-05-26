#!/usr/bin/env python3
"""
FHDS Decky Plugin Packager
Creates a zip file with correct forward-slash paths ready for Decky Loader.

Usage:
    python package_plugin.py
    python package_plugin.py --version 0.2.0
"""
import os, sys, zipfile

SRC = r"D:\ds_work\fhds-in-decky-loader"
OUT = r"D:\ds_work"
VERSION = "0.1.0"
if len(sys.argv) > 2 and sys.argv[1] == "--version":
    VERSION = sys.argv[2]

PLUGIN_NAME = "fhds-decky"
ZIP_NAME = f"{PLUGIN_NAME}-v{VERSION}.zip"
ZIP_PATH = os.path.join(OUT, ZIP_NAME)

# Files/dirs to include relative to SRC
INCLUDE = [
    "plugin.json",
    "package.json",
    "main.py",
    "LICENSE",
    "README.md",
    "dist/index.js",
    "dist/index.js.map",
    "fhds_engine/__init__.py",
    "fhds_engine/settings.py",
    "fhds_engine/dualsense/__init__.py",
    "fhds_engine/dualsense/manager.py",
    "fhds_engine/dualsense/_hidraw.py",

    "fhds_engine/forzahorizon/__init__.py",
    "fhds_engine/forzahorizon/udp_listener.py",
    "fhds_engine/forzahorizon/effects.py",
    "defaults/settings.json",
    "py_modules/.keep",
]

print(f"Packaging {PLUGIN_NAME} v{VERSION}...")

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

count = 0
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for rel in INCLUDE:
        src_path = os.path.join(SRC, rel)
        if not os.path.exists(src_path):
            print(f"  WARNING: missing {rel}")
            continue
        # Use forward-slash path with plugin directory prefix
        arcname = f"{PLUGIN_NAME}/{rel.replace(os.sep, '/')}"
        zf.write(src_path, arcname)
        count += 1

size_kb = os.path.getsize(ZIP_PATH) / 1024
print(f"Done: {ZIP_NAME} ({count} files, {size_kb:.0f} KB)")
print()
print("Install on Steam Deck:")
print(f"  1. Copy to Deck:  scp {ZIP_PATH} deck@IP:/home/deck/")
print(f"  2. SSH into Deck: cd ~/homebrew/plugins")
print(f"  3. sudo unzip /home/deck/{ZIP_NAME}")
print(f"  4. sudo chown -R deck:deck {PLUGIN_NAME}")
print(f"  5. Gaming mode -> Decky -> Reload plugins")
