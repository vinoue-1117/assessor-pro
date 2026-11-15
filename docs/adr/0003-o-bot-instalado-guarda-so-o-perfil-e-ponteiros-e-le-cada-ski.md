# O bot instalado guarda só o perfil e ponteiros, e lê cada skill da stable a cada uso

O que fica gravado no bot é o perfil e um ponteiro por skill, com description fixa. O ponteiro baixa da stable o texto da skill a cada uso, então uma correção promovida chega a todos os bots sem reinstalar, e mudar o texto ou a description da skill não altera o que está instalado. Pelo mesmo motivo o perfil só manda seguir a skill core, onde ficam a persona e as regras: mudar o perfil exige colar o prompt de instalação de novo em cada bot.

## Alternativas consideradas

Copiar a skill inteira, ou a description dela, para o bot: cada mudança no texto obrigaria a reinstalar à mão em cada bot.
