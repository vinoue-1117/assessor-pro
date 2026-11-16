<p align="center">
  <img src="assets/logo.png" alt="Assessor Pro" width="192">
</p>

# Assessor Pro

Bots para assessores enviarem o relatório mensal de performance da corretora (PDF + mensagem com os números do mês) aos clientes pelo WhatsApp, usando dois bots. O repositório guarda também o Analista, um bot de análise de mercado que não participa do envio. Cada bot tem uma pasta em [`bots/`](bots/README.md), com a ficha que o define (`bot.md`) e as skills dele.

## Os bots

| Pasta | Bot | Faz | Não faz |
| --- | --- | --- | --- |
| [`assessor/envio`](bots/assessor/envio) | Relatórios - Assessor Pro | recebe o zip do lote e a planilha de clientes, monta um pacote por cliente com script determinístico, confere, pede UMA aprovação do lote e entrega cada envio ao bot de WhatsApp | enviar direto, reescrever texto, responder cliente, inventar número |
| [`assessor/zap`](bots/assessor/zap) | Whatsapp - Assessor Pro | lê e envia no WhatsApp Web exatamente o que outro bot do dono pediu (o gate é de quem pede); exporta conversas; acompanha conversas por rotas pedidas pelos bots e encaminha as respostas | escrever conteúdo, escolher destinatário, responder por conta própria |
| [`analista`](bots/analista) | Analista | consulta cotação, histórico e opções pelo `yfinance`, Selic, CDI e IPCA no Banco Central e taxa do Tesouro Direto, faz as contas em Python e entrega tese ou comparação em Page, com os contras levantados e os números conferidos antes de publicar | mandar ordem, acessar corretora ou conta, falar com terceiros, inventar número |

Fluxo do envio: assessor manda zip + planilha → Relatórios - Assessor Pro prepara e mostra o resumo → assessor aprova o lote → Relatórios - Assessor Pro pede cada envio ao bot Whatsapp - Assessor Pro → o bot de WhatsApp envia e devolve o status.

## Como usar

Bot pessoal pode ser instalado pelo [bot construtor](docs/grokbot.md#bot-construtor), que é opcional: peça no chat dele, por exemplo "Leia o repo `https://github.com/vinoue-1117/assessor-pro` e instale os bots relatório/whatsapp". Bot de time, que o construtor não acessa, e bot pessoal sem o construtor são instalados com o prompt que está no README da pasta do bot, colado no chat dele. O mesmo prompt atualiza o bot e confere se ele está funcionando.

1. Instale os dois bots, pelo construtor ou com o prompt de cada um: [Relatórios - Assessor Pro](bots/assessor/envio/README.md#instalar) e [Whatsapp - Assessor Pro](bots/assessor/zap/README.md#instalar).
2. No bot Whatsapp - Assessor Pro, conecte o WhatsApp Web lendo o QR code.
3. No bot Relatórios - Assessor Pro, mande a planilha (`conta_xp, telefone, nome, apelido`; `conta_xp` é o número da conta na corretora) e, todo mês, o zip do lote.

O discurso macro do mês vem de [`discurso/discurso-macro.md`](discurso/), baixado a cada lote.

O Analista se instala do mesmo jeito, com o [prompt dele](bots/analista/README.md#instalar), e não depende dos outros dois.

## Como as atualizações chegam a quem instalou
O bot instalado guarda só ponteiros: cada skill baixa a versão completa da branch `stable` a cada uso, e os scripts e o discurso vêm do mesmo lugar. A edição fica na `main`. Quem promove é o dono do repositório:

`git push origin main:stable`

O que fica gravado é o perfil do bot e a lista de ponteiros. Bot de time guarda os ponteiros nas skills próprias. Bot do plano particular não guarda skill própria: os ponteiros ficam na biblioteca de skills do dono, vista por todo bot, e cada bot reconhece os seus pela pasta na URL ([`docs/grokbot.md`](docs/grokbot.md)). Skill nova ou perfil alterado pedem colar de novo o prompt desse bot no chat dele. O bot segue o [`bots/instalar.md`](bots/instalar.md) e se ajusta.

A description de cada ponteiro é fixa (quando usar a skill) e fica na seção `## Skills` do `bot.md`. Mudar a description da skill completa não muda o ponteiro, então uma promoção para `stable` não exige atualizar as skills já instaladas nos bots.

## Manutenção
- Valide antes de cada commit: `python scripts/check.py`. Ele recusa arquivo de dado versionado, confere os ponteiros e roda os testes (os que executam o comando de download requerem `bash` e `curl` e são pulados no Windows). O mesmo comando roda em toda PR.
- Criou, removeu ou renomeou uma skill, ou mudou a linha dela no `bot.md`? Rode `python scripts/gerar-ponteiros.py`.
- Avaliação de mudança de skill (dry run do fluxo com avaliação do transcript, análise de live run, com o avaliador sobre o export do bot real, e amostras de variantes lidas pelo dono no eixo de gosto): [`evals/`](evals/README.md).
- Skill passou a depender de algo novo no `assessor.py` (um subcomando, por exemplo)? Suba a versão na 1ª linha do script e o número em `bots/assessor/envio/skills/assessor-preparar-envio/scripts/versao-minima` na mesma mudança, e ajuste o número fixo em `bots/assessor/tests/test_baixar_assessor.py`. Sem isso, um bot com download falho aceita a versão anterior. O `mercado.py` do Analista segue a mesma regra, descrita no [README dele](bots/analista/README.md).
- Nunca coloque dado de cliente neste repositório (nomes, contas, telefones, PDFs, planilhas). Ele é público. A lista do que não entra está em [`bots/README.md`](bots/README.md).
- Só o dono do repositório deve ter escrita nele.

Licença: MIT.
