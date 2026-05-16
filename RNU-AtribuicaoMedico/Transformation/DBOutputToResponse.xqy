(: 
   DBOutputToResponse.xqy
   Transformacao dos parametros de saida da stored procedure 
   igif.inscr_api_ws.atribuicao_medico_destino para a resposta AtribuicaoMedico
:)
declare namespace tns = "http://igif.min-saude.pt/rnu/atribuicaomedico";
declare namespace db = "http://xmlns.oracle.com/pcbpel/adapter/db/sp/AtribuicaoMedicoDestino";

declare variable $dbOutput as element(db:OutputParameters) external;

<tns:AtribuicaoMedicoResponse>
    <tns:CodigoResposta>{$dbOutput/db:P_COD_RESPOSTA/text()}</tns:CodigoResposta>
    <tns:MensagemResposta>{$dbOutput/db:P_MSG_RESPOSTA/text()}</tns:MensagemResposta>
    {
        if ($dbOutput/db:P_NOVO_PROC_FAM/text() != '') then
            <tns:NovoProcessoFamilia>{$dbOutput/db:P_NOVO_PROC_FAM/text()}</tns:NovoProcessoFamilia>
        else ()
    }
    {
        if ($dbOutput/db:P_COD_PARENTESCO/text() != '') then
            <tns:CodigoParentesco>{$dbOutput/db:P_COD_PARENTESCO/text()}</tns:CodigoParentesco>
        else ()
    }
</tns:AtribuicaoMedicoResponse>
