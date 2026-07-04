#!/bin/bash
set -e
GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🌙 NYX-ROUTER INSTALLER v2.2.0                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "📦 Installing NYX-ROUTER..."
mkdir -p ~/.nyx-router
SCRIPT_DIR="$(pwd)"
for file in nyx core.py swarm.js web_ui.py; do
    if [ -f "$SCRIPT_DIR/$file" ]; then cp "$SCRIPT_DIR/$file" "$HOME/.nyx-router/"; fi
done
chmod +x "$HOME/.nyx-router/nyx" "$HOME/.nyx-router/core.py"
sudo ln -sf "$HOME/.nyx-router/nyx" "/usr/local/bin/nyx"

echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "Quick start: nyx single \"Buat REST API\" --free"
echo "🌙 Selamat menggunakan NYX-ROUTER!"
