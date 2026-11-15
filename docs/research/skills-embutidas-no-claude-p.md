# Skills embutidas do Claude Code num `claude -p` headless

Acesso às fontes em 15/11/2026. Versão local observada: Claude Code 2.1.317 (`claude --version`, `claude --help`). Cada conclusão está marcada como **documentado** (com citação), **inferência** ou **em aberto**.

## Pergunta

Como esconder ou negar as skills embutidas do Claude Code (as que vêm com o produto, como `dataviz` e `artifact-design`) para um `claude -p` headless, mantendo as skills do projeto em `.claude/skills/`? E por que `--tools` com `Skill`, `--allowedTools` com `Skill(<nome>)` e `--permission-mode dontAsk` não barram a carga de uma skill que não está na lista?

## Resposta curta

1. **Documentado:** o mecanismo que mira só as embutidas é a setting `disableBundledSkills: true` (ou a variável `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1`). A doc diz que "Skills from plugins, `.claude/skills/`, and `.claude/commands/` are unaffected". Pode ir no JSON de `--settings`, que o comando já usa para `claudeMdExcludes`.
2. **Documentado:** para esconder skills nomeadas uma a uma, `skillOverrides` com `"off"` esconde a skill do modelo e do menu `/` e faz a invocação pelo nome completo devolver erro. Exige listar cada nome.
3. **Documentado:** as três opções atuais não restringem skills. `--tools` escolhe ferramentas, `--allowedTools` só pré-aprova, e `dontAsk` só nega o que pediria aprovação. A doc afirma que "When you add allow rules, Claude isn't limited to the skills they name."
4. **Documentado:** não há deny por lista aberta ("tudo menos estas N"). Deny aceita nome exato, prefixo `Skill(nome *)` e a forma `Skill(skill:<padrão com *>)`, sem negação. Um deny `Skill` sem especificador tira a ferramenta inteira, inclusive as skills do projeto.
5. **Testado na 2.1.317:** com `disableBundledSkills: true` no JSON do `--settings`, o `init` deixa de listar `dataviz` e `code-review`, e a ferramenta `Skill` devolve `Unknown skill` para `dataviz`, `artifact-design` e `code-review`. A skill de `.claude/skills/` segue carregando. Sobram no `init` `design`, `doctor` e `plugin-authoring`; das três, só `plugin-authoring` carrega, e `skillOverrides` `"off"` tira as três do `init` e recusa a carga. Detalhe em "Teste na versão 2.1.317".

## Mecanismos candidatos

| Mecanismo | O que desliga (segundo a doc) | Mantém as skills do projeto? | Funciona em `-p`? | Fonte |
|---|---|---|---|---|
| `disableBundledSkills: true` em `--settings` | "Claude Code removes bundled skills and workflows entirely, while built-in commands such as `/init` stay typable but are hidden from the model." Escopo: qualquer arquivo de settings | Sim: "Skills from plugins, `.claude/skills/`, and `.claude/commands/` are unaffected." | A doc não menciona `-p` à parte; a setting não é restrita a modo interativo (inferência) | settings-reference, seção `disableBundledSkills` |
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1` (ambiente) | Mesmo efeito da setting; "Equivalent to the `disableBundledSkills` setting". Para uma sessão | Sim (mesma frase) | Idem | env-vars; settings-reference ("Per-session overrides") |
| `skillOverrides: {"<nome>": "off"}` em `--settings` | `"off"`: skill oculta ao modelo e ao menu `/`; "Invoking a hidden skill by its full name returns the `skillOverrides` error instead of running it." A doc cita esta setting como o jeito de esconder uma embutida individual | Sim: só afeta as chaves listadas. "Plugin skills are not affected by `skillOverrides`." | A doc não restringe a `-p` (inferência) | skills, "Override skill visibility from settings" e "Remove a skill" |
| `permissions.deny: ["Skill(<nome>)"]` ou `--disallowedTools "Skill(<nome>)"` | Bloqueia a chamada da skill nomeada; alias e nome não qualificado também (tabela "Claude Code also blocks") | Sim, só as nomeadas | Regras de permissão valem em `-p` | skills, "Restrict Claude's skill access"; permissions |
| `Skill(skill:<padrão>)` em deny | Compara o parâmetro `skill` com `*` como curinga, e "matches the skill under any of its names" | Sim, para o que o padrão não casar | Idem | permissions, "Match by input parameter" |
| `permissions.deny: ["Skill"]` | "Disable all skills by denying the Skill tool". Deny com nome de ferramenta sem especificador "removes the tool from Claude's context entirely" | **Não.** Remove a ferramenta `Skill` para todas as skills | Sim | skills; permissions |
| `--disable-slash-commands` | "Disable all skills and commands for this session" | **Não.** Desliga todas | Flag de CLI geral | cli-reference |
| `--bare` | Pula "auto-discovery of hooks, skills, custom commands, subagents, installed plugins, MCP servers, auto memory, and CLAUDE.md"; o Claude "doesn't get the list of available skills" | **Não** por descoberta: só skills de diretório passado em `--add-dir` carregam, e sem a lista de skills no contexto. Exige `ANTHROPIC_API_KEY` ou `apiKeyHelper` em `--settings`: "bare mode doesn't use your subscription login" | Sim, é pensado para `-p` | headless, "Start faster with bare mode"; cli-reference |
| `--safe-mode` | Desliga "CLAUDE.md, skills, plugins, hooks, MCP servers, custom commands and agents" etc. | **Não** (desliga skills) | A doc não restringe | cli-reference (`claude --help` local traz a mesma descrição) |
| `syncClaudeAiSkills: false` | Só as skills sincronizadas da conta claude.ai (`anthropic-skills:*`), não as embutidas | Sim | Aplica-se a sessões com login claude.ai | settings-reference |
| `strictPluginOnlyCustomization: ["skills"]` | Trava as skills de usuário e projeto; "It keeps loading bundled skills" | **Não** (corta as do projeto e mantém as embutidas: o oposto do necessário). Escopo só Managed | n/a | settings-reference |
| Opção `skills` do Agent SDK (lista de nomes) | "The model doesn't see unlisted skills and the Skill tool rejects them." Aceita só nomes exatos | Sim, para os nomes listados | É opção do SDK; a referência de flags da CLI que li não tem flag equivalente | agent-sdk/skills, "Allow only specific skills" |

Observações:

- **Observado, não documentado:** variáveis `CLAUDE_CODE_DISABLE_CLAUDE_API_SKILL` e `CLAUDE_CODE_DISABLE_CLAUDE_CODE_SKILL` aparecem como nomes de variável no binário local 2.1.317 e **não** aparecem nas páginas de env-vars nem de settings que li. Observado na versão 2.1.317 instalada; sem sustentação na doc, não usar como mecanismo.
- **Observado na versão 2.1.317 instalada:** o texto de erro embutido no binário descreve uma skill indisponível como "disabled, set to off in the skillOverrides setting, or turned off with every other bundled skill by the disableBundledSkills setting or CLAUDE_CODE_DISABLE_BUNDLED_SKILLS". Isso confirma que as três formas existem na versão local, mas não diz nada sobre o que a ferramenta `Skill` devolve ao modelo.

## Por que as três opções atuais não barram

### `--tools` com `Skill`

**Documentado:** `--tools` "Restrict which built-in tools Claude can use". Escolhe quais ferramentas existem. Com `Skill` na lista, a ferramenta existe para qualquer skill descoberta. A tabela de ferramentas descreve `Skill` como "Executes a skill within the main conversation" e não menciona filtro por nome. A doc não diz que `--tools` filtra skills. Tirar `Skill` da lista tiraria também as skills do projeto (inferência).

### `--allowedTools` com `Skill(<nome>)`

**Documentado (cli-reference):** `--allowedTools` são "Tools that execute without prompting for permission... To restrict which tools are available, use `--tools` instead."

**Documentado (skills):** "**Allow or deny specific skills** using permission rules. When you add allow rules, Claude isn't limited to the skills they name." Uma regra `Skill(a)` em allow não implica negar `Skill(b)`: a doc afirma o contrário, de forma explícita.

### `--permission-mode dontAsk`

**Documentado (permission-modes):** "Claude Code auto-denies every tool call that would otherwise prompt you". Só o que cairia em prompt é negado; ações "that need no approval" seguem rodando.

**Documentado (tools-reference):** a ferramenta `Skill` "Can prompt for skills that set `allowed-tools`, `disallowed-tools`, or `hooks`". A doc também diz que mudou `/loop` e tarefas agendadas para perguntar "before running a skill that declares `allowed-tools` or hooks" (CHANGELOG 2.1.x).

**Inferência:** uma skill sem `allowed-tools`, `disallowed-tools` nem `hooks` não cai em prompt. `dontAsk` então não tem o que negar, e a carga passa. A doc não afirma essa conclusão com todas as letras: a frase acima implica que o prompt é a exceção, não a regra. As skills embutidas provavelmente não declaram esses campos, o que explica a carga sem recusa, mas a doc não mostra o frontmatter delas. Em aberto: se alguma das embutidas declara `allowed-tools` e nesse caso `dontAsk` a recusa.

**Documentado:** nenhuma exceção específica para `Skill` aparece na descrição de `dontAsk`. A doc não diz se uma regra `Skill(a)` em allow muda a decisão sobre `Skill(b)` em `dontAsk`; pelas frases acima, não muda.

## Pontos pedidos

### Semântica de `--tools`, `--allowedTools` e `dontAsk`

- `--tools`: escolhe as ferramentas built-in disponíveis. Não filtra por skill.
- `--allowedTools`: pré-aprova, não restringe.
- `dontAsk`: nega o que pediria aprovação. Não nega o que não pede.
- Precedência (permissions): "Rules are evaluated in order: deny, then ask, then allow." e "If a tool is denied at any level, no other level can allow it."

### Deny por lista aberta ou por nome

- **Documentado:** `Skill(name)` é exato, `Skill(name *)` é prefixo com qualquer argumento: "Permission syntax: `Skill(name)` for exact match, `Skill(name *)` for prefix match with any arguments."
- **Documentado:** na forma de parâmetro, "The value supports `*` as a wildcard that matches any sequence of characters" (permissions, "Match by input parameter"), e a skills.md cita `Skill(skill:deploy)`. Isso permite padrões como `Skill(skill:data*)` em deny (inferência da combinação das duas páginas).
- **Documentado:** o SDK diz que a lista de `skills` "takes exact skill names only" e manda usar `"all"` em vez de curinga.
- **Não documentado:** negação ("deny tudo exceto N"). Como "An allow rule can't carve an exception out of a deny rule", um `Skill(skill:*)` em deny seguido de allow para as skills do bot não funciona: o deny vence. A doc não descreve regra de exceção para `Skill`.
- **Documentado, aplicação a embutidas:** a doc sobre deny de skill dá exemplos com skills próprias e a embutida `/code-review` (alias `/review`). Não há ressalva de que deny não valha para embutidas.

### Deny tira a skill da listagem ou só bloqueia a chamada?

- **Documentado:** deny com nome de ferramenta sem especificador remove a ferramenta do contexto: "A bare tool name like `Bash` removes the tool from Claude's context entirely, so Claude never sees it." Escopo com padrão "leaves the tool available and blocks matching calls when Claude attempts them." Por analogia, `Skill(nome)` em deny bloqueia a chamada e deixa a ferramenta (inferência: a doc não trata o caso `Skill(...)` separadamente).
- **Documentado:** a listagem some por `skillOverrides` (`"off"` e `"user-invocable-only"` ficam "Hidden" para o Claude) e por `disable-model-invocation: true` ("This removes the skill from Claude's context entirely"), este último só para skill que se controla no frontmatter.
- **Em aberto:** se o evento `init` deixa de listar a skill com deny escopado, `skillOverrides` ou `disableBundledSkills`. A doc do SDK diz que a lista do `init` "includes... bundled skills included with Claude Code" e "lists the same skills whether or not they're in your `skills` list", e que `"off"` esconde dos "Agent SDK callers" na lista de comandos. Se o `init` do `-p` reflete isso, só um teste mostra.

## O que a doc não responde e só um teste mostra

1. `disableBundledSkills` cobre `artifact-design`? A doc de comandos marca como bundled skill, entre outras, `/dataviz`, `/artifact-capabilities` e `/artifact-diagramming`, e o CHANGELOG chama `artifact-design` de "bundled artifact-design skill" (2.1.281), mas `artifact-design` não está na tabela de comandos que li. Se ele vier de outra origem (por exemplo, ferramenta `Artifact` ou skill sincronizada), a setting pode não pegar. Teste: `init` com a setting ligada.
2. O que a ferramenta `Skill` devolve ao modelo para uma skill escondida por `disableBundledSkills`: a doc só descreve o erro de `skillOverrides` na invocação por nome completo.
3. Se `skillOverrides` em `--settings` vale para skill embutida pelo próprio nome em `-p` (a doc diz que sim para "Bundled skill... hide it", mas o exemplo é genérico).
4. Se `--setting-sources project` impede `skillOverrides` vindo de `--settings` de valer. A doc de `--settings` diz que ele "override[s] the same keys in your `settings.json` files"; não trata a combinação com `--setting-sources`.
5. Se há mais fontes que o ator enxerga além das embutidas (plugins instalados, skills sincronizadas): a doc diz que skills sincronizadas não carregam quando `--setting-sources` omite `user`, e que plugins instalados ficam fora com `--bare`; o que sobra com `project` apenas não está descrito.
6. Se `Skill(skill:<padrão>*)` em deny funciona com curinga no meio e se casa com skills embutidas pelo nome curto.
7. Se uma embutida declara `allowed-tools`, `disallowed-tools` ou `hooks` (o que faria `dontAsk` recusá-la).

## Teste na versão 2.1.317

Duas rodadas de `claude -p` com o comando do ator do dry run (`--setting-sources project`, `--strict-mcp-config`, `--tools` com `Skill`, `--allowedTools` com `Skill(sonda)`, `--permission-mode dontAsk`), numa pasta com uma única skill de projeto, `sonda`, em `.claude/skills/`. O pedido mandava chamar `Skill` para `sonda`, `dataviz`, `artifact-design` e `code-review`. A única diferença entre as rodadas é `"disableBundledSkills": true` no JSON do `--settings`.

| | Sem a opção | Com `disableBundledSkills: true` |
|---|---|---|
| Skills no `init` | 24: `sonda` e 23 embutidas | 4: `sonda`, `design`, `doctor`, `plugin-authoring` |
| `Skill(sonda)` | carrega | carrega |
| `Skill(dataviz)` | carrega | erro `Unknown skill: dataviz` |
| `Skill(artifact-design)` | carrega | erro `Unknown skill: artifact-design` |
| `Skill(code-review)` | carrega e roda em fork | erro `Unknown skill: code-review` |
| `permission_denials` | nenhuma | nenhuma |

O que o teste responde:

- `artifact-design` não aparece no `init` em nenhuma das rodadas, mas carrega sem a opção e é recusada com ela. A opção cobre essa skill.
- Sem a opção, `dontAsk` com `Skill(sonda)` em allow não recusa nenhuma das três embutidas, o que confirma a leitura da doc sobre `--allowedTools` e `dontAsk`.
- Com a opção, a recusa vem da ferramenta (`Unknown skill`), não do sistema de permissões: nenhuma das recusas aparece em `permission_denials`.
- O `--settings` combinado com `--setting-sources project` aplica a opção.

### As três que sobram

Mais duas rodadas, as duas com `disableBundledSkills: true`, chamando `sonda`, `design`, `doctor` e `plugin-authoring`. A segunda acrescenta `skillOverrides` com `"off"` para as três.

| | Só `disableBundledSkills` | Com `skillOverrides` `"off"` para as três |
|---|---|---|
| Skills no `init` | 4: `sonda`, `design`, `doctor`, `plugin-authoring` | 1: `sonda` |
| `Skill(sonda)` | carrega | carrega |
| `Skill(design)` | erro: não pode ser usada pela ferramenta `Skill` por `disable-model-invocation` | mesmo erro |
| `Skill(doctor)` | mesmo erro de `design` | mesmo erro |
| `Skill(plugin-authoring)` | carrega | erro: desligada para o modelo em `skillOverrides` |
| `permission_denials` | nenhuma | nenhuma |

- `design` e `doctor` aparecem no `init`, mas o modelo não consegue carregá-las, com ou sem `skillOverrides`.
- `plugin-authoring` sobrevive a `disableBundledSkills` e carrega. Só `skillOverrides` `"off"` a recusa.
- `skillOverrides` vindo de `--settings` vale com `--setting-sources project`.

## Combinação para o ator ver só as skills do projeto

No JSON de `--settings`, `"disableBundledSkills": true` mais `"skillOverrides": {"design": "off", "doctor": "off", "plugin-authoring": "off"}` deixa no `init` só as skills de `.claude/skills/`, e o modelo não carrega nenhuma das outras (testado acima, na 2.1.317). A lista de `skillOverrides` é por nome: uma skill nova que sobreviva a `disableBundledSkills` numa versão futura aparece no `init` até entrar na lista.

## Fontes

Todas acessadas em 15/11/2026. Primárias: documentação oficial e CHANGELOG oficial. Nenhuma issue do repositório foi usada.

- https://code.claude.com/docs/en/llms.txt (índice)
- https://code.claude.com/docs/en/skills.md ("Bundled skills", "Remove a skill", "Restrict Claude's skill access", "Override skill visibility from settings")
- https://code.claude.com/docs/en/permissions.md (ordem deny/ask/allow, deny de nome de ferramenta, "Match by input parameter", precedência)
- https://code.claude.com/docs/en/permission-modes.md ("Allow only pre-approved tools with dontAsk mode")
- https://code.claude.com/docs/en/cli-reference.md (`--tools`, `--allowedTools`, `--disallowedTools`, `--bare`, `--disable-slash-commands`, `--safe-mode`, `--settings`, `--setting-sources`)
- https://code.claude.com/docs/en/headless.md ("Start faster with bare mode")
- https://code.claude.com/docs/en/settings-reference.md (`disableBundledSkills`, `skillOverrides`, `syncClaudeAiSkills`, `strictPluginOnlyCustomization`)
- https://code.claude.com/docs/en/env-vars.md (`CLAUDE_CODE_DISABLE_BUNDLED_SKILLS`, `CLAUDE_CODE_SYNC_SKILLS`, `DISABLE_DOCTOR_COMMAND`)
- https://code.claude.com/docs/en/tools-reference.md (ferramenta `Skill`)
- https://code.claude.com/docs/en/commands.md (lista de skills embutidas)
- https://code.claude.com/docs/en/agent-sdk/skills.md (opção `skills`, "Allow only specific skills", "Confirm skills loaded")
- https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md (versões 2.1.81 `--bare`, 2.1.129 `skillOverrides`, 2.1.139 `Skill(name *)`, 2.1.169 `disableBundledSkills`, 2.1.260 e 2.1.283 regras `Skill(`, 2.1.281 skill embutida `artifact-design`)
- Observação local: `claude --version` (2.1.317) e `claude --help`; strings do binário instalado, citadas só como observação da versão instalada.
