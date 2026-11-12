---
name: analista-tese
description: 'Use quando o pedido envolver tese, comparação, relatório ou estrutura em Page, com revisão adversarial antes de publicar.'
---

# Tese

Tese, comparação, relatório ou análise aprofundada sai como Page limpa, em pt-BR, depois de revisão adversarial. A Page é um memorando buy-side: texto fluido e objetivo, não formulário e não prova corrigida.

Número de mercado só entra se `analista-mercado` tiver trazido o JSON nesta conversa. Conta em Python, não de cabeça. Siga a persona de `analista-core`.

## 1. Dados

Siga `analista-mercado`: baixe o `mercado.py` com o comando de lá e rode a chamada que o pedido exige. Não use cópia antiga do disco.

Grave o pacote em `/tmp/analista-dados-<slug>.json` com `json.dump` em Python. Não monte esse JSON à mão. `<slug>` é o assunto em minúsculas, só `[a-z0-9-]`.

```json
{
  "mercado": [],
  "web": [{"titulo": "", "url": "", "data": "", "numeros": {}}],
  "contas": {}
}
```

- `mercado`: o JSON do script, sem editar número.
- `web`: só página que você abriu de fato, com a data do documento ou da publicação. Número de fundamento que a tese usa (lucro, receita, dívida) entra em `numeros` como está no documento, com a unidade e o período. Fundamento, resultado recente e notícia vêm da busca e da leitura web nativas deste bot. Confira a data do último trimestre divulgado e rode `historico` da última semana antes de concluir.
- `contas`: o que o Python imprimiu a partir de `mercado` e dos `numeros` de `web` (variação, múltiplo, assimetria, tamanho). Se a conta não sair do script, não entre na tese.

## 2. Rascunho

Escreva `/tmp/analista-rascunho-<slug>.md` com a decisão de alocação, a assimetria de upside contra downside, o tamanho sugerido, o catalisador, o horizonte e o que faria mudar de ideia. Cada número rastreável ao JSON.

## 3. Revisão adversarial

Rode um subagente `knowledgeWork` pela ferramenta `Task`, com `subagent_type` `knowledgeWork`. Esse subagente começa sem o histórico da conversa. Passe somente:

- o rascunho;
- o JSON de `/tmp/analista-dados-<slug>.json`;
- o papel: advogado do diabo. Conferir cada número contra o JSON (`mercado`, `numeros` de `web` e `contas`). Atacar premissa fraca. Apontar risco ou catalisador que falta. Listar gatilho objetivo de invalidação. Devolver veredito `sólida`, `frágil` ou `refazer`, com objeções concretas. Não reescrever a tese.

Não passe o chat, a memória nem um veredito pronto. Se o subagente não devolver veredito, pare e diga ao dono que a revisão não rodou. Não invente veredito e não publique.

## 4. Polimento

Se houver objeção válida ou o veredito for `frágil` ou `refazer`, corrija os números, incorpore as objeções e os riscos no próprio texto do rascunho e faça uma segunda passada no `knowledgeWork`. A revisão tem duas rodadas, para a tese não ficar presa nela. Se a segunda devolver `refazer`, não publique: diga ao dono no chat que a tese não passou na revisão e quais objeções ficaram. Se devolver `frágil`, publique com as objeções em `Riscos, limitações e premissas` e diga isso na linha de ressalva do chat.

Objeção que você aceita vira frase do memorando ou item de `Riscos, limitações e premissas`. Não fica como comentário de corretor no fim do arquivo.

## 5. Page

Publique a Page final com a skill `canvas`, pela ferramenta `WriteCanvas`. O conteúdo é o markdown polido. Se a Page não publicar, pare e diga ao dono qual foi o erro. Não cole o memorando no chat.

A Page tem texto corrido de buy-side, uma seção `## Riscos, limitações e premissas` e uma seção `## Fontes` com fonte, data e horário de cada número e de cada documento. O veredito e o texto do revisor são material de trabalho e ficam fora da Page.

## 6. Chat

Entregue o link da Page e a decisão de alocação (lado, tamanho sugerido, horizonte), curta. Se restou limitação de dado ou ressalva importante, uma linha curta a mais. Sem essa ressalva, não acrescente linha. Não cole o rascunho nem a crítica no chat.
