#!/bin/bash

# GhidraInsight Troubleshooting Script
# Yaygın sorunları tanı ve çöz

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║   GhidraInsight - Sorun Çözen Araç         ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Hata mesajı
error() {
    echo -e "${RED}✗ $1${NC}"
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

# Logları göster
show_logs() {
    local service=$1
    echo ""
    info "Son 20 log satırı:"
    docker-compose logs --tail=20 $service
}

# Sistem bilgisi topla
collect_diagnostics() {
    echo ""
    echo -e "${BLUE}=== Sistem Tanılaması ===${NC}"
    echo ""
    
    info "İşletim Sistemi:"
    uname -a
    echo ""
    
    info "Docker Bilgisi:"
    if command -v docker &> /dev/null; then
        docker --version
        docker-compose --version
    else
        error "Docker bulunamadı"
    fi
    echo ""
    
    info "Java Bilgisi:"
    if command -v java &> /dev/null; then
        java -version
    else
        warn "Java bulunamadı (Optional)"
    fi
    echo ""
    
    info "Python Bilgisi:"
    if command -v python &> /dev/null; then
        python --version
    else
        warn "Python bulunamadı"
    fi
    echo ""
    
    info "Node.js Bilgisi:"
    if command -v node &> /dev/null; then
        node --version
        npm --version
    else
        warn "Node.js bulunamadı (Dashboard için gerekli)"
    fi
}

# Docker kontrol et
check_docker() {
    echo -e "\n${BLUE}=== Docker Kontrolü ===${NC}"
    
    if ! command -v docker &> /dev/null; then
        error "Docker kurulu değil"
        echo "   İndir: https://www.docker.com/products/docker-desktop"
        return 1
    fi
    success "Docker kurulu"
    
    if ! docker ps &> /dev/null; then
        error "Docker daemon çalışmıyor"
        echo "   Çözüm: Docker Desktop'ı başlatın"
        return 1
    fi
    success "Docker daemon çalışıyor"
    
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose kurulu değil"
        return 1
    fi
    success "docker-compose kurulu"
    
    return 0
}

# Container durumunu kontrol et
check_containers() {
    echo -e "\n${BLUE}=== Container Durumu ===${NC}"
    
    docker-compose ps
    
    echo ""
    info "Container günlüklerini görmek için:"
    echo "  docker-compose logs -f [service]"
}

# Port kontrolü
check_ports() {
    echo -e "\n${BLUE}=== Port Kontrolü ===${NC}"
    
    local ports=(3000 8000 8001 8002 5173)
    
    for port in "${ports[@]}"; do
        if command -v lsof &> /dev/null; then
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                success "Port $port: Kullanımda"
            else
                warn "Port $port: Boş"
            fi
        else
            info "lsof komutu bulunamadı. Manuel kontrol edin: netstat -tuln | grep $port"
        fi
    done
}

# API kontrolü
check_api() {
    echo -e "\n${BLUE}=== API Sunucusu Kontrolü ===${NC}"
    
    if command -v curl &> /dev/null; then
        if curl -s http://localhost:8000/health &> /dev/null; then
            success "API sunucusu (http://localhost:8000) çalışıyor"
        else
            error "API sunucusu yanıt vermiyor"
            info "API loglarını kontrol edin: docker-compose logs python-mcp"
        fi
    else
        warn "curl bulunamadı. Manuel kontrol edin."
    fi
}

# Dashboard kontrolü
check_dashboard() {
    echo -e "\n${BLUE}=== Dashboard Kontrolü ===${NC}"
    
    if command -v curl &> /dev/null; then
        if curl -s http://localhost:3000 &> /dev/null; then
            success "Dashboard (http://localhost:3000) çalışıyor"
        else
            error "Dashboard yanıt vermiyor"
            info "Dashboard loglarını kontrol edin: docker-compose logs web-dashboard"
        fi
    else
        warn "curl bulunamadı. Manuel kontrol edin."
    fi
}

# Yaygın sorunlar
show_solutions() {
    echo -e "\n${BLUE}=== Yaygın Sorunlar ve Çözümleri ===${NC}"
    
    echo ""
    echo "1️⃣  'docker: command not found'"
    echo "   → Docker Desktop'ı indirin: https://www.docker.com/"
    echo "   → macOS: brew install docker docker-compose"
    echo ""
    
    echo "2️⃣  'Cannot connect to Docker daemon'"
    echo "   → Docker Desktop uygulamasını başlatın"
    echo "   → Veya şunu çalıştırın: sudo systemctl start docker"
    echo ""
    
    echo "3️⃣  'Port 3000 already in use'"
    echo "   → Mevcut süreci öldürün: lsof -ti:3000 | xargs kill -9"
    echo "   → Veya farklı port kullanın: PORT=3001 docker-compose up"
    echo ""
    
    echo "4️⃣  'npm ERR! code ERESOLVE'"
    echo "   → Package.json bağımlılıklarını temizle: npm cache clean --force"
    echo "   → Sonra yeniden yükle: npm install"
    echo ""
    
    echo "5️⃣  'Python venv hatası'"
    echo "   → setup.sh'ı yeniden çalıştırın: ./scripts/setup.sh --mode=python"
    echo ""
    
    echo "6️⃣  'Gradle build hatası'"
    echo "   → Gradle cache'ini temizle: cd ghidra-plugin && ./gradlew clean"
    echo ""
}

# Reset işlemi
perform_reset() {
    echo -e "\n${YELLOW}=== Reset İşlemi ===${NC}"
    
    read -p "Tüm Docker servislerini sıfırlayacak mısınız? (e/H) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ee]$ ]]; then
        warn "Durduruluyor..."
        docker-compose down -v
        success "Tamamen sıfırlandı"
        
        read -p "Yeniden başlatılsın mı? (E/h) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Hh]$ ]]; then
            info "Yeniden başlatılıyor..."
            docker-compose up -d
            success "Yeniden başlatıldı"
        fi
    fi
}

# Menu
show_menu() {
    echo ""
    echo -e "${BLUE}Tanılama Seçenekleri:${NC}"
    echo "  1) Tüm kontrolü çalıştır (Önerilen)"
    echo "  2) Docker kontrol et"
    echo "  3) Container durumunu kontrol et"
    echo "  4) Port durumunu kontrol et"
    echo "  5) API sunucusunu kontrol et"
    echo "  6) Dashboard'ı kontrol et"
    echo "  7) Yaygın sorunları göster"
    echo "  8) Sistem tanılaması topla"
    echo "  9) Logları göster"
    echo "  10) Sıfırlama işlemi yap"
    echo "  0) Çık"
    echo ""
}

# Main menu loop
main_menu() {
    while true; do
        show_menu
        read -p "Seçim yapınız [0-10]: " choice
        
        case $choice in
            1)
                collect_diagnostics
                check_docker
                check_containers
                check_ports
                check_api
                check_dashboard
                ;;
            2)
                check_docker
                ;;
            3)
                check_containers
                ;;
            4)
                check_ports
                ;;
            5)
                check_api
                ;;
            6)
                check_dashboard
                ;;
            7)
                show_solutions
                ;;
            8)
                collect_diagnostics
                ;;
            9)
                read -p "Hangi hizmetin günlüğünü görmek ister misiniz? (python-mcp/web-dashboard/ghidra-plugin): " service
                if [ -n "$service" ]; then
                    show_logs "$service"
                fi
                ;;
            10)
                perform_reset
                ;;
            0)
                echo "Çıkılıyor..."
                exit 0
                ;;
            *)
                error "Geçersiz seçim"
                ;;
        esac
    done
}

# Komut satırı parametresi varsa direkt çalıştır
if [[ $# -eq 0 ]]; then
    main_menu
else
    case "$1" in
        --full)
            collect_diagnostics
            check_docker
            check_containers
            check_ports
            check_api
            check_dashboard
            show_solutions
            ;;
        --docker)
            check_docker
            ;;
        --containers)
            check_containers
            ;;
        --ports)
            check_ports
            ;;
        --api)
            check_api
            ;;
        --dashboard)
            check_dashboard
            ;;
        --logs)
            show_logs "$2"
            ;;
        --reset)
            perform_reset
            ;;
        *)
            echo "Bilinmeyen parametre: $1"
            echo "Kullanım: $0 [--full|--docker|--containers|--ports|--api|--dashboard|--logs SERVICE|--reset]"
            exit 1
            ;;
    esac
fi

echo ""
echo -e "${GREEN}✓ Tanılama tamamlandı${NC}"
