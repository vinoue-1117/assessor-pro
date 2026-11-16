# Assessor Pro

Bots de IA de um assessor de investimentos: o envio do relatório mensal aos clientes, a análise de mercado, a instalação dos bots e a avaliação das mudanças nas skills.

## Linguagem

### Pessoas

**dono**:
Pessoa que usa os bots: instala cada bot, faz os pedidos e decide o que ele pode fazer.
_Evitar_: usuário

**criador**:
Pessoa que constrói e mantém os bots no repositório: edita a main, promove para a stable e escolhe entre as amostras no eixo de gosto. Nos bots pessoais dele, é também o dono.
_Evitar_: dono do repositório

**assessor**:
Assessor de investimentos que usa os bots do Assessor Pro: manda o lote e a planilha de clientes e aprova o envio.

**cliente**:
Pessoa atendida pelo assessor, que recebe o relatório XP performance pelo WhatsApp.
_Evitar_: contato (quando é o cliente)

### Bots

**bot**:
Assistente de IA da plataforma com uma função própria, definido pela ficha do bot.
_Evitar_: plugin

**bot de relatórios**:
Bot que prepara o lote mensal, pede a aprovação do assessor e pede cada envio ao bot de WhatsApp. Nunca envia direto.
_Evitar_: Bot Envio, bot de envio, assessor-envio

**bot de WhatsApp**:
Único bot que lê e envia no WhatsApp do dono. Envia exatamente o que outro bot do dono pediu.
_Evitar_: zap, WO, assessor-zap

**Analista**:
Bot de análise de mercado buy-side: consulta dados de mercado, faz as contas e entrega a tese numa Page. Não participa do envio nem acessa corretora.
_Evitar_: bot Analista, analista-tese

**Assessor Pro**:
Produto formado pelos dois bots que entregam o relatório XP performance aos clientes: o bot de relatórios e o bot de WhatsApp.
_Evitar_: Assessor

**bot construtor**:
Bot da plataforma que cria os outros bots e grava as skills deles na biblioteca de skills do dono. Opcional, e só para bot pessoal: não acessa as skills próprias de um bot de time.

**skill core**:
Skill de cada bot que traz a persona, o que o bot nunca faz e as regras dele, seguida em toda conversa.

**perfil**:
Texto curto do bot gravado na instalação, que manda seguir a skill core.

**ficha do bot**:
Documento que define um bot: perfil, skills, rotinas e conexões. É a única lista do que a instalação grava.
_Evitar_: bot.md

### Instalação

**ponteiro**:
Cópia curta e gerada de uma skill, que é o que o bot instalado guarda. A cada uso ela baixa da stable o texto da skill e manda segui-lo.
_Evitar_: skill instalada, template

**stable**:
Versão do repositório que os bots leem. Só muda quando o criador promove.
_Evitar_: produção

**promoção**:
Ato do criador de levar para a stable o que está na main, por push direto e nunca por PR. É o momento em que uma mudança passa a valer para os bots instalados.
_Evitar_: publicar

**prompt de instalação**:
Texto que o dono cola no chat do bot para ele instalar ou atualizar as próprias skills, ou para conferir se ele está funcionando. Diz a função do bot e a pasta dele no repositório. Bot pessoal também pode ser instalado pelo bot construtor, sem este texto.

**skill órfã**:
Skill instalada que aponta para a pasta de um bot mas cujo nome não está mais na lista de skills dele.
_Evitar_: órfã

**bot de time**:
Bot de um plano de time, que guarda skills próprias, visíveis só para ele.
_Evitar_: Teams, escopo bot

**bot pessoal**:
Bot de um plano particular, que não guarda skill própria e enxerga a biblioteca de skills do dono.

**biblioteca de skills do dono**:
Conjunto de skills que todo bot acessa e pode alterar. Na plataforma é a pasta `user`.
_Evitar_: biblioteca user, escopo user, biblioteca pessoal

**catálogo de erros**:
Lista numerada de padrões de erro de comportamento já vistos no repositório, conferida antes de mexer em script ou skill de bot.

### Envio

**relatório XP performance**:
PDF mensal da carteira de um cliente, emitido pela corretora. É o que o assessor envia e a fonte dos números da mensagem.

**lote**:
Conjunto de relatórios XP performance de um mês, um por conta, preparado e aprovado de uma vez.
_Evitar_: envio mensal

**conta**:
Código da conta XP de um cliente.
_Evitar_: conta_xp

**planilha de clientes**:
Planilha do assessor com conta, telefone, nome e apelido de cada cliente.
_Evitar_: clientes.csv

**apelido**:
Como o assessor chama o cliente. Entra na saudação da mensagem.

**preparo**:
Etapa que lê os relatórios XP performance do lote e monta a mensagem de cada conta, com um status: pronto (vai), revisar (só vai se o assessor aprovar nominalmente) ou bloqueado (não vai). Não envia nada.
_Evitar_: preparar envio, preparo do lote

**formato mudado**:
Situação em que o relatório XP performance parece ter outro layout. A conta sai revisar e a mensagem sai sem o bloco de números.

**aprovação do lote**:
Um único "sim" explícito do assessor ao resumo do lote, preso ao código do lote, a impressão digital do conteúdo. É o único gate dos envios a clientes, e lote que muda depois do resumo pede nova aprovação.
_Evitar_: CODIGO

**pacote**:
Unidade de um envio: um destinatário com o seu arquivo e o seu texto.

**envio de teste**:
Envio de um pacote só para o chat do próprio assessor, para ver como a mensagem chega. Nenhum cliente recebe.
_Evitar_: teste, envio-teste

**histórico de envios**:
Registro de cada tentativa de envio, com o resultado: enviado, falhou, pulado ou teste.

**trava de destinatário**:
Conferência feita imediatamente antes de enviar: a conversa aberta tem que ser a do destinatário pedido.

**trava de texto**:
Conferência feita imediatamente antes de enviar: a caixa de mensagem tem que conter o texto inteiro.
_Evitar_: trava de conteúdo

**legenda**:
Campo de texto do anexo no WhatsApp, limitado a 1.024 caracteres, onde a mensagem do cliente vai junto com o relatório XP performance.

### Mensagem

**mensagem do cliente**:
Texto de WhatsApp que acompanha o relatório XP performance: saudação com o apelido, bloco de números, discurso macro e despedida.
_Evitar_: mensagem.txt, mensagem ao cliente, legenda

**bloco de números**:
Parte da mensagem com os números da carteira: patrimônio, rentabilidade do mês, comparativos e as janelas no ano e em 12 meses, com a carteira e o CDI lado a lado. Traz só o que foi lido do relatório XP performance.
_Evitar_: NUMEROS

**discurso macro**:
Texto curto de cenário do mês, igual para todos os clientes do lote, que fecha a mensagem.
_Evitar_: discurso, cenário do mês

**data de referência**:
Mês (MM/AAAA) a que um lote ou um discurso macro pertence. Discurso de outro mês não entra no lote.
_Evitar_: ref

### WhatsApp

**apelido confirmado**:
Nome alternativo de um contato do WhatsApp que o dono confirmou uma vez. Vale como nome exato para abrir a conversa.

### Analista

**tese**:
Análise do Analista que sustenta uma decisão de alocação: lado, tamanho sugerido, horizonte e o que faria mudar de ideia.
_Evitar_: relatório

**Page**:
Página que o Analista publica com a tese. No chat vão só o link e a decisão.
_Evitar_: canvas, markdown polido

**pacote de dados**:
Conjunto dos dados de mercado, das páginas consultadas e das contas sobre o qual a tese é escrita e conferida.
_Evitar_: pacote, JSON de dados

**revisão da tese**:
Leitura da tese, antes da publicação, por dois subagentes que recebem só o texto e o pacote de dados: o antagonista lê o rascunho, e o conferente lê o texto final.

**antagonista**:
Subagente que procura contras e riscos no rascunho da tese e devolve itens, cada um destinado a uma seção da Page. Não dá veredito e não decide a publicação.

**conferente**:
Subagente que confere o texto final da tese contra o pacote de dados, só por fato, e devolve `confere` ou `reescrever`. É quem decide a publicação.

### Avaliação

**eixo**:
Cada uma das três perguntas independentes com que se avalia uma mudança de skill: fluxo (o bot segue a skill?), acerto (a resposta está certa contra uma referência conhecida?) e gosto (qual formato de saída o criador prefere?). Não são etapas e não têm ordem.
_Evitar_: alicerce, etapa, modo de gosto

**dry run**:
Rodada em que um ator faz o papel do bot sobre um cenário, fora da plataforma, e um avaliador lê o transcript.
_Evitar_: ensaio fora da plataforma, benchmark, harness, rodada de prova

**ator**:
Claude que faz o papel do bot num dry run, com as skills da branch.

**live run**:
Rodada em que o avaliador lê o export de uma conversa do bot real, sem ator e sem cenário. O pedido é a mensagem do dono no transcript.

**avaliador**:
Agente que lê o transcript contra as skills e as falhas já vistas no fluxo e escreve o relatório de desvios. Não dá nota nem corrige a skill.
_Evitar_: avaliador-transcript

**cenário**:
Descrição do pedido feito ao bot num dry run e do que substitui a plataforma nele.
_Evitar_: cenario.md

**desvio**:
Ponto em que o ator contraria a skill: faz o que ela proíbe, deixa de fazer o que ela manda ou faz fora de ordem. Quando a skill não diz o que fazer, é lacuna da skill, não desvio.

**anti-pattern**:
Falha já vista num fluxo, registrada com o que aparece no transcript e a instrução da skill que ela contraria. O avaliador procura cada uma no transcript da rodada.
_Evitar_: erro já visto

**variante**:
Versão alternativa de uma instrução do bot, usada no eixo de gosto.

**amostra**:
Saída de uma variante sobre a entrada comum, lida pelo criador no eixo de gosto.

**partida**:
Arquivos congelados de uma rodada anterior, de onde todas as variantes de uma rodada de gosto começam.

**pasta de dados**:
Pasta privada, fora do repositório, onde ficam transcripts, relatórios e amostras.

**caso**:
Unidade do eixo de acerto: uma entrada fictícia com gabarito e critérios.
_Evitar_: caso de eval, caso de acerto
