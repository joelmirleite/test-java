# ============================================================================
# WLST Script para importar o projeto RNU-AtribuicaoMedico no Oracle Service Bus
#
# Uso:
#   1. Copiar o ficheiro RNU-AtribuicaoMedico.sbar para o servidor WebLogic
#   2. Executar via WLST:
#      $MW_HOME/oracle_common/common/bin/wlst.sh import_osb.py
#
#   Ou com parametros:
#      $MW_HOME/oracle_common/common/bin/wlst.sh import_osb.py <admin_url> <username> <password> <sbar_path>
#
# Exemplo:
#   $MW_HOME/oracle_common/common/bin/wlst.sh import_osb.py t3://localhost:7001 weblogic welcome1 /tmp/RNU-AtribuicaoMedico.sbar
# ============================================================================

import sys
import os

from java.io import FileInputStream
from java.util import HashMap
from java.util import HashSet
from java.util import ArrayList
from java.util import Collections

from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.sb.management.importexport import ALSBImportOperation
from com.bea.wli.config import Ref

# ============================================================================
# Configuracao - Alterar conforme o ambiente
# ============================================================================
ADMIN_URL  = 't3://localhost:7001'
USERNAME   = 'weblogic'
PASSWORD   = 'welcome1'
SBAR_PATH  = './RNU-AtribuicaoMedico.sbar'

# Verificar parametros da linha de comando
if len(sys.argv) > 1:
    ADMIN_URL = sys.argv[1]
if len(sys.argv) > 2:
    USERNAME = sys.argv[2]
if len(sys.argv) > 3:
    PASSWORD = sys.argv[3]
if len(sys.argv) > 4:
    SBAR_PATH = sys.argv[4]

SESSION_NAME = 'ImportAtribuicaoMedico_' + str(System.currentTimeMillis())

# ============================================================================
# Funcoes auxiliares
# ============================================================================

def create_session(session_mbean, session_name):
    """Cria uma sessao no Service Bus"""
    print '[INFO] Criar sessao: ' + session_name
    session_mbean.createSession(session_name)
    print '[INFO] Sessao criada com sucesso'

def activate_session(session_mbean, session_name):
    """Activa a sessao no Service Bus"""
    print '[INFO] Activar sessao: ' + session_name
    session_mbean.activateSession(session_name, 'Import do projeto RNU-AtribuicaoMedico')
    print '[INFO] Sessao activada com sucesso'

def discard_session(session_mbean, session_name):
    """Descarta a sessao no Service Bus"""
    print '[WARN] Descartar sessao: ' + session_name
    session_mbean.discardSession(session_name)
    print '[INFO] Sessao descartada'

def read_sbar_file(sbar_path):
    """Le o ficheiro .sbar e retorna os bytes"""
    print '[INFO] Ler ficheiro: ' + sbar_path
    file_input = FileInputStream(sbar_path)
    file_size = os.path.getsize(sbar_path)
    buffer = jarray.zeros(file_size, 'b')
    file_input.read(buffer)
    file_input.close()
    print '[INFO] Ficheiro lido: ' + str(file_size) + ' bytes'
    return buffer

# ============================================================================
# Script principal
# ============================================================================

def main():
    print '=' * 70
    print ' Import RNU-AtribuicaoMedico para Oracle Service Bus'
    print '=' * 70
    print ''
    print '[INFO] Admin URL : ' + ADMIN_URL
    print '[INFO] Username  : ' + USERNAME
    print '[INFO] SBAR Path : ' + SBAR_PATH
    print ''

    # Verificar se o ficheiro existe
    if not os.path.exists(SBAR_PATH):
        print '[ERRO] Ficheiro nao encontrado: ' + SBAR_PATH
        sys.exit(1)

    try:
        # Conectar ao servidor WebLogic
        print '[INFO] Conectar ao servidor WebLogic...'
        connect(USERNAME, PASSWORD, ADMIN_URL)
        print '[INFO] Conectado com sucesso'

        # Obter MBeans
        domainRuntime()
        session_mbean = findService(SessionManagementMBean.NAME, SessionManagementMBean.TYPE)
        
        # Criar sessao
        create_session(session_mbean, SESSION_NAME)

        # Obter ALSBConfigurationMBean para a sessao
        alsb_config_mbean = findService(
            ALSBConfigurationMBean.NAME + '.' + SESSION_NAME,
            ALSBConfigurationMBean.TYPE
        )

        # Ler ficheiro SBAR
        sbar_bytes = read_sbar_file(SBAR_PATH)

        # Upload do JAR
        print '[INFO] Upload do ficheiro SBAR...'
        alsb_config_mbean.uploadJarFile(sbar_bytes)
        print '[INFO] Upload concluido'

        # Obter informacao do JAR
        print '[INFO] Obter informacao do JAR...'
        jar_info = alsb_config_mbean.getImportJarInfo()
        import_plan = jar_info.getDefaultImportPlan()
        
        # Listar recursos a importar
        operations = import_plan.getOperations()
        print '[INFO] Recursos a importar: ' + str(operations.size())
        
        for op in operations.values():
            ref = op.getResourceRef()
            print '  -> ' + ref.getFullName() + ' [' + op.getOperation().toString() + ']'

        # Executar import
        print '[INFO] Executar import...'
        import_result = alsb_config_mbean.importUploaded(import_plan)
        
        # Verificar resultado
        if import_result.getFailed().isEmpty():
            print '[INFO] Import concluido com sucesso - todos os recursos importados'
        else:
            print '[WARN] Alguns recursos falharam:'
            for ref in import_result.getFailed():
                diagnostics = import_result.getImportDiagnostics(ref)
                print '  FALHA: ' + ref.getFullName()
                if diagnostics:
                    for diag in diagnostics:
                        print '    -> ' + diag.getMessage()

        # Verificar conflitos
        if not import_result.getConflicts().isEmpty():
            print '[WARN] Conflitos detectados:'
            for ref in import_result.getConflicts():
                print '  CONFLITO: ' + ref.getFullName()

        # Activar sessao
        activate_session(session_mbean, SESSION_NAME)

        print ''
        print '=' * 70
        print ' IMPORT CONCLUIDO COM SUCESSO'
        print ' Projeto: RNU-AtribuicaoMedico'
        print ' Endpoint: http://<host>:<port>/RNU-AtribuicaoMedico/ProxyService/AtribuicaoMedico_PS'
        print '=' * 70

    except Exception, e:
        print '[ERRO] Ocorreu um erro durante o import:'
        print str(e)
        # Tentar descartar a sessao em caso de erro
        try:
            discard_session(session_mbean, SESSION_NAME)
        except:
            pass
        raise e

    finally:
        # Desconectar
        try:
            disconnect()
        except:
            pass

# Executar
main()
