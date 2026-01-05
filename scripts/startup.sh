#!/bin/bash

# GhidraInsight Startup Script
# Tüm servisleri kolayca başlatmak için

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║   GhidraInsight - Başlangıç Aracı          ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Hangisi başlatılacak?
if [[ $# -eq 0 ]]; then
    MODE="docker"
else
    MODE="$1"
fi

case $MODE in
    docker)
        echo "🐳 Docker servisleri başlatılıyor..."
        docker-compose up -d
        
        sleep 2
        echo ""
        echo -e "${GREEN}✓ Hizmetler başlatıldı!${NC}"
        echo ""
        echo "📍 Erişim noktaları:"
        echo "   🌐 Web Dashboard: http://localhost:3000"
        echo "   🔌 API Server: http://localhost:8000"
        echo "   📡 WebSocket: ws://localhost:8001"
        echo ""
        echo "📊 Durumu kontrol etmek için:"
        echo "   docker-compose ps"
        echo "   docker-compose logs -f"
        echo ""
        ;;
    
    python)
        echo "🐍 Python MCP sunucusu başlatılıyor..."
        
        if [ ! -d "python-mcp/venv" ]; then
            echo "Virtual environment bulunamadı. setup.sh çalıştırınız."
            exit 1
        fi
        
        cd python-mcp
        source venv/bin/activate
        ghidrainsight-server --host 0.0.0.0 --port 8000
        ;;
    
    dashboard)
        echo "💻 Web Dashboard başlatılıyor..."
        
        if [ ! -d "web-dashboard/node_modules" ]; then
            echo "Node modules bulunamadı. setup.sh çalıştırınız."
            exit 1
        fi
        
        cd web-dashboard
        npm run dev
        ;;
    
    all)
        echo "📦 Tüm servisleri Manuel Başlat"
        echo ""
        echo "1️⃣  Terminal 1'de Python sunucusunu başlatın:"
        echo "   ./scripts/startup.sh python"
        echo ""
        echo "2️⃣  Terminal 2'de Dashboard'ı başlatın:"
        echo "   ./scripts/startup.sh dashboard"
        echo ""
        echo "3️⃣  Web tarayıcınızda açın:"
        echo "   http://localhost:5173 (Vite dev server)"
        echo ""
        echo "💡 Veya Docker ile başlatın:"
        echo "   ./scripts/startup.sh docker"
        ;;
    
    stop)
        echo "🛑 Docker servisleri durduruluyor..."
        docker-compose down
        echo -e "${GREEN}✓ Servisler durduruldu${NC}"
        ;;
    
    *)
        echo "Geçersiz modu: $MODE"
        echo ""
        echo "Kullanım: ./scripts/startup.sh [MODE]"
        echo ""
        echo "Modu:"
        echo "  docker    - Docker ile tüm servisleri başlat (varsayılan)"
        echo "  python    - Python MCP sunucusunu başlat"
        echo "  dashboard - Web Dashboard'ı başlat"
        echo "  all       - Manuel başlatım talimatları göster"
        echo "  stop      - Docker servislerini durdur"
        exit 1
        ;;
esac
