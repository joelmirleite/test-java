# Deploy do Projecto RNU-AtribuicaoMedico no Oracle Service Bus 12c

## Pré-requisitos

- Oracle Service Bus 12c (12.2.1.x) instalado
- Java JDK 1.8+
- Apache Ant (incluído no Middleware Home: `$MW_HOME/oracle_common/modules/thirdparty/ant`)
- Variável `OSB_HOME` definida (ex: `/u01/app/oracle/middleware/osb`)

## Gerar sbconfig.jar

O `sbconfig.jar` é um ficheiro com serialização Java binária interna do OSB — **não pode ser gerado manualmente**. É necessário usar o **configjar offline tool** incluído na instalação do OSB 12c.

### Opção 1: Via Script Shell (recomendado)

```bash
# Definir OSB_HOME se ainda não estiver definido
export OSB_HOME=/u01/app/oracle/middleware/osb

# Executar o script
cd deploy/
chmod +x build_sbconfig.sh
./build_sbconfig.sh $OSB_HOME
```

O script:
1. Valida que o configjar tool existe em `$OSB_HOME/tools/configjar/`
2. Gera um ficheiro de settings temporário com caminhos absolutos
3. Executa `configjar.sh` para produzir o `sbconfig.jar`
4. O ficheiro é gerado em `deploy/sbconfig.jar`

### Opção 2: Via Ant

```bash
# Definir variáveis de ambiente
export OSB_HOME=/u01/app/oracle/middleware/osb

# Executar Ant (a partir da raiz do repositório)
ant -f deploy/build.xml -Dosb.home=$OSB_HOME
```

### Opção 3: Via Linha de Comando Directa

```bash
# 1. Ir para o directório do configjar
cd $OSB_HOME/tools/configjar

# 2. Configurar o ambiente
source setenv.sh

# 3. Executar o configjar com o ficheiro de settings
#    (ajustar o caminho para o configjar-settings.xml)
./configjar.sh -settingsfile /caminho/para/deploy/configjar-settings.xml
```

**Nota:** O ficheiro `configjar-settings.xml` tem placeholders `${PROJECT_DIR}` e `${OUTPUT_DIR}` que precisam de ser substituídos com caminhos absolutos, ou usar o `build_sbconfig.sh` que faz isto automaticamente.

### Opção 4: Via Maven (se tiver Maven configurado)

```xml
<!-- Adicionar ao pom.xml do projecto -->
<plugin>
    <groupId>com.oracle.servicebus</groupId>
    <artifactId>oracle-servicebus-plugin</artifactId>
    <version>12.2.1-4-0</version>
    <configuration>
        <oracleHome>${env.ORACLE_HOME}</oracleHome>
    </configuration>
</plugin>
```

```bash
mvn package -DoracleHome=$ORACLE_HOME
```

## Importar na OSB Console

### Via Console Web (Import/Export)

1. Abrir a OSB Console: `http://<host>:7001/sbconsole`
2. Clicar em **Create** (iniciar sessão de edição)
3. Ir a **System Administration** → **Import/Export**
4. Clicar em **Import Resources**
5. Selecionar o ficheiro `sbconfig.jar` gerado
6. Confirmar os recursos a importar
7. Clicar em **Import**
8. Clicar em **Activate** para publicar as alterações

### Via WLST (alternativa programática)

```bash
# Usar o script WLST incluído
$MW_HOME/oracle_common/common/bin/wlst.sh deploy/import_osb.py \
    t3://localhost:7001 weblogic <password> deploy/RNU-AtribuicaoMedico.sbar
```

## Importar via .sbar (alternativa)

Se preferir importar o `.sbar` sem gerar o `sbconfig.jar`:

1. Abrir a OSB Console
2. Clicar em **Create** (iniciar sessão)
3. No menu **Create**, selecionar **Import Resources**
4. Selecionar `deploy/RNU-AtribuicaoMedico.sbar`
5. Confirmar e **Activate**

**Nota:** A importação via `.sbar` usa o caminho **Create > Import Resources**, não o caminho **System Administration > Import/Export**.

## Validações Após Deploy

Após importar com sucesso:

1. **Verificar o Proxy Service:**
   - Navegar para `RNU-AtribuicaoMedico` → `ProxyService` → `AtribuicaoMedico_PS`
   - Verificar que o endpoint está activo

2. **Verificar o Business Service:**
   - Navegar para `RNU-AtribuicaoMedico` → `BusinessService` → `AtribuicaoMedico_BS`
   - Confirmar que o JNDI `eis/DB/igifDS` está configurado no WebLogic

3. **Testar com SoapUI:**
   - Abrir `test/AtribuicaoMedico-soapui-project.xml` no SoapUI
   - Ajustar `OSB_HOST` e `OSB_PORT` nas propriedades do projecto
   - Executar `TC01_DadosValidos`

4. **Testar com curl:**
   ```bash
   curl -X POST \
     -H "Content-Type: text/xml" \
     -H "SOAPAction: \"atribuicaoMedicoDestino\"" \
     -d @- \
     http://<host>:<port>/RNU/AtribuicaoMedico \
     <<'EOF'
   <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                     xmlns:atr="http://igif.min-saude.pt/rnu/atribuicaomedico">
     <soapenv:Body>
       <atr:AtribuicaoMedicoRequest>
         <atr:event_id>12345</atr:event_id>
         <atr:NNU>123456789</atr:NNU>
         <atr:DataNasc>1990-01-15T00:00:00</atr:DataNasc>
         <atr:SYS_ENTIDADES_ID_ORIGEM>100</atr:SYS_ENTIDADES_ID_ORIGEM>
         <atr:PRO_EQUIPA_ID_ORIGEM>200</atr:PRO_EQUIPA_ID_ORIGEM>
         <atr:PRO_EQUIPA_ID_DESTINO>300</atr:PRO_EQUIPA_ID_DESTINO>
         <atr:Parentesco>Proprio</atr:Parentesco>
         <atr:PROC_FAM>50000</atr:PROC_FAM>
       </atr:AtribuicaoMedicoRequest>
     </soapenv:Body>
   </soapenv:Envelope>
   EOF
   ```

## Resolução de Problemas

| Erro | Solução |
|------|---------|
| `Invalid Config Jar` | O `.jar` não foi gerado pelo configjar tool do OSB. Regenerar usando `build_sbconfig.sh` |
| `configjar.sh not found` | Verificar que `$OSB_HOME/tools/configjar/` existe. Este tool está disponível a partir do OSB 11.1.1.7 (PS6) |
| `JNDI eis/DB/igifDS not found` | Configurar o DB Adapter connection factory no WebLogic Admin Console |
| `Stored procedure not found` | Verificar que `igif.inscr_api_ws.atribuicao_medico_destino` existe na base de dados |
| Erro ao importar `.sbar` | Usar o caminho **Create > Import Resources** (não System Administration) |

## Estrutura dos Ficheiros de Deploy

```
deploy/
├── build.xml                  # Ant build file para gerar sbconfig.jar
├── build_sbconfig.sh          # Script shell alternativo
├── configjar-settings.xml     # Settings para o configjar tool
├── import_osb.py              # Script WLST para importar .sbar
├── export_sbconfig.py         # Script WLST para exportar sbconfig.jar
├── RNU-AtribuicaoMedico.sbar  # Pacote deploy alternativo
└── README_Deploy.md           # Este ficheiro
```
