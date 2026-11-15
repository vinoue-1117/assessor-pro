# Issue tracker: GitHub

Issues e specs deste repo ficam nas Issues do GitHub. Toda operação usa o `gh` CLI.

## Convenções

- **Criar issue**: `gh issue create --title "..." --body "..."`. Corpo de várias linhas vai por heredoc.
- **Ler issue**: `gh issue view <número> --json number,title,body,labels,comments`.
- **Listar issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`, com os filtros `--label` e `--state` que o caso pedir.
- **Tornar uma issue sub-issue de outra**: `gh issue create --parent <pai> ...`, ou depois `gh issue edit <pai> --add-sub-issue <filha>` (`gh` 2.94+). Em `gh` mais antigo: `gh api --method POST repos/<owner>/<repo>/issues/<pai>/sub_issues -F sub_issue_id=<id-de-banco-da-filha>` (id de banco, como em **Bloqueio** abaixo). Sem sub-issues, pôr `Part of #<pai>` no topo do corpo da filha.
- **Comentar**: `gh issue comment <número> --body "..."`
- **Pôr / tirar label**: `gh issue edit <número> --add-label "..."` / `--remove-label "..."`
- **Fechar issue resolvida**: `gh issue close <número> --comment "..."`
- **Fechar sem implementar**: `gh issue close <número> --reason "not planned" --comment "..."`. O motivo padrão do `gh issue close` é `completed`, que faz a issue aparecer como resolvida. Depois de fechar, conferir com `gh issue view <número> --json stateReason`.
- **PR que resolve issue**: o corpo usa `Closes #N`. O GitHub só reconhece `Closes`, `Fixes` e `Resolves`. Depois de abrir, conferir com `gh pr view <n> --json closingIssuesReferences`.

O repo é inferido de `git remote -v`; o `gh` faz isso sozinho quando roda dentro do clone.

## Pull requests como superfície de triagem

**PRs as a request surface: no.** _(Trocar para `yes` se o repo passar a tratar PR externa como pedido de feature; a `/triage` lê este flag.)_

Com `yes`, as PRs passam pelos mesmos labels e estados das issues, com os equivalentes do `gh pr`:

- **Ler uma PR**: `gh pr view <número> --comments` e `gh pr diff <número>` para o diff.
- **Listar PRs externas para triagem**: `gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`.
- **Comentar / pôr label / fechar**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

No GitHub, issues e PRs dividem a mesma numeração, então um `#42` solto pode ser qualquer um dos dois: resolver com `gh pr view 42` e, se falhar, `gh issue view 42`.

## Quando uma skill diz "publish to the issue tracker"

Criar uma issue no GitHub.

## Quando uma skill diz "fetch the relevant ticket"

Ler como em **Ler issue** acima.

## Operações de wayfinding

Usadas pela `/wayfinder`. O **mapa** é uma issue só, com issues **filhas** como tickets.

- **Mapa**: uma issue com o label `wayfinder:map`, cujo corpo traz Notes / Decisions-so-far / Fog. `gh issue create --label wayfinder:map`.
- **Ticket filho**: uma issue ligada ao mapa como sub-issue do GitHub (ver **Tornar uma issue sub-issue de outra**). Onde sub-issues não estiverem habilitadas, acrescentar a filha a uma task list no corpo do mapa e pôr `Part of #<mapa>` no topo do corpo da filha. Labels: `wayfinder:<tipo>` (`research`/`prototype`/`grilling`/`task`). Depois de assumido, o ticket fica atribuído a quem está conduzindo.
- **Bloqueio**: as **dependências nativas de issue** do GitHub, que são a representação canônica e aparecem na interface. Acrescentar uma aresta com `gh api --method POST repos/<owner>/<repo>/issues/<filha>/dependencies/blocked_by -F issue_id=<id-de-banco-da-bloqueadora>`, em que `<id-de-banco-da-bloqueadora>` é o **id de banco** numérico da bloqueadora (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _não_ o `#número` nem o `node_id`). O GitHub informa `issue_dependencies_summary.blocked_by` (só bloqueadoras abertas, que é a trava em vigor). Onde dependências não estiverem disponíveis, usar uma linha `Blocked by: #<n>, #<n>` no topo do corpo da filha. Um ticket está desbloqueado quando toda bloqueadora está fechada.
- **Consulta da fronteira**: listar as filhas abertas do mapa (`gh issue list --state open`, restrito às sub-issues ou à task list do mapa), tirar as que têm bloqueadora aberta (`issue_dependencies_summary.blocked_by > 0`, ou issue aberta na linha `Blocked by`) ou responsável atribuído; vale a primeira na ordem do mapa.
- **Assumir**: `gh issue edit <n> --add-assignee @me`, a primeira escrita da sessão.
- **Resolver**: `gh issue comment <n> --body "<resposta>"`, depois `gh issue close <n>`, depois acrescentar um ponteiro de contexto (gist + link) ao Decisions-so-far do mapa.
