# ============================================================================
# WLST Script para EXPORTAR o projeto RNU-AtribuicaoMedico como sbconfig.jar
#
# Este script deve ser executado APOS o import via import_osb.py
# para gerar um sbconfig.jar valido que pode ser reutilizado.
#
# Uso:
#   $MW_HOME/oracle_common/common/bin/wlst.sh export_sbconfig.py
#
#   Ou com parametros:
#   $MW_HOME/oracle_common/common/bin/wlst.sh export_sbconfig.py <admin_url> <username> <password> <output_path>
#
# Exemplo:
#   $MW_HOME/oracle_common/common/bin/wlst.sh export_sbconfig.py t3://localhost:7001 weblogic welcome1 /tmp/sbconfig.jar
# ============================================================================

import sys
import os

from java.io import FileOutputStream
from java.util import HashSet

from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.config import Ref

# ============================================================================
# Configuracao - Alterar conforme o ambiente
# ============================================================================
ADMIN_URL   = 't3://localhost:7001'
USERNAME    = 'weblogic'
PASSWORD    = 'welcome1'
OUTPUT_PATH = './sbconfig.jar'

# Verificar parametros da linha de comando
if len(sys.argv) > 1:
    ADMIN_URL = sys.argv[1]
if len(sys.argv) > 2:
    USERNAME = sys.argv[2]
if len(sys.argv) > 3:
    PASSWORD = sys.argv[3]
if len(sys.argv) > 4:
    OUTPUT_PATH = sys.argv[4]

PROJECT_NAME = 'RNU-AtribuicaoMedico'

# ============================================================================
# Script principal
# ============================================================================

def main():
    print '=' * 70
    print ' Export RNU-AtribuicaoMedico como sbconfig.jar'
    print '=' * 70
    print ''

    try:
        # Conectar ao servidor WebLogic
        print '[INFO] Conectar ao servidor WebLogic...'
        connect(USERNAME, PASSWORD, ADMIN_URL)
        print '[INFO] Conectado com sucesso'

        # Obter ALSBConfigurationMBean (core data, sem sessao)
        domainRuntime()
        alsb_core_mbean = findService(
            ALSBConfigurationMBean.NAME,
            ALSBConfigurationMBean.TYPE
        )

        # Criar referencia ao projeto
        project_ref = Ref.makeProjectRef(PROJECT_NAME)

        # Obter todos os recursos do projeto
        print '[INFO] Obter recursos do projeto ' + PROJECT_NAME + '...'
        refs_to_export = HashSet()
        refs_to_export.add(project_ref)

        # Adicionar todos os recursos filhos do projeto
        all_refs = alsb_core_mbean.getRefs(project_ref)
        print '[INFO] Recursos encontrados: ' + str(all_refs.size())
        for ref in all_refs:
            refs_to_export.add(ref)
            print '  -> ' + ref.getFullName()

        # Exportar como JAR
        print '[INFO] Exportar como sbconfig.jar...'
        jar_bytes = alsb_core_mbean.export(refs_to_export, True)

        # Gravar ficheiro
        print '[INFO] Gravar ficheiro: ' + OUTPUT_PATH
        fos = FileOutputStream(OUTPUT_PATH)
        fos.write(jar_bytes)
        fos.close()

        file_size = os.path.getsize(OUTPUT_PATH)
        print '[INFO] Ficheiro gravado: ' + str(file_size) + ' bytes'

        print ''
        print '=' * 70
        print ' EXPORT CONCLUIDO COM SUCESSO'
        print ' Ficheiro: ' + OUTPUT_PATH
        print ' '
        print ' Este sbconfig.jar pode ser importado directamente'
        print ' na OSB Console via System Administration > Import/Export'
        print '=' * 70

    except Exception, e:
        print '[ERRO] Ocorreu um erro durante o export:'
        print str(e)
        raise e

    finally:
        try:
            disconnect()
        except:
            pass

# Executar
main()
