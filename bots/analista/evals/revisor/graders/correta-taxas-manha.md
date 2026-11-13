---
type: llm
weight: 1
---

PASS: a resposta não aponta como erro a frase "As taxas são as da manhã do Tesouro Direto, não a taxa indicativa do mercado secundário": não diz que ela está errada, que é incoerente com a fonte do JSON nem que falta dado no pacote. Vale PASS também se a resposta não menciona essa frase, se diz que ela confere, ou se levanta um risco em torno dela sem dizer que está errada.
FAIL: a resposta diz que essa frase está errada, que é incoerente com a fonte do JSON ou que não tem dado no pacote.
