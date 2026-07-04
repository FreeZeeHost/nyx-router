#!/bin/bash
set -e
GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🌙 NYX-ROUTER INSTALLER v2.2.0                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "📦 Checking dependencies..."
DEPS=("curl" "jq" "python3" "pip3")
MISSING=()
for dep in "${DEPS[@]}"; do
    if ! command -v "$dep" &> /dev/null; then MISSING+=("$dep"); fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing: ${MISSING[*]}${NC}"
    echo "Install: sudo apt update && sudo apt install curl jq python3 python3-pip"
    exit 1
fi
echo -e "${GREEN}✅ All dependencies installed${NC}"
echo ""

echo "📦 Installing Python packages..."
if [ -n "$VIRTUAL_ENV" ]; then
    pip install gradio requests --quiet
else
    pip3 install gradio requests --break-system-packages --quiet 2>/dev/null || pipx install gradio requests --quiet 2>/dev/null || echo "⚠️  Install manually: pip install gradio requests"
fi

echo "📁 Installing NYX-ROUTER..."
mkdir -p ~/.nyx-router
SCRIPT_DIR="$(pwd)"
for file in nyx core.py swarm.js web_ui.py; do
    if [ -f "$SCRIPT_DIR/$file" ]; then cp "$SCRIPT_DIR/$file" "$HOME/.nyx-router/"; fi
done
chmod +x "$HOME/.nyx-router/nyx" "$HOME/.nyx-router/core.py"
sudo ln -sf "$HOME/.nyx-router/nyx" "/usr/local/bin/nyx"
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "Quick start: nyx single \"Buat REST API\" | nyx ui"
echo "🌙 Selamat menggunakan NYX-ROUTER!"
