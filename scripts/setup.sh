#!/bin/bash

# GhidraInsight Setup Script - Hızlı ve otomatik kurulum
# Kullanım: ./scripts/setup.sh --mode=all

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script başında mesaj
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║   GhidraInsight - Hızlı Kurulum Aracı      ║"
echo "║   Version 1.0 - Kullanıcı Dostu            ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Varsayılan değerler
MODE="all"
PYTHON_VERSION="3.11"
SKIP_DOCKER=false
VERBOSE=false

# Komut satırı parametrelerini işle
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --python-version=*)
            PYTHON_VERSION="${1#*=}"
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Yardım mesajı
show_help() {
    cat << EOF
GhidraInsight Setup Script

KULLANÜM:
    ./scripts/setup.sh [OPTIONS]

SEÇENEKLER:
    --mode=MODE              Kurulum modu (varsayılan: all)
                            - all: Tüm bileşenler
                            - docker: Docker kurulumu
                            - python: Python MCP sunucusu
                            - java: Java plugin
                            - dashboard: Web dashboard
    
    --python-version=VER    Python versiyonu (varsayılan: 3.11)
    --skip-docker           Docker kurulumunu atla
    --verbose               Detaylı çıktı
    --help                  Bu yardım mesajını göster

ÖRNEKLER:
    ./scripts/setup.sh --mode=all
    ./scripts/setup.sh --mode=python --python-version=3.10
    ./scripts/setup.sh --mode=docker

EOF
}

# Hata yöneticisi
error() {
    echo -e "${RED}✗ HATA: $1${NC}"
    exit 1
}

# Başarı mesajı
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Bilgi mesajı
info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Uyarı mesajı
warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Sistem kontrolü
check_system() {
    info "Sistem ve bağımlılıklar kontrol ediliyor..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        error "Bu script Windows'da native olarak çalıştırılamaz. WSL2 kullanınız."
    else
        error "Desteklenmeyen işletim sistemi: $OSTYPE"
    fi
    success "OS detected: $OS"
}

# Java kontrolü
check_java() {
    info "Java kontrolü yapılıyor..."
    
    if ! command -v java &> /dev/null; then
        warn "Java bulunamadı"
        return 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -n1)
    success "Java bulundu: $JAVA_VERSION"
    return 0
}

# Python kontrolü
check_python() {
    info "Python $PYTHON_VERSION kontrolü yapılıyor..."
    
    if ! command -v python$PYTHON_VERSION &> /dev/null && ! command -v python &> /dev/null; then
        warn "Python bulunamadı"
        return 1
    fi
    
    PYTHON_CMD="python$PYTHON_VERSION"
    if ! command -v $PYTHON_CMD &> /dev/null; then
        PYTHON_CMD="python"
    fi
    
    PYTHON_ACTUAL_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    success "Python bulundu: $PYTHON_ACTUAL_VERSION"
    return 0
}

# Node.js kontrolü
check_nodejs() {
    info "Node.js kontrol ediliyor..."
    
    if ! command -v node &> /dev/null; then
        warn "Node.js bulunamadı"
        return 1
    fi
    
    NODE_VERSION=$(node --version)
    success "Node.js bulundu: $NODE_VERSION"
    return 0
}

# Docker kontrolü
check_docker() {
    info "Docker kontrol ediliyor..."
    
    if ! command -v docker &> /dev/null; then
        warn "Docker bulunamadı"
        return 1
    fi
    
    DOCKER_VERSION=$(docker --version)
    success "$DOCKER_VERSION"
    return 0
}

# Ghidra kontrolü
check_ghidra() {
    info "Ghidra kurulumu kontrol ediliyor..."
    
    if [ -z "$GHIDRA_INSTALL_DIR" ]; then
        warn "GHIDRA_INSTALL_DIR ortam değişkeni ayarlanmamış"
        return 1
    fi
    
    if [ ! -d "$GHIDRA_INSTALL_DIR" ]; then
        warn "Ghidra dizini bulunamadı: $GHIDRA_INSTALL_DIR"
        return 1
    fi
    
    success "Ghidra bulundu: $GHIDRA_INSTALL_DIR"
    return 0
}

# Docker kurulum
setup_docker() {
    if [[ "$SKIP_DOCKER" == true ]]; then
        warn "Docker kurulumu atlandı"
        return
    fi
    
    echo -e "\n${BLUE}=== Docker Kurulumu ===${NC}"
    
    if ! check_docker; then
        error "Docker kurulması gerekli. Docker Desktop'ı indirin: https://www.docker.com/"
    fi
    
    info "docker-compose kontrolü yapılıyor..."
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose bulunamadı"
    fi
    success "docker-compose bulundu"
    
    info "Docker imajları indiriliyotu..."
    docker-compose pull
    
    success "Docker kurulum tamamlandı"
}

# Python kurulum
setup_python() {
    echo -e "\n${BLUE}=== Python MCP Sunucusu Kurulumu ===${NC}"
    
    if ! check_python; then
        error "Python bulunamadı. Python 3.9+ kurmalısınız"
    fi
    
    cd python-mcp || error "python-mcp dizini bulunamadı"
    
    info "Virtual environment oluşturuluyor..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    info "Paketler kuruluyotu..."
    pip install --upgrade pip setuptools wheel
    pip install -e .
    
    success "Python kurulum tamamlandı"
    echo -e "${GREEN}Sunucuyu başlatmak için: ghidrainsight-server${NC}"
}

# Java kurulum
setup_java() {
    echo -e "\n${BLUE}=== Java Ghidra Plugin Kurulumu ===${NC}"
    
    if ! check_java; then
        error "Java bulunamadı. JDK 11+ kurmalısınız"
    fi
    
    if ! check_ghidra; then
        warn "Ghidra kurulması gerekli"
        return
    fi
    
    cd ghidra-plugin || error "ghidra-plugin dizini bulunamadı"
    
    info "Gradle build yapılıyor..."
    ./gradlew build
    
    info "Plugin Ghidra'ya kopyalanıyor..."
    PLUGIN_JAR=$(find build/libs -name "*.jar" -type f | head -n1)
    if [ -z "$PLUGIN_JAR" ]; then
        error "JAR dosyası bulunamadı"
    fi
    
    cp "$PLUGIN_JAR" "$GHIDRA_INSTALL_DIR/Extensions/Ghidra/plugins/"
    success "Plugin kuruldu"
}

# Dashboard kurulum
setup_dashboard() {
    echo -e "\n${BLUE}=== Web Dashboard Kurulumu ===${NC}"
    
    if ! check_nodejs; then
        error "Node.js bulunamadı. Node.js 18+ kurmalısınız"
    fi
    
    cd web-dashboard || error "web-dashboard dizini bulunamadı"
    
    info "Bağımlılıklar kuruluyotu..."
    npm install
    
    success "Dashboard kurulum tamamlandı"
    echo -e "${GREEN}Sunucuyu başlatmak için: npm run dev${NC}"
}

# Tüm bileşenleri kur
setup_all() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      Tüm Bileşenlerin Kurulumu        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    check_system
    
    echo ""
    info "Temel kontrollar yapılıyor..."
    HAS_ISSUES=false
    
    check_python || HAS_ISSUES=true
    check_nodejs || HAS_ISSUES=true
    check_java || HAS_ISSUES=true
    check_docker || HAS_ISSUES=true
    
    if [[ "$HAS_ISSUES" == true ]]; then
        echo ""
        warn "Bazı bağımlılıklar eksik"
        read -p "Devam etmek istiyor musunuz? (e/H) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ee]$ ]]; then
            error "Kurulum iptal edildi"
        fi
    fi
    
    # Docker kontrolü
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        read -p "Docker ile kurulumu tercih ediyor musunuz? (E/h) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Hh]$ ]]; then
            setup_docker
            success "Tüm kurulum Docker ile tamamlandı!"
            echo -e "${GREEN}Başlatmak için: docker-compose up -d${NC}"
            return
        fi
    fi
    
    # Manuel kurulum
    echo ""
    info "Manuel kuruluma devam ediliyor..."
    
    setup_python
    echo ""
    setup_dashboard
    echo ""
    setup_java || warn "Java plugin kurulumu atlandı"
}

# Main
case $MODE in
    all)
        setup_all
        ;;
    docker)
        check_system
        setup_docker
        ;;
    python)
        check_system
        setup_python
        ;;
    java)
        check_system
        setup_java
        ;;
    dashboard)
        check_system
        setup_dashboard
        ;;
    *)
        error "Bilinmeyen mod: $MODE"
        ;;
esac

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Kurulum Başarıyla Tamamlandı!    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
info "Sonraki adımlar:"
echo "  📖 Dokümantasyon: https://github.com/yourusername/GhidraInsight"
echo "  🚀 Hızlı başlangıç: cat docs/QUICKSTART.md"
echo "  💬 Yardım: ghidrainsight --help"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "  Python: $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "  Node.js: $NODE_VERSION"

# Check Gradle
echo "✓ Checking Gradle..."
if [ ! -f "ghidra-plugin/gradlew" ]; then
    echo "⚠️  Gradle wrapper not found, using system gradle"
fi

# Setup Java Plugin
echo ""
echo "📦 Setting up Java Ghidra plugin..."
cd ghidra-plugin
if [ ! -f "gradlew" ]; then
    chmod +x gradlew
fi
echo "  Building plugin..."
./gradlew build -q
cd ..

# Setup Python MCP
echo ""
echo "📦 Setting up Python MCP server..."
cd python-mcp
echo "  Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "  Installing dependencies..."
pip install -q -e ".[dev]"
deactivate
cd ..

# Setup Web Dashboard
echo ""
echo "📦 Setting up web dashboard..."
cd web-dashboard
echo "  Installing dependencies..."
npm install -q
cd ..

# Create .env file if not exists
echo ""
echo "⚙️  Creating configuration files..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# GhidraInsight Configuration
GHIDRA_INSTALL_DIR=/opt/ghidra-11.0
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_LOG_LEVEL=INFO

JWT_SECRET=change-this-to-a-secure-key-at-least-32-chars
JWT_ALGORITHM=HS256
API_KEY=your-api-key-here

RATE_LIMIT=60
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

TELEMETRY_ENABLED=false
EOF
    echo "  Created .env (configure with your settings)"
fi

# Create directories
echo ""
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p data
mkdir -p cache

# Summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set GHIDRA_INSTALL_DIR in .env"
echo "2. Configure JWT_SECRET and API_KEY"
echo "3. Run: make start"
echo ""
echo "Or start components individually:"
echo "  - Java: cd ghidra-plugin && ./gradlew run"
echo "  - Python: cd python-mcp && source venv/bin/activate && ghidrainsight-server"
echo "  - Web: cd web-dashboard && npm run dev"
