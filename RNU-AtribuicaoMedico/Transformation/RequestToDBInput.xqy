(: 
   RequestToDBInput.xqy
   Transformacao do pedido AtribuicaoMedico para os parametros de entrada 
   da stored procedure igif.inscr_api_ws.atribuicao_medico_destino
:)
declare namespace tns = "http://igif.min-saude.pt/rnu/atribuicaomedico";
declare namespace db = "http://xmlns.oracle.com/pcbpel/adapter/db/sp/AtribuicaoMedicoDestino";

declare variable $request as element(tns:AtribuicaoMedicoRequest) external;

<db:InputParameters>
    <db:P_EVENT_ID>{$request/tns:event_id/text()}</db:P_EVENT_ID>
    <db:P_NNU>{$request/tns:NNU/text()}</db:P_NNU>
    <db:P_DATA_NASC>{$request/tns:DataNasc/text()}</db:P_DATA_NASC>
    <db:P_SYS_ENTIDADES_ID_ORIGEM>{$request/tns:SYS_ENTIDADES_ID_ORIGEM/text()}</db:P_SYS_ENTIDADES_ID_ORIGEM>
    <db:P_PRO_EQUIPA_ID_ORIGEM>{$request/tns:PRO_EQUIPA_ID_ORIGEM/text()}</db:P_PRO_EQUIPA_ID_ORIGEM>
    <db:P_PRO_EQUIPA_ID_DESTINO>{$request/tns:PRO_EQUIPA_ID_DESTINO/text()}</db:P_PRO_EQUIPA_ID_DESTINO>
    <db:P_PARENTESCO>{$request/tns:Parentesco/text()}</db:P_PARENTESCO>
    <db:P_PROC_FAM>{$request/tns:PROC_FAM/text()}</db:P_PROC_FAM>
    <db:P_COD_RESPOSTA/>
    <db:P_MSG_RESPOSTA/>
    <db:P_NOVO_PROC_FAM/>
    <db:P_COD_PARENTESCO/>
</db:InputParameters>
