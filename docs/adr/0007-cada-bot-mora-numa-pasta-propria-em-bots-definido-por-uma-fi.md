# Cada bot mora numa pasta própria em bots/, definido por uma ficha de formato fixo

O repositório é um monorepo com uma pasta por bot. Cada pasta traz a ficha do bot, com perfil, skills, rotinas e conexões no mesmo formato para todos, e as skills dele. A fonte fica num lugar só, sem cópia gerada, e o que vale para todos os bots não cita nenhum pelo nome.

## Alternativas consideradas

Plugins instalados por marketplace, com perfis e descriptions mantidos fora da pasta do bot: a instalação por marketplace deixou de existir. Manter a pasta antiga como cópia gerada, para as URLs antigas seguirem valendo: uma mudança feita na cópia se perderia ao regenerar.
