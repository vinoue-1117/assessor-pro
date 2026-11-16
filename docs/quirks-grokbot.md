# Quirks do Grok Bot

O que a plataforma faz e que muda como se escreve uma skill ou como se avalia um bot. Cada quirk diz o que foi observado, o que isso muda e quantas vezes foi visto.

Fatos da plataforma que já têm dono ficam com ele: onde as skills ficam, o bot construtor e a atualização dos bots em [`grokbot.md`](grokbot.md); a limpeza do `/workspace` na instalação em [`bots/instalar.md`](../bots/instalar.md); o formato e o corte do export da conversa no contrato da skill [`live-run`](../.claude/skills/live-run/SKILL.md) e nos limites do live run em [`evals/README.md`](../evals/README.md).

## O que entra

Um quirk entra quando as seis condições abaixo valem. Falhou em uma, fica de fora. O teste vale para o quirk novo e para o já escrito.

1. **É da plataforma.** O comportamento vem do Grok Bot: uma ferramenta, um limite, uma permissão ou o que o bot faz por conta própria. Falha que vem de uma skill deste repositório vai para o catálogo de erros ou para o `anti-patterns.md` do fluxo.
2. **Não depende de um bot.** O quirk pode aparecer em qualquer bot da plataforma. O que só aparece com a skill ou o pedido de um bot fica de fora.
3. **Muda o que se faz.** Saber do quirk muda uma skill, a instalação, o ambiente de avaliação ou a leitura de um transcript. Fato sem efeito é curiosidade. Na dúvida, é curiosidade.
4. **Foi observado.** Veio de um transcript, de um export, de uma recusa da plataforma ou de um teste no bot real, com a condição em que apareceu. Suposição, documentação da plataforma não conferida e o que o bot diz sobre si mesmo ficam de fora. O texto não amplia além do que foi visto.
5. **Não tem dono melhor.** O fato que já está escrito onde age (`grokbot.md`, `instalar.md`, uma skill, o contrato da `live-run`) fica lá.
6. **Tem gatilho reconhecível.** O quirk diz em que situação aparece (a ferramenta, o tipo de bot, o plano), estreito o bastante para não casar com qualquer tarefa.

## Workspace

**Bots pessoais do mesmo dono parecem dividir o `/workspace`.** A limpeza de um bot apagou as cópias de outro.
- **Muda:** o bot que guarda estado grava na própria pasta (`/workspace/<bot>/`) e não lê nem apaga a pasta de outro bot.
- **Visto:** uma vez, num bot de teste do plano particular. Não foi conferido se arquivos de estado de dois bots colidem.

## Subagentes

**O subagente chamado pela ferramenta `Task` começa sem o histórico da conversa.** Ele recebe só o que a chamada passa.
- **Muda:** o que o subagente precisa saber vai na chamada, inclusive a regra que mora no script ou na skill. Um revisor isolado trata como afirmação sem dado o que não recebeu.
- **Visto:** no bot real, com o `subagent_type` `knowledgeWork`.

**O bot cria subagente que a skill não pediu.** Numa tese, o bot passou dados, rascunho, escolhas, correções e Page a um subagente `executor`, retomado várias vezes, que recebeu a conversa inteira.
- **Muda:** a regra de isolamento ("passe somente") vale só para o subagente que a skill nomeia. Cada subagente em série é mais espera para o dono. A skill que não quer delegação precisa dizer isso.
- **Visto:** uma vez, no bot real. O dry run, com Claude no papel do bot, nunca fez isso.

## Page

**O `WriteCanvas` recebe um módulo TSX, não markdown.** O módulo importa componentes de `grok/canvas` (`Page`, `Section`, `Text`, `Table`, `Grid`, `Columns`, `LineChart`, `BulletList`, `Callout`, `Properties`, `LinkCards`) e passa por compilação TypeScript.
- **Muda:** a skill descreve as seções pela função e deixa o componente com a skill `canvas` da plataforma.
- **Visto:** uma vez, no bot real.

**Erro de compilação da Page não publica e se remenda.** Erro de compilação ou de tipo mantém a revisão anterior e diz o que corrigir, e o bot corrige com `EditCanvas`. Um `>` solto em texto de JSX (`>90d`) quebra a compilação (`TS1382`).
- **Muda:** erro de compilação é passo normal da publicação, não falha da Page. A skill não manda parar nesse caso.
- **Visto:** uma vez, no bot real.

## Uso

**O tempo de uma conversa sai do CSV de uso, não do export.** O export da conversa não traz horário. O CSV de uso baixado da plataforma tem uma linha por requisição, com horário e tokens.
- **Muda:** o tempo que o dono espera pela resposta se mede pelo CSV, casando o horário das requisições com a conversa.
- **Visto:** no CSV de uso e em todo export.
