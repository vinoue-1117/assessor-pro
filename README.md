<p align="center">
  <img src="assets/logo.png" alt="Assessor Pro" width="192">
</p>

# Assessor Pro

Bots para assessores enviarem o relatório mensal de performance da corretora (PDF + mensagem com os números do mês) aos clientes pelo WhatsApp, usando dois bots. Cada bot tem uma pasta em [`bots/`](bots/README.md), com a ficha que o define (`bot.md`) e as skills dele.

## Os dois bots

| Pasta | Bot | Faz | Não faz |
| --- | --- | --- | --- |
| [`assessor/envio`](bots/assessor/envio) | Relatórios - Assessor Pro | recebe o zip do lote e a planilha de clientes, monta um pacote por cliente com script determinístico, confere, pede UMA aprovação do lote e entrega cada envio ao bot de WhatsApp | enviar direto, reescrever texto, responder cliente, inventar número |
| [`assessor/zap`](bots/assessor/zap) | Whatsapp - Assessor Pro | lê e envia no WhatsApp Web exatamente o que outro bot do dono pediu (o gate é de quem pede); exporta conversas; acompanha conversas por rotas pedidas pelos bots e encaminha as respostas | escrever conteúdo, escolher destinatário, responder por conta própria |

Fluxo: assessor manda zip + planilha → Relatórios - Assessor Pro prepara e mostra o resumo → assessor aprova o lote → Relatórios - Assessor Pro pede cada envio ao bot Whatsapp - Assessor Pro → o bot de WhatsApp envia e devolve o status.

## Como usar

O dono dá um prompt por bot. Cole o prompt no chat desse bot. O bot ajusta a si mesmo.

No chat do bot Relatórios - Assessor Pro:

```
você é o bot de Relatórios do Assessor Pro; se não for, pare e diga que este prompt é para outro bot. Atualize suas skills seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md para o bot assessor/envio. Não apague nada do workspace.
```

No chat do bot Whatsapp - Assessor Pro:

```
você é o bot de WhatsApp do Assessor Pro; se não for, pare e diga que este prompt é para outro bot. Atualize suas skills seguindo https://raw.githubusercontent.com/vinoue-1117/assessor-pro/stable/bots/instalar.md para o bot assessor/zap. Não apague nada do workspace.
```

1. Cole cada prompt no chat do bot correspondente.
2. No bot Whatsapp - Assessor Pro, conecte o WhatsApp Web lendo o QR code.
3. No bot Relatórios - Assessor Pro, mande a planilha (`conta_xp, telefone, nome, apelido`; `conta_xp` é o número da conta na corretora) e, todo mês, o zip do lote.

O discurso macro do mês vem de [`discurso/discurso-macro.md`](discurso/), baixado a cada lote.

## Como as atualizações chegam a quem instalou
O bot instalado guarda só ponteiros: cada skill baixa a versão completa da branch `stable` a cada uso, e os scripts e o discurso vêm do mesmo lugar. A edição fica na `main`. Quem promove é o dono do repositório:

`git push origin main:stable`

O que fica gravado no bot é o perfil e a lista de ponteiros. Skill nova ou perfil alterado pedem colar de novo o prompt desse bot no chat dele. O bot segue o [`bots/instalar.md`](bots/instalar.md) e se ajusta.

A description de cada ponteiro é fixa (quando usar a skill) e fica na seção `## Skills` do `bot.md`. Mudar a description da skill completa não muda o ponteiro, então uma promoção para `stable` não exige atualizar as skills já instaladas nos bots.

## Manutenção
- Valide antes de cada commit: `python scripts/check.py`. Ele recusa arquivo de dado versionado, confere os ponteiros e roda os testes (os que executam o comando de download requerem `bash` e `curl` e são pulados no Windows). O mesmo comando roda em toda PR.
- Criou, removeu ou renomeou uma skill, ou mudou a linha dela no `bot.md`? Rode `python scripts/gerar-ponteiros.py`.
- Skill passou a depender de algo novo no `assessor.py` (um subcomando, por exemplo)? Suba a versão na 1ª linha do script e o número em `bots/assessor/envio/skills/assessor-preparar-envio/scripts/versao-minima` na mesma mudança, e ajuste o número fixo em `bots/assessor/tests/test_baixar_assessor.py`. Sem isso, um bot com download falho aceita a versão anterior.
- Nunca coloque dado de cliente neste repositório (nomes, contas, telefones, PDFs, planilhas). Ele é público. A lista do que não entra está em [`bots/README.md`](bots/README.md).
- Só o dono do repositório deve ter escrita nele.

Licença: MIT.
