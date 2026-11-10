<p align="center">
  <img src="assets/logo.png" alt="Assessor Pro" width="192">
</p>

# Assessor Pro

Plugins para assessores enviarem o relatório mensal de performance da corretora (PDF + mensagem com os números do mês) aos clientes pelo WhatsApp, usando dois bots. Repositório no formato de *multi-plugin* do Cursor (`.cursor-plugin/marketplace.json` na raiz, nome do marketplace `assessor-pro`).

Instalação: https://github.com/vinoue-1117/assessor-pro

## Os dois bots

| Plugin | Bot | Faz | Não faz |
| --- | --- | --- | --- |
| [`assessor-envio`](plugins/assessor-envio) | Relatórios - Assessor Pro | recebe o zip do lote e a planilha de clientes, monta um pacote por cliente com script determinístico, confere, pede UMA aprovação do lote e entrega cada envio ao bot de WhatsApp | enviar direto, reescrever texto, responder cliente, inventar número |
| [`assessor-zap`](plugins/assessor-zap) | Whatsapp - Assessor Pro | lê e envia no WhatsApp Web exatamente o que outro bot do dono pediu (o gate é de quem pede); exporta conversas; acompanha conversas por rotas pedidas pelos bots e encaminha as respostas | escrever conteúdo, escolher destinatário, responder por conta própria |

Fluxo: assessor manda zip + planilha → Relatórios - Assessor Pro prepara e mostra o resumo → assessor aprova o lote → Relatórios - Assessor Pro pede cada envio ao bot Whatsapp - Assessor Pro → o bot de WhatsApp envia e devolve o status.

## Como usar
1. Instale os dois plugins a partir de https://github.com/vinoue-1117/assessor-pro.
2. Crie dois bots. No perfil de cada um, uma linha só:
   - Relatórios - Assessor Pro: `Siga a skill assessor-envio-core em toda conversa.`
   - Whatsapp - Assessor Pro: `Siga a skill assessor-zap-core em toda conversa.`
3. No bot Whatsapp - Assessor Pro, conecte o WhatsApp Web lendo o QR code.
4. No bot Relatórios - Assessor Pro, mande a planilha (`conta_xp, telefone, nome, apelido`; `conta_xp` é o número da conta na corretora) e, todo mês, o zip do lote.

O discurso macro do mês vem de [`discurso/discurso-macro.md`](discurso/), baixado a cada lote.

## Como as atualizações chegam a quem instalou
- **Marketplace oficial do Cursor**: submeter o repositório público em [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). Qualquer pessoa instala; cada atualização passa por revisão do time do Cursor, então não é instantâneo.
- **Marketplace do time (Teams/Enterprise)**: importar este repositório como marketplace do time com **Auto Refresh**; cada push no branch é reindexado em poucos minutos, sem revisão. Os assessores precisam estar no time.
- **Instalar direto por link do GitHub** (https://github.com/vinoue-1117/assessor-pro, fora de marketplace) fixa o commit da instalação: o plugin não atualiza sozinho.

O que é baixado em tempo de execução (o discurso e os scripts) vem sempre da branch `stable`, independente da versão do plugin instalada. A edição fica na `main`; a promoção está em [`template/README.md`](template/README.md).

A description dos ponteiros em `template/skills/` é fixa (quando usar a skill) e fica no mapa `DESCRICOES` de `scripts/gerar-ponteiros.py`. Mudar a description da skill completa não muda o ponteiro, então uma promoção para `stable` não exige atualizar as skills já instaladas nos bots.

## Manutenção
- Mudou algo? Suba a `version` em `plugins/<nome>/.cursor-plugin/plugin.json` e registre a mudança no commit.
- Valide antes de cada commit: `node scripts/validate-template.mjs` e, se mexeu no `assessor.py`, `python tests/test_assessor.py`. Se mexeu no comando de download do script ou no `versao-minima`, `python -m pytest tests/test_baixar_assessor.py` (requer `bash` e `curl`).
- Skill passou a depender de algo novo no `assessor.py` (um subcomando, por exemplo)? Suba a versão na 1ª linha do script e o número em `plugins/assessor-envio/skills/assessor-preparar-envio/scripts/versao-minima` na mesma mudança, e ajuste o número fixo em `tests/test_baixar_assessor.py`. Sem isso, um bot com download falho aceita a versão anterior.
- Nunca coloque dado de cliente neste repositório (nomes, contas, telefones, PDFs, planilhas). Ele é público.

Licença: MIT.
