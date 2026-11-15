# O estado do envio é gravado só por script, nunca pelo bot à mão

Planilha de clientes, aprovação e histórico de envios são lidos e escritos por subcomando de script. O histórico mora fora da pasta do lote, que é recriada a cada preparo. Um bot gravando o estado linha a linha quebrou o formato com um motivo que continha vírgula, e a trava de reenvio deixou de ver quem já tinha recebido.

## Alternativas consideradas

O bot gravar os arquivos de estado diretamente. Guardar o histórico dentro da pasta do lote: preparar de novo apagaria o registro.
