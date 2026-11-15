# A promoção para a stable é um push direto da main, nunca uma PR

Os bots leem a stable, e a main só chega a eles quando o dono promove com um push fast-forward da main para a stable. O repositório só aceita squash e a stable não aceita force push: uma PR para a stable criaria um commit que a main não tem, e a promoção seguinte deixaria de ser fast-forward e seria recusada.

## Alternativas consideradas

Promover por PR da main para a stable. Uma PR assim chegou a ser aberta e foi fechada sem merge.
