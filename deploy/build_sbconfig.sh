#!/bin/bash
# ============================================================================
# Script para gerar sbconfig.jar usando o OSB configjar offline tool
#
# Este script gera um sbconfig.jar valido para importar directamente
# na OSB Console via System Administration > Import/Export > Import Resources
#
# Pre-requisitos:
#   - Oracle Service Bus 12c instalado (nao precisa de estar a correr)
#   - Java JDK 1.7+ ou 1.8+
#   - Variavel MW_HOME ou OSB_HOME definida
#
# Uso:
#   ./build_sbconfig.sh
#   ./build_sbconfig.sh /caminho/para/osb_home
#   ./build_sbconfig.sh /caminho/para/osb_home /caminho/para/output
#
# Exemplo:
#   ./build_sbconfig.sh /u01/app/oracle/middleware/osb
#   ./build_sbconfig.sh $MW_HOME/osb
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$REPO_DIR/RNU-AtribuicaoMedico"

# Determinar OSB_HOME
if [ -n "$1" ]; then
    OSB_HOME="$1"
elif [ -n "$OSB_HOME" ]; then
    OSB_HOME="$OSB_HOME"
elif [ -n "$MW_HOME" ]; then
    # Tentar localizar OSB dentro do Middleware Home
    if [ -d "$MW_HOME/osb" ]; then
        OSB_HOME="$MW_HOME/osb"
    elif [ -d "$MW_HOME/Oracle_OSB1" ]; then
        OSB_HOME="$MW_HOME/Oracle_OSB1"
    else
        echo "[ERRO] Nao foi possivel encontrar o directorio OSB dentro de MW_HOME=$MW_HOME"
        echo "       Especifique o caminho do OSB_HOME como primeiro argumento."
        exit 1
    fi
else
    echo "[ERRO] OSB_HOME nao definido."
    echo ""
    echo "Uso: $0 <OSB_HOME> [OUTPUT_DIR]"
    echo ""
    echo "Exemplo:"
    echo "  $0 /u01/app/oracle/middleware/osb"
    echo "  $0 \$MW_HOME/osb"
    echo ""
    exit 1
fi

# Determinar directorio de output
if [ -n "$2" ]; then
    OUTPUT_DIR="$2"
else
    OUTPUT_DIR="$SCRIPT_DIR"
fi

# Verificar se o configjar tool existe
CONFIGJAR_HOME="$OSB_HOME/tools/configjar"
if [ ! -d "$CONFIGJAR_HOME" ]; then
    echo "[ERRO] Directorio configjar nao encontrado: $CONFIGJAR_HOME"
    echo "       Verifique se o OSB_HOME esta correcto: $OSB_HOME"
    exit 1
fi

if [ ! -f "$CONFIGJAR_HOME/configjar.sh" ]; then
    echo "[ERRO] configjar.sh nao encontrado em: $CONFIGJAR_HOME"
    exit 1
fi

# Verificar se o projecto existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[ERRO] Directorio do projecto nao encontrado: $PROJECT_DIR"
    exit 1
fi

# Criar directorio de output se nao existir
mkdir -p "$OUTPUT_DIR"

# Gerar ficheiro de settings temporario com caminhos absolutos
SETTINGS_FILE=$(mktemp /tmp/configjar-settings-XXXXX.xml)
cat > "$SETTINGS_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<configjarSettings xmlns="http://www.bea.com/alsb/tools/configjar/config">
    <source>
        <project dir="$PROJECT_DIR"/>
    </source>
    <configjar jar="$OUTPUT_DIR/sbconfig.jar">
        <projectLevel includeSystem="false"/>
    </configjar>
</configjarSettings>
EOF

echo "============================================================"
echo " Gerar sbconfig.jar - RNU-AtribuicaoMedico"
echo "============================================================"
echo ""
echo "[INFO] OSB_HOME    : $OSB_HOME"
echo "[INFO] Projecto    : $PROJECT_DIR"
echo "[INFO] Output      : $OUTPUT_DIR/sbconfig.jar"
echo "[INFO] Settings    : $SETTINGS_FILE"
echo ""

# Configurar ambiente
echo "[INFO] Configurar ambiente OSB..."
cd "$CONFIGJAR_HOME"
source setenv.sh

# Executar configjar
echo "[INFO] Executar configjar..."
./configjar.sh -settingsfile "$SETTINGS_FILE"
RESULT=$?

# Limpar ficheiro temporario
rm -f "$SETTINGS_FILE"

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo " sbconfig.jar GERADO COM SUCESSO"
    echo ""
    echo " Ficheiro: $OUTPUT_DIR/sbconfig.jar"
    echo " Tamanho : $(du -h "$OUTPUT_DIR/sbconfig.jar" | cut -f1)"
    echo ""
    echo " Para importar na OSB Console:"
    echo "   1. Aceder a OSB Console"
    echo "   2. System Administration > Import/Export"
    echo "   3. Import Resources"
    echo "   4. Selecionar $OUTPUT_DIR/sbconfig.jar"
    echo "   5. Confirmar e Activar as alteracoes"
    echo "============================================================"
else
    echo ""
    echo "[ERRO] Falha ao gerar sbconfig.jar (exit code: $RESULT)"
    exit $RESULT
fi
