#!/bin/bash
set -e
GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
echo ""
echo "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo "${BLUE}║         🌙 NYX-ROUTER INSTALLER v2.2.0                   ║${NC}"
echo "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📦 Checking dependencies..."
DEPS=("curl" "jq" "python3" "pip3")
MISSING=()
for dep in "${DEPS[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        MISSING+=("$dep")
    fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
    echo "${RED}❌ Missing: ${MISSING[*]}${NC}"
    echo "Install: sudo apt update && sudo apt install curl jq python3 python3-pip"
    exit 1
fi
echo "${GREEN}✅ All dependencies installed${NC}"
echo ""
echo "📦 Installing Python packages..."
pip3 install gradio requests --quiet
echo "📁 Installing NYX-ROUTER..."
mkdir -p ~/.nyx-router
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for file in nyx core.py swarm.js web-ui.py; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$HOME/.nyx-router/"
    fi
done
chmod +x "$HOME/.nyx-router/nyx"
chmod +x "$HOME/.nyx-router/core.py"
sudo ln -sf "$HOME/.nyx-router/nyx" "/usr/local/bin/nyx"
echo "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "Quick start:"
echo "  nyx single \"Buat REST API\""
echo "  nyx swarm \"Tulis artikel\""
echo "  nyx orch \"Research blockchain\""
echo "  nyx ui    # Web UI"
echo ""
echo "🌙 Selamat menggunakan NYX-ROUTER!"
