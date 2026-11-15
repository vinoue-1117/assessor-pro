# Assessor Pro

Bots de IA de um assessor de investimentos: o que cada bot faz, como é instalado e como uma mudança nele é avaliada.

## Linguagem

### Pessoas

**dono**:
Pessoa a quem os bots servem: instala cada bot, faz os pedidos e decide o que ele pode fazer.
_Evitar_: usuário

**assessor**:
Assessor de investimentos que usa os bots do Assessor: manda o lote e a planilha de clientes e aprova o envio.

**cliente**:
Pessoa atendida pelo assessor, que recebe o relatório mensal pelo WhatsApp.
_Evitar_: contato (quando é o cliente)

### Bots

**bot**:
Assistente de IA da plataforma com uma função própria, definido por perfil, skills, rotinas e conexões.
_Evitar_: plugin

**bot de relatórios**:
Bot que prepara o lote mensal, pede a aprovação do assessor e pede cada envio ao bot de WhatsApp. Nunca envia direto.
_Evitar_: Bot Envio, bot de envio, assessor-envio

**bot de WhatsApp**:
Bot que lê e envia no WhatsApp do dono exatamente o que outro bot do dono pediu. É a única porta do WhatsApp para os demais bots.
_Evitar_: zap, WO, assessor-zap, gateway, porta do WhatsApp

**Analista**:
Bot de análise de mercado buy-side: consulta dados de mercado, faz as contas e entrega a tese numa Page. Não participa do envio nem acessa corretora.
_Evitar_: bot Analista, analista-tese

**Assessor**:
Produto formado pelos dois bots que entregam o relatório mensal aos clientes: o bot de relatórios e o bot de WhatsApp.

**skill core**:
Skill de cada bot que traz a persona, o que o bot nunca faz e as regras dele, seguida em toda conversa.
_Evitar_: core

**perfil**:
Texto curto do bot gravado na instalação, que manda seguir a skill core.

**ficha do bot**:
Documento que define um bot: perfil, skills, rotinas e conexões. É a única lista do que a instalação grava.
_Evitar_: bot.md

### Instalação

**ponteiro**:
Cópia curta e gerada de uma skill, que é o que o bot instalado guarda. A cada uso ela busca a skill completa na stable e manda segui-la.
_Evitar_: skill instalada, template

**stable**:
Versão do repositório que os bots leem. Só muda quando o dono promove.
_Evitar_: produção

**promoção**:
Ato do dono de levar para a stable o que está na main. É o momento em que uma mudança passa a valer para os bots instalados.
_Evitar_: publicar

**prompt de instalação**:
Texto que o dono cola no chat do bot para ele instalar ou atualizar as próprias skills. Diz a função do bot e a pasta dele no repositório.

**marca do repositório**:
Sinal presente em todo ponteiro, o endereço da skill neste repositório, que identifica de que repositório e de que bot a skill é.
_Evitar_: prefixo assessor-

**skill órfã**:
Skill instalada que aponta para a pasta de um bot mas cujo nome não está mais na lista de skills dele.
_Evitar_: órfã

**bot de time**:
Bot de um plano de time, que guarda skills próprias.
_Evitar_: Teams

**bot pessoal**:
Bot de um plano particular, que não guarda skill própria e enxerga a biblioteca de skills do dono.
_Evitar_: bot do plano particular

**skills próprias**:
Skills que um bot de time guarda só para si.
_Evitar_: escopo bot

**biblioteca de skills do dono**:
Conjunto de skills compartilhado por todos os bots pessoais de um mesmo dono.
_Evitar_: biblioteca user, pasta user, escopo user, biblioteca pessoal

**catálogo de erros**:
Lista numerada de padrões de erro de comportamento já vistos no repositório, conferida antes de mexer em script ou skill de bot.
_Evitar_: erros conhecidos, erros-conhecidos

### Envio

**relatório XP performance**:
PDF mensal da carteira de um cliente, emitido pela corretora. É o que o assessor envia e a fonte dos números da mensagem.

**lote**:
Conjunto de relatórios de um mês, um por conta, preparado e aprovado de uma vez.
_Evitar_: envio mensal

**conta**:
Código da conta XP de um cliente.
_Evitar_: conta_xp

**planilha de clientes**:
Planilha do assessor com conta, telefone, nome e apelido de cada cliente.
_Evitar_: planilha ativa, clientes.csv

**apelido**:
Como o assessor chama o cliente. Entra na saudação da mensagem.

**preparo**:
Etapa que lê os relatórios do lote, monta a mensagem de cada conta e dá a cada uma um status, antes da aprovação. Não envia nada.
_Evitar_: preparar envio, preparo do lote

**status da conta**:
Resultado do preparo para cada conta: pronto (vai), revisar (só vai se o assessor aprovar nominalmente) ou bloqueado (não vai).

**formato mudado**:
Situação em que o relatório parece ter outro layout. A conta sai revisar e a mensagem sai sem o bloco de números.

**trava de lote**:
Conferência feita sobre o lote inteiro: a mesma omissão em todas as contas com bloco de números marca essas contas como revisar.

**código do lote**:
Impressão digital do conteúdo de um lote. A aprovação só vale para o código atual.
_Evitar_: CODIGO

**aprovação do lote**:
Um único "sim" explícito do assessor ao resumo do lote. É o único gate dos envios a clientes.

**gate**:
Ponto em que alguém decide se um envio pode sair. Fica no bot que pede o envio, nunca no executor.
_Evitar_: gate de envio, permissão de envio

**pacote**:
Unidade de um envio: um destinatário com o seu arquivo e o seu texto.

**envio de teste**:
Envio de um pacote só para o chat do próprio assessor, para ver como a mensagem chega. Nenhum cliente recebe.
_Evitar_: teste, envio-teste

**histórico de envios**:
Registro de cada tentativa de envio, com o resultado: enviado, falhou, pulado ou teste.
_Evitar_: log de envios

**trava de destinatário**:
Conferência feita imediatamente antes de enviar: a conversa aberta tem que ser a do destinatário pedido.

**trava de texto**:
Conferência feita imediatamente antes de enviar: a caixa de mensagem tem que conter o texto inteiro.
_Evitar_: trava de conteúdo

**legenda**:
Campo de texto do anexo no WhatsApp, limitado a 1.024 caracteres, onde a mensagem do cliente vai junto com o relatório.

### Mensagem

**mensagem do cliente**:
Texto de WhatsApp que acompanha o relatório: saudação com o apelido, bloco de números, cenário do mês e despedida.
_Evitar_: mensagem.txt, mensagem ao cliente, legenda

**bloco de números**:
Parte da mensagem com os números da carteira: patrimônio, rentabilidade do mês, comparativos e janelas. Traz só o que foi lido do relatório.
_Evitar_: NUMEROS

**janela**:
Período de rentabilidade mais longo que o mês mostrado na mensagem (no ano, 12 meses), com a carteira e o CDI lado a lado.
_Evitar_: coluna

**discurso macro**:
Texto curto de cenário do mês, igual para todos os clientes do lote, que fecha a mensagem.
_Evitar_: discurso, cenário do mês

**data de referência**:
Mês (MM/AAAA) a que um lote ou um discurso macro pertence. Discurso de outro mês não entra no lote.
_Evitar_: ref

### WhatsApp

**nome exato**:
Regra para abrir uma conversa pelo nome: só vale um resultado único, com nome idêntico ao pedido ou a um apelido confirmado.

**apelido confirmado**:
Nome alternativo de um contato do WhatsApp que o dono confirmou uma vez.

### Analista

**tese**:
Análise do Analista que sustenta uma decisão de alocação: lado, tamanho sugerido, horizonte e o que faria mudar de ideia.
_Evitar_: memorando, relatório

**Page**:
Página que o Analista publica com a tese. No chat vão só o link e a decisão.
_Evitar_: canvas, markdown polido

**pacote de dados**:
Conjunto dos dados de mercado, das páginas consultadas e das contas sobre o qual a tese é escrita e conferida.
_Evitar_: pacote, JSON de dados

**revisão da tese**:
Leitura do rascunho da tese por um subagente sem o histórico da conversa, antes da publicação.
_Evitar_: revisão adversarial

**advogado do diabo**:
Papel da revisão da tese que contesta o argumento e devolve um veredito: sólida, frágil ou refazer.

**antagonista**:
Papel da revisão da tese que procura contras e riscos e devolve itens para seções da tese, sem dar veredito.
_Evitar_: advogado do diabo

**conferente**:
Papel da revisão da tese que confere o texto final contra o pacote de dados, só por fato, e decide a publicação.
_Evitar_: conferente factual, revisor

**veredito**:
Conclusão que o revisor declara sobre o rascunho da tese.

### Avaliação

**eixo**:
Cada uma das três perguntas independentes com que se avalia uma mudança de skill: fluxo, acerto e gosto. Não são etapas e não têm ordem.
_Evitar_: alicerce, etapa

**eixo de fluxo**:
Eixo que pergunta se o bot segue a skill.

**eixo de acerto**:
Eixo que pergunta se a resposta do bot está certa, quando há uma referência conhecida.

**eixo de gosto**:
Eixo que pergunta qual formato de saída o dono prefere. O dono lê amostras de variantes e escolhe.
_Evitar_: modo de gosto

**dry run**:
Rodada em que um ator faz o papel do bot sobre um cenário, fora da plataforma, e um avaliador lê o transcript.
_Evitar_: ensaio fora da plataforma, benchmark, harness, rodada de prova

**live run**:
Avaliação feita sobre a conversa real de um bot na plataforma, sem ator.

**ator**:
Claude que faz o papel do bot num dry run, com as skills da branch.

**avaliador**:
Agente que lê o transcript contra as skills e os erros do fluxo e escreve o relatório de desvios. Não dá nota nem corrige a skill.
_Evitar_: avaliador-transcript

**cenário**:
Descrição do pedido feito ao bot num dry run e do que substitui a plataforma nele.
_Evitar_: cenario.md

**desvio**:
Ponto em que o ator contraria a skill: faz o que ela proíbe, deixa de fazer o que ela manda ou faz fora de ordem.

**lacuna da skill**:
Caso em que a skill não diz o que fazer. Não é desvio do ator.

**erros do fluxo**:
Lista das falhas já vistas num fluxo, cada uma com a instrução da skill que ela contraria. É a régua do avaliador.
_Evitar_: erros.md

**variante**:
Versão alternativa de uma instrução do bot, usada no eixo de gosto.

**amostra**:
Saída de uma variante sobre a entrada comum, lida pelo dono no eixo de gosto.

**partida**:
Arquivos congelados de uma rodada anterior, de onde todas as variantes de uma rodada de gosto começam.
_Evitar_: arquivos congelados

**pasta de dados**:
Pasta privada, fora do repositório, onde ficam transcripts, relatórios e amostras.

**caso**:
Unidade do eixo de acerto: uma entrada fictícia com gabarito e critérios.
_Evitar_: caso de eval, caso de acerto

**gabarito**:
Lista dos erros plantados e das frases corretas de um rascunho, usada para contar o que o revisor pegou ou contestou.

**juiz**:
Quem decide o resultado de uma avaliação: um modelo no eixo de acerto, o dono no eixo de gosto.
_Evitar_: graders
