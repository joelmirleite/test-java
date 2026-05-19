# Guia de Testes - WebService AtribuicaoMedico

## 1. Deploy do Pacote OSB (.sbar)

### Pre-requisitos
- Oracle WebLogic Server com Oracle Service Bus instalado
- Datasource JNDI `eis/DB/igifDS` configurado e apontando para o schema IGIF
- Acesso a OSB Console ou JDeveloper

### Importar via OSB Console
1. Aceder a OSB Console: `http://<host>:<port>/sbconsole`
2. Clicar em **Create** > **Import Resources**
3. Selecionar o ficheiro `deploy/RNU-AtribuicaoMedico.sbar`
4. Confirmar a importacao dos recursos
5. Clicar em **Activate** para ativar as alteracoes

### Importar via JDeveloper
1. Abrir JDeveloper e importar o projeto `RNU-AtribuicaoMedico/RNU-AtribuicaoMedico.jpr`
2. Fazer deploy para o servidor WebLogic configurado
3. Verificar na OSB Console que o Proxy Service esta ativo

### Endpoint do Servico
Apos deploy, o endpoint estara disponivel em:
```
http://<host>:<port>/RNU-AtribuicaoMedico/ProxyService/AtribuicaoMedico_PS
```

## 2. Testes com SoapUI

### Configuracao
1. Abrir SoapUI (versao 5.x ou superior)
2. Importar o projeto: `test/AtribuicaoMedico-soapui-project.xml`
3. Configurar as propriedades do projeto:
   - `OSB_HOST`: Hostname do servidor WebLogic (default: `localhost`)
   - `OSB_PORT`: Porta do servidor WebLogic (default: `7001`)

### Casos de Teste Disponiveis

#### Requests Individuais (Interface)
| Request | Descricao |
|---------|-----------|
| TC01_DadosValidos | Teste basico com dados validos (Parentesco: Proprio) |
| TC02_OutroUtente | Teste com outro utente (Parentesco: Conjuge) |
| TC03_ParentescoFilho | Teste com parentesco Filho |
| TC04_MesmaEquipa | Teste com mesma equipa origem/destino |
| TC05_NovoProcessoFamilia | Teste com PROC_FAM=0 (espera novo processo) |

#### Test Suite Automatizada
| Test Case | Descricao | Assertions |
|-----------|-----------|------------|
| TC01_FluxoNormal_DadosValidos | Fluxo normal completo | SOAP Response, Not SOAP Fault, Schema, CodigoResposta, MensagemResposta |
| TC02_ParentescoDiferente | Teste com Conjuge | SOAP Response, Not SOAP Fault, Schema, CodigoParentesco |
| TC03_NovoProcessoFamilia | PROC_FAM=0 | SOAP Response, Not SOAP Fault, Schema, NovoProcessoFamilia |

### Executar Test Suite
1. No SoapUI, expandir **AtribuicaoMedico_TestSuite**
2. Clicar com botao direito > **Run TestSuite**
3. Verificar os resultados (verde = sucesso, vermelho = falha)

## 3. Exemplo de Request SOAP (curl)

```bash
curl -X POST \
  "http://localhost:7001/RNU-AtribuicaoMedico/ProxyService/AtribuicaoMedico_PS" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H "SOAPAction: http://igif.min-saude.pt/rnu/atribuicaomedico/AtribuicaoMedico" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:atr="http://igif.min-saude.pt/rnu/atribuicaomedico">
   <soapenv:Header/>
   <soapenv:Body>
      <atr:AtribuicaoMedicoRequest>
         <atr:event_id>1001</atr:event_id>
         <atr:NNU>123456789</atr:NNU>
         <atr:DataNasc>1985-06-15T00:00:00</atr:DataNasc>
         <atr:SYS_ENTIDADES_ID_ORIGEM>500</atr:SYS_ENTIDADES_ID_ORIGEM>
         <atr:PRO_EQUIPA_ID_ORIGEM>10</atr:PRO_EQUIPA_ID_ORIGEM>
         <atr:PRO_EQUIPA_ID_DESTINO>20</atr:PRO_EQUIPA_ID_DESTINO>
         <atr:Parentesco>Proprio</atr:Parentesco>
         <atr:PROC_FAM>99001</atr:PROC_FAM>
      </atr:AtribuicaoMedicoRequest>
   </soapenv:Body>
</soapenv:Envelope>'
```

## 4. Resposta Esperada (Sucesso)

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Body>
      <tns:AtribuicaoMedicoResponse xmlns:tns="http://igif.min-saude.pt/rnu/atribuicaomedico">
         <tns:CodigoResposta>0</tns:CodigoResposta>
         <tns:MensagemResposta>Sucesso</tns:MensagemResposta>
         <tns:NovoProcessoFamilia>99010</tns:NovoProcessoFamilia>
         <tns:CodigoParentesco>P</tns:CodigoParentesco>
      </tns:AtribuicaoMedicoResponse>
   </soapenv:Body>
</soapenv:Envelope>
```

## 5. Stored Procedure

O servico invoca a stored procedure:
```
igif.inscr_api_ws.atribuicao_medico_destino
```

### Parametros IN
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| P_EVENT_ID | NUMBER | ID do evento |
| P_NNU | NUMBER | Numero Nacional de Utente |
| P_DATA_NASC | DATE | Data de nascimento |
| P_SYS_ENTIDADES_ID_ORIGEM | NUMBER | ID unidade origem |
| P_PRO_EQUIPA_ID_ORIGEM | NUMBER | ID equipa origem |
| P_PRO_EQUIPA_ID_DESTINO | NUMBER | ID equipa destino |
| P_PARENTESCO | VARCHAR2 | Grau de parentesco |
| P_PROC_FAM | NUMBER | Numero processo familia |

### Parametros OUT
| Parametro | Tipo | Descricao |
|-----------|------|-----------|
| P_COD_RESPOSTA | VARCHAR2 | Codigo de resposta |
| P_MSG_RESPOSTA | VARCHAR2 | Mensagem de resposta |
| P_NOVO_PROC_FAM | NUMBER | Novo processo familia (opcional) |
| P_COD_PARENTESCO | VARCHAR2 | Codigo parentesco (opcional) |
