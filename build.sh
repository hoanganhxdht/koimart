#!/bin/bash
# build.sh - Render build script
# This script runs during the build phase on Render

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Build complete ==="
