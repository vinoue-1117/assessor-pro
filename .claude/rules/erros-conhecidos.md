# Erros conhecidos

Padrões de erro de comportamento já vistos neste repo. Antes de mexer em script ou skill de bot, conferir se a mudança repete algum deles.

| # | Padrão | Consequência | Regra |
|---|---|---|---|
| 1 | Mesma validação implementada em dois scripts (telefone em `assessor.py` e `cliente.py`) com regras diferentes | Um caminho aceitava telefone sem DDI (`11 9…` virava `+11…`, número dos EUA) enquanto o outro normalizava para +55 | Dado de entrada é validado e normalizado num ponto só, na entrada (`assessor.py importar`). Script que precisar da regra lê o dado já limpo, ou a cópia fica com docstring apontando a gêmea |
| 2 | Trava de conteúdo velho feita por texto sentinela ("ainda não publicado") | Depois do primeiro texto real, o do mês anterior seria reaproveitado sem aviso | Conteúdo periódico carrega o próprio período (`referência: MM/AAAA`) e o consumidor compara com o período em uso |
| 3 | Delimitador de CSV detectado só pela 1ª linha | Planilha com linha de título acima do cabeçalho caía no delimitador errado | Detectar sobre o arquivo todo (ou várias linhas), nunca só a primeira |
| 4 | LLM do bot gravando CSV de estado à mão, linha a linha | Motivo com vírgula sem aspas quebra as colunas e a trava de reenvio deixa de ver quem já recebeu | Estado (aprovação, histórico, planilha de clientes) é gravado só por subcomando de script com o módulo `csv`; a skill chama o script |
| 5 | Estado durável guardado dentro de pasta que o script recria (`lote-<ref>/`, apagada por `shutil.rmtree` a cada preparo) | Preparar de novo apagaria o registro de quem já recebeu | Estado que precisa sobreviver ao reprocessamento mora fora da pasta recriada (`historico-envios.csv` na raiz do workspace); a aprovação fica presa ao `codigo` do conteúdo |
