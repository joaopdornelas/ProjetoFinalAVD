"""Textos autorais do grupo, usados pelo dashboard e pelo relatório."""

PERGUNTA = """
**Como os perfis de AST, GGT, bilirrubina e colinesterase diferem entre doadores de sangue, doadores suspeitos e participantes classificados com hepatite, fibrose ou cirrose?**

Escolhemos essa pergunta porque os exames apresentam diferenças entre as categorias e permitem investigar a separação e a sobreposição dos perfis laboratoriais.
"""

ENQUADRAMENTO = """
Adotaremos a abordagem de classificação multiclasse, considerando `categoria` como variável-alvo e preservando as cinco categorias originais.

Essa escolha acompanha a estrutura do dataset, que possui rótulos conhecidos. A EDA e o dashboard serão utilizados para examinar como as características observadas se relacionam com essas categorias. A avaliação de um eventual classificador dependerá de treinamento e validação próprios.
"""

PUBLICO_ALVO = """
O público-alvo será formado por estudantes e pesquisadores de saúde e ciência de dados interessados na análise exploratória de exames laboratoriais.

O dashboard permitirá comparar os grupos, examinar distribuições e compreender as limitações da amostra, com filtros e gráficos acessíveis a usuários sem conhecimento de programação.
"""

NOTAS = {
    'composicao_amostra': {
        'o_que_mostra': """
O tamanho e a composição dos cinco grupos.
""",
        'insight': """
A amostra possui 533 doadores comuns e grupos menores de hepatite, fibrose, cirrose e doadores suspeitos. Essa diferença precisa orientar a leitura dos demais gráficos.
""",
        'por_que_esse_grafico': """
As barras permitem comparar os tamanhos dos grupos e observar sua composição por sexo.
""",
    },
    'ausentes': {
        'o_que_mostra': """
Como as ausências se distribuem entre os grupos e os exames. O primeiro heatmap cruza diagnóstico e exame; o segundo cruza sexo e exame.
""",
        'insight': """
ALP está ausente em 42,9% dos registros de fibrose e em 20% dos de cirrose, enquanto todos os doadores comuns possuem esse exame observado.

Por sexo, as mulheres têm menos ausências em ALP (2,5% contra 3,2% dos homens) e nenhuma ausência em ALB, ALT e PROT. Em CHOL, porém, a relação se inverte: 2,9% das mulheres contra 0,8% dos homens, e seis das sete ausências femininas de CHOL são de doadoras. No total, 12 das 238 mulheres (5,0%) e 14 dos 377 homens (3,7%) têm pelo menos um exame ausente. A diferença entre os sexos depende do exame e é pequena em números absolutos, por isso não sustenta uma conclusão geral de que um dos sexos omite menos resultados.
""",
        'por_que_esse_grafico': """
O heatmap facilita a identificação de concentrações de ausência e fundamenta a discussão do tratamento. Cada célula mostra o percentual e a contagem, para que percentuais altos em grupos pequenos não sejam superestimados.
""",
    },
    'ast_ggt': {
        'o_que_mostra': """
A relação conjunta entre os exames e a distribuição dos participantes de cada grupo.
""",
        'insight': """
A maior concentração dos doadores fica na região inferior esquerda. Seus 50% centrais estão aproximadamente entre 21,1 e 29,8 em AST e entre 15,1 e 32 em GGT.

Os grupos com doença apresentam, em geral, valores centrais maiores:

| Diagnóstico | AST (mediana) | GGT (mediana) |
|---|---:|---:|
| Doadores | 24,8 | 21,4 |
| Hepatite | 47,2 | 45,55 |
| Fibrose | 70,0 | 72,2 |
| Cirrose | 92,9 | 96,35 |

A sobreposição aparece na região intermediária e nas caudas. Existem doadores com valores elevados e participantes com doença com valores menores. Hepatite, fibrose e cirrose também se misturam entre si. Assim, as duas variáveis mostram tendências de grupo, mas a posição de um ponto não determina sua categoria.

A associação geral pode ser descrita como positiva moderada, usando essa classificação como referência descritiva.

| Categoria | n | Spearman AST × GGT |
|---|---:|---:|
| Doadores | 533 | 0,381 |
| Doadores suspeitos | 7 | 0,214 |
| Hepatite | 24 | 0,624 |
| Fibrose | 21 | 0,441 |
| Cirrose | 30 | 0,089 |
| Amostra completa | 615 | 0,505 |

A relação varia bastante. Em cirrose, ela é praticamente nula nesta amostra. A estimativa dos suspeitos é especialmente instável por envolver sete registros.
""",
        'por_que_esse_grafico': """
Escolhemos o gráfico de dispersão porque AST e GGT são duas variáveis quantitativas e a pergunta é sobre a relação entre elas e sobre a separação dos grupos. Cada ponto representa um participante, o que permite ver ao mesmo tempo a tendência conjunta, a dispersão, as observações extremas e a sobreposição entre os diagnósticos, algo que um resumo por médias ou um boxplot de cada exame separado não mostraria.

Os dois eixos estão em escala logarítmica porque os exames são muito assimétricos: a maioria dos doadores fica abaixo de 50 U/L, mas há participantes acima de 300 U/L. Na escala linear, os doadores ficariam comprimidos no canto do gráfico. Os dois eixos usam as mesmas marcas (5, 10, 20, 50, 100, 200 e 500 U/L), o que torna as distâncias comparáveis entre AST e GGT, e o intervalo de cada eixo é calculado a partir dos dados, com margem para que nenhum ponto fique cortado.
""",
    },
    'spearman': {
        'o_que_mostra': """
Associações monotônicas entre as variáveis quantitativas. Como a matriz é simétrica (ALB × PROT é igual a PROT × ALB) e a diagonal sempre vale 1, mostramos apenas o triângulo inferior, sem repetições.
""",
        'insight': """
Na base tratada, os maiores coeficientes positivos são:

| Par | Spearman |
|---|---:|
| ALB × PROT | 0,517 |
| AST × GGT | 0,505 |
| ALT × AST | 0,497 |
| ALT × GGT | 0,418 |
| CHE × CHOL | 0,403 |

As associações negativas de maior magnitude são fracas:

| Par | Spearman |
|---|---:|
| Idade × ALB | −0,158 |
| BIL × CHOL | −0,119 |
| Idade × PROT | −0,100 |

Entre as praticamente nulas estão idade × BIL (−0,005), ALB × AST (0,028) e ALB × GGT (0,034). Esses valores descrevem associação monotônica, e relações de outro formato podem passar despercebidas.

| Par | Spearman |
|---|---:|
| AST × GGT | 0,505 |
| AST × BIL | 0,356 |
| GGT × BIL | 0,247 |
| GGT × CHE | 0,156 |
| AST × CHE | 0,102 |
| BIL × CHE | −0,068 |

AST e GGT apresentam a associação mais evidente. CHE apresenta relações gerais fracas com os outros três, embora sua distribuição por diagnóstico mostre diferenças importantes.

Com a idade, as maiores associações são com ALP (0,186), CHOL (0,174) e ALB (−0,158). São relações fracas. A correlação com BIL é praticamente zero.

Os doadores representam aproximadamente 86,7% da amostra e têm grande influência nas correlações gerais. Esses coeficientes combinam a variação dentro dos grupos com diferenças entre eles. Por isso, a correlação da amostra completa precisa ser acompanhada das correlações por categoria, como mostra a comparação de AST × GGT.
""",
        'por_que_esse_grafico': """
A matriz resume todos os pares de variáveis quantitativas e permite comparar a intensidade das associações. A escala de cores vai do roxo (associação negativa) ao verde (positiva), passando pelo branco (sem associação). O verde acompanha a identidade visual do dashboard e o roxo foi escolhido por contrastar bem com ele, inclusive para pessoas com daltonismo.
""",
    },
    'perfis': {
        'o_que_mostra': """
Diferenças de posição, dispersão e sobreposição entre as categorias.
""",
        'insight': """
| Diagnóstico | AST (mediana) | GGT (mediana) | BIL (mediana) | CHE (mediana) |
|---|---:|---:|---:|---:|
| Doadores | 24,8 | 21,4 | 6,9 | 8,35 |
| Hepatite | 47,2 | 45,55 | 13,0 | 9,51 |
| Fibrose | 70,0 | 72,2 | 13,0 | 8,59 |
| Cirrose | 92,9 | 96,35 | 34,0 | 3,43 |

As diferenças entre categorias descrevem participantes distintos e não representam o acompanhamento da evolução de uma mesma pessoa. O tamanho de cada grupo aparece no subtítulo do gráfico e ao passar o mouse sobre cada caixa.

AST e GGT mostram uma separação mais clara dos 50% centrais dos doadores em relação aos três grupos com doença:

- Em AST, o terceiro quartil dos doadores é 29,8, abaixo do primeiro quartil dos três grupos com doença.
- Em GGT, o terceiro quartil dos doadores é 32, também abaixo dos primeiros quartis desses grupos.
- Em CHE, a diferença é mais clara entre cirrose e os demais grupos.
- Em BIL, há maior sobreposição entre doadores, hepatite e fibrose, enquanto cirrose apresenta valores centrais maiores.

Entre hepatite, fibrose e cirrose, a sobreposição permanece importante.

Os suspeitos têm grande dispersão em AST e GGT. Em GGT, o intervalo interquartil vai de aproximadamente 55,3 a 257, com n = 7. Cirrose apresenta grande dispersão em BIL, com intervalo interquartil de 13,5 a 56, contra 5 a 10,1 nos doadores. A escala logarítmica deve ser considerada ao comparar visualmente essas amplitudes.
""",
        'por_que_esse_grafico': """
Os boxplots mostram a distribuição de cada exame, evitando restringir a comparação a uma única medida central.
""",
        'relacao_com_pergunta': """
Responde diretamente como os quatro perfis laboratoriais diferem entre os grupos.
""",
        'atributo_preatentivo': """
**Mensagem.** Na amostra, cirrose apresenta medianas maiores de AST, GGT e BIL e menor de CHE que os doadores, com sobreposição dos valores individuais.

**O que o público precisa enxergar primeiro.** O contraste do perfil de cirrose com o dos doadores nos quatro exames, especialmente a inversão de direção em CHE.

**Destaque anterior.** Na visualização 5, as cinco categorias recebem cores distintas e disputam atenção. Falta uma hierarquia visual que conduza ao contraste principal.

**Atributo utilizado.** Contexto em cinza, mantendo cirrose no vermelho usado para essa categoria em todo o dashboard. Os rótulos e as medianas devem permanecer legíveis em todos os grupos.

**Por que serve ao público.** Estudantes e pesquisadores precisam identificar o contraste principal e depois examinar a distribuição e as exceções. O destaque reduz a dependência da leitura repetida da legenda. Rótulos diretos, contagens e posição consistente complementam as cores e favorecem a leitura por pessoas com daltonismo.
""",
    },
    'tercis_ggt': {
        'o_que_mostra': """
O primeiro gráfico mostra a composição de cada categoria segundo a posição do GGT na distribuição da amostra. O segundo compara os quatro exames com a distribuição dos doadores, tomada como referência de normalidade: as anomalias são os valores que ficam além da fronteira externa do boxplot dos doadores, isto é, abaixo de Q1 − 1,5·IQR ou acima de Q3 + 1,5·IQR.
""",
        'insight': """
O tercil superior reúne 25,3% dos doadores, 79,2% dos registros de hepatite, 85,7% dos de fibrose e 90% dos de cirrose. Entre os doadores suspeitos, são seis dos sete participantes.

Percentual de cada grupo fora da faixa de referência dos doadores:

| Diagnóstico | AST | GGT | BIL | CHE |
|---|---:|---:|---:|---:|
| Doadores | 4,5% | 10,5% | 6,8% | 1,3% |
| Doadores suspeitos | 71,4% | 71,4% | 0,0% | 14,3% |
| Hepatite | 58,3% | 45,8% | 16,7% | 8,3% |
| Fibrose | 76,2% | 66,7% | 14,3% | 0,0% |
| Cirrose | 86,7% | 63,3% | 70,0% | 50,0% |

Em AST, GGT e BIL, todos os valores fora da faixa estão acima dela. Em CHE, a direção muda conforme o grupo: na cirrose, os 50% fora da faixa estão todos abaixo dela, enquanto nos demais grupos os poucos casos estão acima. AST e GGT já se afastam do padrão dos doadores na hepatite e na fibrose; BIL e CHE só se afastam de forma marcante na cirrose. Entre os doadores, os valores fora da faixa são os outliers do próprio grupo. Os percentuais dos suspeitos se referem a apenas sete participantes.
""",
        'por_que_esse_grafico': """
A normalização por categoria permite comparar composições apesar dos diferentes tamanhos dos grupos. No segundo gráfico, usar os doadores como referência transforma cada exame em uma pergunta simples: que parte do grupo está fora do que é comum entre pessoas sem doença hepática.
""",
        'relacao_com_pergunta': """
Evidencia diferenças na distribuição de GGT entre as categorias e mostra, para os quatro exames da pergunta, em que grupos os valores deixam de ser compatíveis com o padrão dos doadores.
""",
        'atributo_preatentivo': """
**Mensagem.** O tercil superior de GGT concentra uma proporção maior dos participantes com hepatite, fibrose e cirrose do que dos doadores.

**O que o público precisa enxergar primeiro.** A diferença no comprimento do segmento do tercil superior entre as categorias.

**Destaque anterior.** Na visualização 6, os tercis usavam três intensidades de azul sem relação com o restante do dashboard. O alinhamento também podia ser melhorado colocando o tercil superior no início de todas as barras, facilitando a comparação a partir de uma origem comum.

**Atributo utilizado.** Intensidade crescente de verde, com o tercil superior mais escuro e posicionado no início das barras. Como o diagnóstico já está identificado no eixo, a cor representa apenas o nível de GGT.

**Por que serve ao público.** Estudantes e pesquisadores precisam identificar o contraste principal e depois examinar a distribuição e as exceções. O destaque reduz a dependência da leitura repetida da legenda. Rótulos diretos, contagens e posição consistente complementam as cores e favorecem a leitura por pessoas com daltonismo.
""",
    },
}

STORYTELLING = """
**O que a exploração encontrou e onde**

- Visualização 1: forte desequilíbrio entre categorias, com 533 dos 615 registros pertencentes a doadores.
- Visualização 2 e seção 2 da EDA: ausência de ALP concentrada em determinados diagnósticos, chegando a 9 de 21 registros de fibrose.
- Visualização 3: doadores concentrados em valores menores de AST e GGT, enquanto os grupos com doença apresentam deslocamento e maior dispersão, com sobreposição.
- Visualização 4: associação positiva moderada entre AST e GGT, com Spearman de aproximadamente 0,505.
- Tabela de medianas por diagnóstico e boxplots da EDA: cirrose apresenta maiores medianas de AST, GGT e BIL e menor mediana de CHE que os doadores.
- Tabela de GGT discretizado por diagnóstico: o tercil superior reúne 25,3% dos doadores e 90% dos participantes com cirrose.

**Que história os dados contam**

A amostra reúne principalmente doadores de sangue e grupos menores com diferentes categorias de doença hepática. Os perfis laboratoriais diferem entre esses grupos, com maiores medianas de AST, GGT e BIL e menor mediana de CHE em cirrose quando comparada aos doadores. A sobreposição individual, os grupos pequenos e o padrão de ausência limitam a separação das categorias e a generalização dos resultados.

**Por que essa mensagem importa para o público**

Ela mostra como diferenças entre grupos podem coexistir com sobreposição individual. Também ensina que correlações gerais, percentuais e valores imputados precisam ser interpretados considerando o desequilíbrio da amostra e a qualidade dos dados.

**Qual técnica visual destaca a mensagem**

Na visualização 5, cirrose será destacada contra o contexto em cinza. Na visualização 6, o tercil superior será destacado pela intensidade do verde e pelo alinhamento dos segmentos.

**De quais exploratórias nasceram as explanatórias**

- Visualização 5: surgiu da visualização 3, que mostrou diferenças e sobreposição em AST e GGT, e dos boxplots e da tabela de medianas da EDA, que estenderam a comparação a BIL e CHE.
- Visualização 6: surgiu da visualização 3, que mostrou a distribuição desigual de GGT entre as categorias, e foi desenvolvida com a tabela de tercis da EDA.
"""

RESPOSTA = """
Na amostra analisada, os perfis de AST, GGT, bilirrubina e colinesterase apresentam diferenças entre as categorias. As medianas de AST e GGT são maiores nos grupos de hepatite, fibrose e cirrose do que entre os doadores comuns. O grupo de cirrose também apresenta maior mediana de bilirrubina e menor mediana de colinesterase em relação aos doadores.

A distribuição dos tercis de GGT reforça essas diferenças, com maior concentração dos grupos com doença no tercil superior. A sobreposição dos valores individuais, o desequilíbrio entre as categorias e os grupos pequenos limitam as conclusões. Esses resultados descrevem a amostra e fundamentam a investigação da relação entre exames e categorias conhecidas.

**Doadores suspeitos**

Manteremos os suspeitos na pergunta, nas visualizações e na resposta final, explicitando seu tamanho de sete participantes. O perfil é misto:

| Exame (mediana) | Suspeitos | Doadores | Hepatite | Fibrose | Cirrose |
|---|---:|---:|---:|---:|---:|
| AST | 46,7 | 24,8 | 47,2 | 70,0 | 92,9 |
| GGT | 83,0 | 21,4 | 45,55 | 72,2 | 96,35 |
| BIL | 4,9 | 6,9 | 13,0 | 13,0 | 34,0 |
| CHE | 5,33 | 8,35 | 9,51 | 8,59 | 3,425 |

Em AST e GGT, os suspeitos se aproximam mais dos grupos com doença. Em BIL, têm mediana menor que a dos doadores. Em CHE, ficam entre doadores e cirrose. Portanto, não apresentam um perfil uniformemente semelhante a uma única categoria.

Podemos descrever os valores observados, medianas e contagens desses sete registros. Por exemplo, seis dos sete estão no tercil superior de GGT. O tamanho reduzido limita generalizações e estimativas estáveis de associação. O rótulo disponível também não esclarece, por si só, o motivo da suspeita de cada participante.
"""
