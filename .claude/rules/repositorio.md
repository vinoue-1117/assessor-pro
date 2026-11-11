# Repositório

Monorepo dos bots. A branch que os computadores dos assessores leem é a `stable`. A `main` só chega neles quando o dono promove (`git push origin main:stable`). Não promover daqui.

## Layout
- `bots/<produto>/` é a fonte. Hoje só `assessor` tem código. `briefing` entra no PR 2 e `mercado` no PR 3.
- `plugins/` é gerado por `python3 tools/gerar-ponteiros.py`, um diretório por bot instalável. O assessor continua com dois plugins (`assessor-envio` e `assessor-zap`) porque são dois bots instalados. Não editar `plugins/` à mão.
- `template/<produto>/` é a descrição e o getting-started do bot (ponteiros e perfis). A palavra para isso é template. Template de página, se aparecer, fica em `bots/<produto>/templates-page/`.
- `comum/` é só o que mais de um bot usa de fato. Neste PR, o baixador. Skill compartilhada vai em `comum/skills/`. O cliente de LLM fica para o PR 2.
- `tools/check.py` valida ponteiros, plugins, template e testes.

## O que não entra no repo
Vale com o repositório privado: nome de pessoa, chave, token, id interno, telefone e e-mail. Dado de cliente também não entra (nome, conta, telefone, PDF, planilha).

O endereço `github.com/vinoue-1117/assessor-pro` fica nos comandos de download: é o caminho que os bots já chamam. Os manifestos do marketplace e dos plugins já têm o campo de autor que o formato pede; não acrescentar nome em texto novo.

## Download
`comum/baixar.py` baixa da `stable`. Tenta o caminho novo (`bots/assessor/...`) e, se a resposta for 401 ou 404, o caminho antigo (`plugins/...`). `discurso/discurso-macro.md` não mudou de lugar.

`GITHUB_TOKEN_BOTS` é o token de leitura. Só segue no cabeçalho `Authorization`, e só para `raw.githubusercontent.com` (ou `127.0.0.1` em teste). Não vai na URL, no argumento, no log nem em arquivo. Sem a variável, o comando tenta sem autenticação. 401 ou 404 sem token pede para definir a variável.

Redirecionamento para outro host é recusado, para o token não sair do host permitido.

## Caminhos antigos que continuam na `stable`
Estes caminhos são o que os bots já instalados baixam. A cópia em `plugins/` é gerada e é também o que o marketplace instala. Não apagar neste PR.

| Caminho | Quem ainda chama |
| --- | --- |
| `plugins/assessor-envio/skills/<skill>/SKILL.md` | ponteiro já instalado, que baixa a skill completa |
| `plugins/assessor-zap/skills/<skill>/SKILL.md` | ponteiro já instalado |
| `plugins/assessor-envio/skills/assessor-preparar-envio/scripts/assessor.py` | skill que ainda tem o curl antigo |
| `plugins/assessor-envio/skills/assessor-preparar-envio/scripts/versao-minima` | o mesmo curl |
| `plugins/assessor-envio/skills/assessor-ajustar-cliente/scripts/cliente.py` | skill de ajuste de cliente |
| `discurso/discurso-macro.md` | preparar envio; o caminho não mudou |

O ponteiro novo tenta `bots/assessor/.../<skill>/SKILL.md` e cai no caminho da tabela. O baixador do script faz o mesmo com `assessor.py`, `versao-minima` e `cliente.py`.

Esses caminhos antigos podem deixar de ser contrato de download quando não houver computador cuja skill ou ponteiro instalado chame só a URL antiga. Isso inclui instalação presa a um commit e ponteiro importado pelo template, que não se atualizam sozinhos. O diretório `plugins/` em si continua enquanto o marketplace instalar por ele. `discurso/` sai de lá só num PR que mova o arquivo e deixe o baixador com fallback.

Não tornar o repositório privado antes de o token estar configurado nos bots e de um download com token ter funcionado com o repositório ainda público. Sem o token, a `stable` privada responde 404 e o envio para.
