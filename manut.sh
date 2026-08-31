#!/bin/bash

# ============================================================
#  Script de Manutenção Linux - RAM / Disco / CPU / Órfãos
#  Autor: Grok
#  Uso: sudo bash manutencao.sh
# ============================================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Verifica se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[ERRO] Este script precisa ser executado como root (sudo).${NC}"
   exit 1
fi

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         SCRIPT DE MANUTENÇÃO LINUX - COMPLETO            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
pause() {
    echo
    read -p "Pressione ENTER para continuar..."
}

confirm() {
    read -p "$(echo -e ${YELLOW}$1 [s/N]: ${NC})" resp
    [[ "$resp" =~ ^[sS]$ ]]
}

# ------------------------------------------------------------
# 1. Detectar gerenciador de pacotes
# ------------------------------------------------------------
detect_pkg_manager() {
    if command -v apt >/dev/null 2>&1; then
        PKG="apt"
    elif command -v dnf >/dev/null 2>&1; then
        PKG="dnf"
    elif command -v pacman >/dev/null 2>&1; then
        PKG="pacman"
    elif command -v zypper >/dev/null 2>&1; then
        PKG="zypper"
    else
        PKG="unknown"
    fi
    echo -e "${BLUE}[INFO] Gerenciador de pacotes detectado: ${PKG}${NC}"
}

# ------------------------------------------------------------
# 2. Liberar e otimizar RAM
# ------------------------------------------------------------
free_ram() {
    echo -e "\n${CYAN}=== Liberando e otimizando RAM ===${NC}"

    echo -e "${YELLOW}Memória antes:${NC}"
    free -h

    # Sincroniza e limpa caches de página, dentries e inodes
    sync
    echo 3 > /proc/sys/vm/drop_caches
    echo -e "${GREEN}[OK] Caches de página, dentries e inodes limpos.${NC}"

    # Limpa swap se estiver usando pouco (opcional e seguro)
    if [[ $(swapon --show | wc -l) -gt 1 ]]; then
        if confirm "Deseja limpar a swap também? (recomendado se estiver com pouca memória livre)"; then
            swapoff -a && swapon -a
            echo -e "${GREEN}[OK] Swap limpa e reativada.${NC}"
        fi
    fi

    echo -e "${YELLOW}Memória depois:${NC}"
    free -h
}

# ------------------------------------------------------------
# 3. Otimizar / limpar disco
# ------------------------------------------------------------
clean_disk() {
    echo -e "\n${CYAN}=== Limpando e otimizando disco ===${NC}"

    # Espaço antes
    echo -e "${YELLOW}Espaço em disco antes:${NC}"
    df -h / | tail -1

    # Limpeza de logs antigos do journald
    if command -v journalctl >/dev/null 2>&1; then
        journalctl --vacuum-time=7d
        echo -e "${GREEN}[OK] Logs do journald com mais de 7 dias removidos.${NC}"
    fi

    # Limpeza de arquivos temporários
    rm -rf /tmp/* 2>/dev/null
    rm -rf /var/tmp/* 2>/dev/null
    echo -e "${GREEN}[OK] /tmp e /var/tmp limpos.${NC}"

    # Limpeza específica por gerenciador
    case $PKG in
        apt)
            apt clean
            apt autoclean
            apt autoremove -y
            echo -e "${GREEN}[OK] Cache do APT e pacotes órfãos removidos.${NC}"
            ;;
        dnf)
            dnf clean all
            dnf autoremove -y
            echo -e "${GREEN}[OK] Cache do DNF e pacotes órfãos removidos.${NC}"
            ;;
        pacman)
            pacman -Sc --noconfirm
            # Remove órfãos
            orphans=$(pacman -Qtdq)
            if [[ -n "$orphans" ]]; then
                pacman -Rns $orphans --noconfirm
                echo -e "${GREEN}[OK] Pacotes órfãos removidos.${NC}"
            else
                echo -e "${GREEN}[OK] Nenhum pacote órfão encontrado.${NC}"
            fi
            ;;
        zypper)
            zypper clean --all
            zypper packages --unneeded | awk 'NR>2 {print $5}' | xargs -r zypper remove -y
            echo -e "${GREEN}[OK] Cache do Zypper limpo.${NC}"
            ;;
        *)
            echo -e "${YELLOW}[AVISO] Gerenciador desconhecido. Limpeza de cache de pacotes pulada.${NC}"
            ;;
    esac

    # Limpa thumbnails antigos do usuário (se existir)
    if [[ -d /home ]]; then
        find /home -type d -name ".thumbnails" -exec rm -rf {} + 2>/dev/null
        find /home -type d -name "thumbnails" -exec rm -rf {} + 2>/dev/null
        echo -e "${GREEN}[OK] Thumbnails antigos removidos.${NC}"
    fi

    # Espaço depois
    echo -e "${YELLOW}Espaço em disco depois:${NC}"
    df -h / | tail -1
}

# ------------------------------------------------------------
# 4. Definir CPU para máxima performance
# ------------------------------------------------------------
set_cpu_performance() {
    echo -e "\n${CYAN}=== Configurando CPU para máxima performance ===${NC}"

    # Verifica se o governor está disponível
    if [[ ! -d /sys/devices/system/cpu/cpu0/cpufreq ]]; then
        echo -e "${YELLOW}[AVISO] cpufreq não disponível (talvez seja máquina virtual ou kernel sem suporte).${NC}"
        return
    fi

    # Lista governadores disponíveis
    available=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors 2>/dev/null)
    echo -e "${BLUE}Governadores disponíveis: $available${NC}"

    if echo "$available" | grep -q "performance"; then
        for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            echo "performance" > "$cpu" 2>/dev/null
        done
        echo -e "${GREEN}[OK] Todos os núcleos definidos para 'performance'.${NC}"

        # Mostra frequência atual
        echo -e "${YELLOW}Frequências atuais:${NC}"
        grep MHz /proc/cpuinfo | head -n $(nproc)
    else
        echo -e "${YELLOW}[AVISO] Governor 'performance' não disponível.${NC}"
    fi

    # Desativa alguns recursos de economia de energia (opcional)
    if confirm "Deseja também desativar o Intel P-State em modo passive / forçar max (se aplicável)?"; then
        if [[ -f /sys/devices/system/cpu/intel_pstate/status ]]; then
            echo "active" > /sys/devices/system/cpu/intel_pstate/status 2>/dev/null
            echo -e "${GREEN}[OK] Intel P-State ajustado.${NC}"
        fi
    fi
}

# ------------------------------------------------------------
# 5. Remover processos residentes desnecessários
# ------------------------------------------------------------
kill_unnecessary() {
    echo -e "\n${CYAN}=== Processos residentes (cuidado!) ===${NC}"

    echo -e "${YELLOW}Processos que mais consomem memória agora:${NC}"
    ps aux --sort=-%mem | head -15

    echo
    echo -e "${RED}ATENÇÃO: Matar processos pode fechar programas importantes!${NC}"
    echo "Exemplos comuns de processos que as pessoas costumam matar:"
    echo "  - tracker-miner / tracker-store (indexação GNOME)"
    echo "  - evolution-calendar-factory, evolution-source-registry"
    echo "  - snapd (se não usa snaps)"
    echo "  - packagekitd"
    echo "  - alguns agentes de atualização automática"

    if confirm "Deseja tentar matar processos comuns de indexação e atualização automática?"; then
        # Lista de processos "seguros" para tentar matar (não críticos do sistema)
        targets=(
            "tracker-miner-fs"
            "tracker-extract"
            "tracker-store"
            "evolution-calendar-factory"
            "evolution-source-registry"
            "evolution-addressbook-factory"
            "packagekitd"
            "gnome-software"
            "update-notifier"
        )

        for proc in "${targets[@]}"; do
            if pgrep -x "$proc" >/dev/null; then
                pkill -x "$proc" && echo -e "${GREEN}[OK] Processo $proc finalizado.${NC}" || echo -e "${YELLOW}[AVISO] Não foi possível matar $proc${NC}"
            fi
        done
    fi

    echo
    if confirm "Deseja abrir o htop para matar processos manualmente? (recomendado)"; then
        if command -v htop >/dev/null; then
            htop
        else
            echo -e "${YELLOW}htop não instalado. Use: top ou instale com seu gerenciador de pacotes.${NC}"
            top
        fi
    fi
}

# ------------------------------------------------------------
# 6. Verificar pacotes órfãos (detalhado)
# ------------------------------------------------------------
check_orphans() {
    echo -e "\n${CYAN}=== Verificando pacotes órfãos / não necessários ===${NC}"

    case $PKG in
        apt)
            echo -e "${YELLOW}Pacotes que podem ser removidos (autoremove):${NC}"
            apt autoremove --dry-run
            if confirm "Deseja remover os pacotes listados acima?"; then
                apt autoremove -y
            fi
            ;;
        dnf)
            echo -e "${YELLOW}Pacotes não necessários:${NC}"
            dnf autoremove --dry-run
            if confirm "Deseja remover?"; then
                dnf autoremove -y
            fi
            ;;
        pacman)
            orphans=$(pacman -Qtdq)
            if [[ -n "$orphans" ]]; then
                echo -e "${YELLOW}Pacotes órfãos encontrados:${NC}"
                echo "$orphans"
                if confirm "Deseja remover estes pacotes órfãos?"; then
                    pacman -Rns $orphans --noconfirm
                fi
            else
                echo -e "${GREEN}Nenhum pacote órfão encontrado.${NC}"
            fi
            ;;
        zypper)
            echo -e "${YELLOW}Pacotes não necessários:${NC}"
            zypper packages --unneeded
            ;;
        *)
            echo -e "${YELLOW}Gerenciador não suportado para verificação de órfãos.${NC}"
            ;;
    esac
}

# ------------------------------------------------------------
# 7. Executar TRIM em SSDs
# ------------------------------------------------------------
trim_ssd() {
    echo -e "\\n${CYAN}=== Otimizando SSD com TRIM ===${NC}"

    if ! command -v fstrim >/dev/null 2>&1; then
        echo -e "${YELLOW}[AVISO] fstrim não está disponível neste sistema.${NC}"
        return
    fi

    echo -e "${YELLOW}Dispositivos de bloco detectados:${NC}"
    lsblk -o NAME,TYPE,ROTA,SIZE,MOUNTPOINTS 2>/dev/null || true

    if confirm "Deseja executar fstrim em todos os sistemas de arquivos montados?"; then
        fstrim -av 2>&1 || echo -e "${YELLOW}[AVISO] Alguns pontos de montagem não aceitaram TRIM.${NC}"
        echo -e "${GREEN}[OK] TRIM concluído onde suportado.${NC}"
    else
        echo -e "${YELLOW}[INFO] TRIM cancelado.${NC}"
    fi
}

# ------------------------------------------------------------
# 8. Ajustar parâmetros de memória e I/O do kernel
# ------------------------------------------------------------
optimize_kernel() {
    echo -e "\\n${CYAN}=== Ajustando parâmetros do kernel ===${NC}"
    echo -e "${YELLOW}Os ajustes são temporários e podem ser revertidos com a reinicialização.${NC}"
    echo "  vm.swappiness: $(sysctl -n vm.swappiness 2>/dev/null || echo indisponível)"
    echo "  vm.vfs_cache_pressure: $(sysctl -n vm.vfs_cache_pressure 2>/dev/null || echo indisponível)"
    echo "  vm.dirty_ratio: $(sysctl -n vm.dirty_ratio 2>/dev/null || echo indisponível)"

    if ! confirm "Aplicar perfil equilibrado para desktop (swappiness=10, cache_pressure=50, dirty_ratio=10)?"; then
        echo -e "${YELLOW}[INFO] Ajustes do kernel cancelados.${NC}"
        return
    fi

    sysctl -w vm.swappiness=10 2>/dev/null || true
    sysctl -w vm.vfs_cache_pressure=50 2>/dev/null || true
    sysctl -w vm.dirty_ratio=10 2>/dev/null || true
    sysctl -w vm.dirty_background_ratio=5 2>/dev/null || true
    echo -e "${GREEN}[OK] Perfil de memória e I/O aplicado temporariamente.${NC}"
}

# ------------------------------------------------------------
# 9. Otimizar parâmetros de rede
# ------------------------------------------------------------
optimize_network() {
    echo -e "\\n${CYAN}=== Otimizando rede ===${NC}"
    echo -e "${YELLOW}Os ajustes são temporários e podem ser revertidos com a reinicialização.${NC}"
    echo "  net.ipv4.tcp_fastopen: $(sysctl -n net.ipv4.tcp_fastopen 2>/dev/null || echo indisponível)"
    echo "  net.ipv4.tcp_fin_timeout: $(sysctl -n net.ipv4.tcp_fin_timeout 2>/dev/null || echo indisponível)"
    echo "  net.core.default_qdisc: $(sysctl -n net.core.default_qdisc 2>/dev/null || echo indisponível)"

    if ! confirm "Aplicar ajustes seguros de latência TCP e fila de rede?"; then
        echo -e "${YELLOW}[INFO] Ajustes de rede cancelados.${NC}"
        return
    fi

    sysctl -w net.ipv4.tcp_fastopen=3 2>/dev/null || true
    sysctl -w net.ipv4.tcp_fin_timeout=30 2>/dev/null || true
    sysctl -w net.core.default_qdisc=fq 2>/dev/null || true
    echo -e "${GREEN}[OK] Perfil de rede aplicado onde suportado.${NC}"
}

# ------------------------------------------------------------
# 10. Exibir relatório de saúde do sistema
# ------------------------------------------------------------
system_health_report() {
    echo -e "\\n${CYAN}=== Relatório avançado de saúde do sistema ===${NC}"
    echo -e "${YELLOW}Uptime:${NC}"
    uptime -p 2>/dev/null || uptime
    echo -e "${YELLOW}Carga:${NC}"
    uptime | sed 's/^.*load average: //' || true
    echo -e "${YELLOW}Memória:${NC}"
    free -h
    echo -e "${YELLOW}Discos:${NC}"
    df -hT --exclude-type=tmpfs --exclude-type=devtmpfs 2>/dev/null || df -h
    echo -e "${YELLOW}Swap:${NC}"
    swapon --show 2>/dev/null || echo "Nenhuma swap ativa."
    echo -e "${YELLOW}Temperatura disponível:${NC}"
    if command -v sensors >/dev/null 2>&1; then
        sensors 2>/dev/null || echo "Sensores não disponíveis."
    else
        echo "Instale lm-sensors para consultar temperaturas."
    fi
}

# ------------------------------------------------------------
# Menu separado de otimização
# ------------------------------------------------------------
menu_otimizacao() {
    while true; do
        clear
        echo -e "${CYAN}=== Menu de otimização ===${NC}"
        echo "  1) Liberar / otimizar RAM"
        echo "  2) Limpar e otimizar disco"
        echo "  3) Definir CPU para máxima performance"
        echo "  4) Executar todas as otimizações básicas"
        echo "  5) Executar TRIM em SSDs"
        echo "  6) Ajustar memória e I/O do kernel"
        echo "  7) Otimizar parâmetros de rede"
        echo "  8) Exibir relatório avançado de saúde"
        echo "  9) Executar todas as otimizações avançadas"
        echo "  0) Voltar ao menu principal"
        echo
        read -p "Opção: " opcao_otimizacao

        case $opcao_otimizacao in
            1) clear; free_ram; pause ;;
            2) clear; clean_disk; pause ;;
            3) clear; set_cpu_performance; pause ;;
            4)
                clear
                free_ram
                clean_disk
                set_cpu_performance
                echo -e "\\n${GREEN}=== Otimização completa finalizada ===${NC}"
                pause
                ;;
            5) clear; trim_ssd; pause ;;
            6) clear; optimize_kernel; pause ;;
            7) clear; optimize_network; pause ;;
            8) clear; system_health_report; pause ;;
            9)
                clear
                free_ram
                clean_disk
                set_cpu_performance
                trim_ssd
                optimize_kernel
                optimize_network
                echo -e "\\n${GREEN}=== Otimizações avançadas finalizadas ===${NC}"
                pause
                ;;
            0) return 0 ;;
            *) echo -e "${RED}Opção inválida!${NC}"; pause ;;
        esac
    done
}

# ------------------------------------------------------------
# Menu principal
# ------------------------------------------------------------
main_menu() {
    detect_pkg_manager

    while true; do
        echo
        echo -e "${CYAN}Escolha uma opção:${NC}"
        echo "  1) Liberar / otimizar RAM"
        echo "  2) Limpar e otimizar disco"
        echo "  3) Definir CPU para máxima performance"
        echo "  4) Remover processos residentes desnecessários"
        echo "  5) Verificar e remover pacotes órfãos"
        echo "  6) Executar TUDO (recomendado com atenção)"
        echo "  7) Abrir menu separado de otimização"
        echo "  0) Sair"
        echo
        read -p "Opção: " opcao

        case $opcao in
            1) clear; free_ram; pause ;;
            2) clear; clean_disk; pause ;;
            3) clear; set_cpu_performance; pause ;;
            4) clear; kill_unnecessary; pause ;;
            5) clear; check_orphans; pause ;;
            6)
                clear
                free_ram
                clean_disk
                set_cpu_performance
                check_orphans
                kill_unnecessary
                echo -e "\n${GREEN}=== Manutenção completa finalizada ===${NC}"
                pause
                ;;
            7) menu_otimizacao ;;
            0) echo -e "${GREEN}Saindo...${NC}"; exit 0 ;;
            *) echo -e "${RED}Opção inválida!${NC}" ;;
        esac
    done
}

# Inicia
main_menu
