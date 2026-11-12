# assessor-envio

Plugin do bot **Relatórios - Assessor Pro**: prepara e confere o lote mensal do relatório de performance da corretora e entrega os envios ao bot de WhatsApp (plugin [`assessor-zap`](../assessor-zap)).

Perfil do bot: `Siga a skill assessor-envio-core em toda conversa.`

## Skills
| Skill | Quando |
| --- | --- |
| `assessor-envio-core` | sempre: persona, regras, setup do primeiro uso |
| `assessor-preparar-envio` | chegou o zip/planilha: monta os pacotes e pede aprovação do lote |
| `assessor-enviar-relatorio` | depois do "sim": pede cada envio ao bot de WhatsApp e registra o log |
| `assessor-envio-teste` | manda um pacote para o próprio assessor (chat "você") |
| `assessor-rastrear-apelido` | propõe a coluna `apelido` lendo como o assessor chama cada cliente |
| `assessor-ajustar-cliente` | adiciona, altera ou remove um cliente na planilha salva, por mensagem |
| `assessor-resumo-ultimo-envio` | resumo do último lote a partir do log |

## Script
`skills/assessor-preparar-envio/scripts/assessor.py` (Python 3 + `pdftotext`): descompacta o zip, lê cada PDF, cruza com a planilha e grava `/workspace/assessor/lote-<ref>/` com `relatorio.pdf` + `mensagem.txt` por conta e um `conferir-envios.csv` com status `pronto` / `revisar` / `bloqueado`. Sem IA no conteúdo.

Uso: `python3 assessor.py LOTE.zip CLIENTES.csv|.xlsx DISCURSO.md`. A planilha aceita variações de nome de coluna, linhas de título acima do cabeçalho e telefone com ou sem 55 (normalizado para `+55DDDNÚMERO`); apelido vazio usa o 1º nome sem mudar o status. O discurso precisa da linha `referência: MM/AAAA` igual ao mês do lote e de no máximo 550 caracteres; acima disso o preparo para. Conta sem histórico, com `-` no ano ou no 12M da carteira, sai sem essa janela no bloco "No ano / 12M", e o CDI acompanha a carteira. Dado da tabela de referências que não for lido (CDI, Ibovespa ou IPCA do mês; janelas da carteira; CDI das janelas) fica fora da mensagem, sem traço no lugar e sem bloquear a conta, e a coluna `aviso` registra `mensagem sem: …`. Sem patrimônio, rentabilidade do mês ou resultado, a conta sai `bloqueado`. Conta cuja mensagem passe de 1.024 caracteres (limite da legenda de anexo do WhatsApp) sai `bloqueado`. A saída termina com `CODIGO <código>`, a impressão digital do conteúdo do lote.

Limpeza da planilha, antes de qualquer uso: `importar PLANILHA` lê a planilha do assessor como veio e grava a ativa, `/workspace/assessor/clientes.csv`, com as 4 colunas canônicas (conta só com dígitos, telefone em +55 quando válido, espaços colapsados); a anterior vira `clientes.bak-*`. Preparo, `cliente.py` e rastreio de apelidos leem só esse arquivo.

Estado do envio, sempre gravado pelo script (o bot não escreve CSV à mão):
- `aprovar REF CODIGO [CONTAS_REVISAR…]`: grava `lote-<ref>/aprovacao.json`, só se o código for o do lote atual.
- `checar [REF]`: confere `historico-envios.csv` (colunas, data, horário, status) e, com REF, o `conferir-envios.csv`, os pacotes e a aprovação; com tudo certo, imprime a fila (`ENVIAR` / `PULAR` / `JA_REGISTRADO`).
- `registrar REF CONTA STATUS [HH:MM]`: acrescenta a linha em `historico-envios.csv` (status `enviado`, `falhou: …`, `pulado: …` ou `teste: …`).
- `copiar REF CONTA` ou `copiar CAMINHO.txt`: lê o arquivo do disco e grava o conteúdo exato na área de transferência X11 (`xclip -selection clipboard`). Um argumento é o caminho do `.txt` (o que o bot de WhatsApp recebe no pedido); dois argumentos são `REF` e `CONTA`. Usa o `DISPLAY` do ambiente, que precisa ser o display do desktop do bot. Arquivo ausente: `falhou: arquivo não encontrado`. Sem parágrafo: `vazio`. Sem `xclip`, tenta `sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y xclip` em silêncio; se não instalar, sai com erro.
- `marcar`: troca a área de transferência por uma marca, depois do Ctrl+V. Um Ctrl+C que não aconteceu deixaria ali o texto do `copiar`, e a conferência bateria sem ler a caixa.
- `conferir-caixa REF CONTA` ou `conferir-caixa CAMINHO.txt`: só vale depois de `marcar`, uma vez. Lê a área de transferência (`xclip -o -selection clipboard`), que o bot preencheu com Ctrl+A e Ctrl+C na caixa, e compara com o `.txt` por parágrafos (quebra real, ignora linha em branco e espaço nas pontas, normaliza CRLF e NBSP). Imprime `bate` ou `nao bate: <motivo>`. A trava de envio é esta, não a leitura da tela.

Download: toda skill que usa o script baixa o `assessor.py` da `stable` a cada execução, para um arquivo temporário, e só troca `/workspace/assessor/assessor.py` se a versão da 1ª linha for igual ou maior que a de `skills/assessor-preparar-envio/scripts/versao-minima`. Se o download falhar ou a versão for menor, a skill para sem usar a cópia do disco.

Checagem: `python tests/test_assessor.py` (sem PDFs reais; a leitura do texto extraído se confere com texto anonimizado, e a extração do PDF, com um lote real) e `python -m pytest tests/test_baixar_assessor.py` para os comandos de download do `assessor.py` e do `cliente.py` (requer `bash` e `curl`; no Windows os testes que executam o comando são pulados).

`skills/assessor-ajustar-cliente/scripts/cliente.py` (Python 3, sem dependências): `add`, `set` e `rm` na cópia salva. Grava `clientes.csv` e guarda a anterior como `clientes.bak-AAAAMMDD-HHMM.<ext>`. As skills o baixam da `stable` a cada execução do mesmo jeito que o `assessor.py`: arquivo temporário, conferência do prefixo `# cliente.py v` e só então a troca de `/workspace/assessor/cliente.py`.

## Entradas do assessor
- Planilha de clientes (.csv ou .xlsx) com conta, telefone e nome (apelido opcional), do jeito que o assessor tem; o bot limpa com `importar`. `conta_xp` é o número da conta na corretora.
- Zip do lote do relatório mensal de performance da corretora, enviado no chat todo mês.
