"""Funções de gráfico: cada uma recebe um DataFrame e devolve uma figura plotly."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import config

COR_GRADE = '#E3EFE7'

# Tema dos gráficos: fundo branco do plotly_white com a paleta e a grade em verde.
# É registrado como padrão para que as funções do plotly express já usem as cores verdes.
_tema = go.layout.Template(pio.templates['plotly_white'])
_tema.layout.colorway = config.PALETA_VERDE
_tema.layout.colorscale.sequential = config.ESCALA_VERDE
_tema.layout.xaxis.gridcolor = COR_GRADE
_tema.layout.yaxis.gridcolor = COR_GRADE
_tema.layout.title.font.color = config.VERDE_ESCURO
pio.templates['saude'] = _tema
pio.templates.default = 'saude'
TEMPLATE = 'saude'

# Escala divergente da correlação: roxo para associações negativas, branco para nulas e verde para positivas.
ESCALA_CORRELACAO = [[0.0, '#7B3294'], [0.5, '#F7F7F7'], [1.0, config.VERDE_ESCURO]]

# Paleta qualitativa dos clusters da Parte Comum: os clusters não têm ordem, então precisam de cores distintas.
CORES_CLUSTERS = [config.VERDE, '#E07B39', '#3E6E9C', '#B2263A', '#8DB580', '#7B3294', '#F2B45A',
                  '#0E3B28', '#999999', '#56B4E9']


def aplicar_layout(fig, titulo, eixo_x=None, eixo_y=None, subtitulo=None):
    titulo_layout = dict(text=titulo)
    if subtitulo:
        titulo_layout['subtitle'] = dict(text=subtitulo, font=dict(size=12, color='#666666'))
    fig.update_layout(
        title=titulo_layout, template=TEMPLATE, separators=',.',
        margin=dict(t=95 if subtitulo else 70, l=20, r=20, b=20),
    )
    if eixo_x is not None:
        fig.update_xaxes(title_text=eixo_x)
    if eixo_y is not None:
        fig.update_yaxes(title_text=eixo_y)
    return fig


def _ordens(df):
    ordens = {}
    for col in df.columns:
        if isinstance(df[col].dtype, pd.CategoricalDtype):
            presentes = set(df[col].dropna())
            ordens[col] = [c for c in df[col].cat.categories if c in presentes]
    return ordens


def _rotulos(df):
    return {col: config.rotulo(col) for col in df.columns}


def eh_quantitativa(df, coluna):
    serie = df[coluna]
    return pd.api.types.is_numeric_dtype(serie) and not pd.api.types.is_bool_dtype(serie)


def _categorias(df):
    return [c for c in config.ORDEM_CATEGORIAS if c in set(df['categoria'])]


def _rotulo_com_n(df, categoria):
    return f"{categoria} (n = {int((df['categoria'] == categoria).sum())})"


def _tamanhos_grupos(df):
    """Linha de apoio com o tamanho de cada grupo, usada no subtítulo dos gráficos."""
    contagem = df['categoria'].value_counts()
    partes = [f'{cat}: {int(contagem[cat])}' for cat in _categorias(df)]
    return 'Participantes por grupo — ' + ' · '.join(partes)


# Marcas dos eixos em escala logarítmica (sequência 1-2-5).
MARCAS_LOG = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]


def _formatar_pct(valor):
    return f'{valor:.1f}'.replace('.', ',') + '%'


# ---------------------------------------------------------------------------
# Visualizações exploratórias
# ---------------------------------------------------------------------------

def fig_composicao_amostra(df):
    contagem = df.groupby(['categoria', 'sexo'], observed=True).size().reset_index(name='participantes')
    contagem['sexo'] = contagem['sexo'].map(config.ROTULOS_SEXO)
    ordem = _categorias(df)

    fig = px.bar(
        contagem, x='participantes', y='categoria', color='sexo', orientation='h',
        category_orders={'categoria': ordem, 'sexo': [config.ROTULOS_SEXO[s] for s in config.ORDEM_SEXO]},
        labels={'participantes': 'Participantes', 'categoria': 'Diagnóstico', 'sexo': 'Sexo'},
    )
    totais = df['categoria'].value_counts()
    for cat in ordem:
        fig.add_annotation(x=int(totais[cat]), y=cat, text=f'{int(totais[cat])}', showarrow=False,
                           xanchor='left', xshift=6)
    return aplicar_layout(fig, 'Composição da amostra por diagnóstico e sexo',
                          eixo_x='Participantes', eixo_y='Diagnóstico')


def fig_ausentes_por_categoria(df):
    cols_flag = [c for c in df.columns if c.endswith('_ausente')]
    ordem = _categorias(df)
    grupos = df.groupby('categoria', observed=True)[cols_flag]
    pct = (grupos.mean() * 100).reindex(ordem)
    contagem = grupos.sum().reindex(ordem).astype(int)
    tamanhos = df['categoria'].value_counts().reindex(ordem)

    exames = [c.replace('_ausente', '').upper() for c in cols_flag]
    texto = [[f'{_formatar_pct(pct.iloc[i, j])}<br>({contagem.iloc[i, j]}/{tamanhos.iloc[i]})'
              for j in range(len(cols_flag))] for i in range(len(ordem))]

    fig = go.Figure(go.Heatmap(
        z=pct.values, x=exames, y=[_rotulo_com_n(df, c) for c in ordem], text=texto,
        texttemplate='%{text}', colorscale=config.ESCALA_VERDE, zmin=0,
        colorbar=dict(title='% ausentes'),
        hovertemplate='%{y}<br>%{x}: %{text}<extra></extra>',
    ))
    fig.update_yaxes(autorange='reversed')
    return aplicar_layout(fig, 'Valores ausentes por diagnóstico e exame (dado bruto)',
                          eixo_x='Exame', eixo_y='Diagnóstico')


def fig_ausentes_por_sexo(df):
    cols_flag = [c for c in df.columns if c.endswith('_ausente')]
    sexos = [s for s in config.ORDEM_SEXO if s in set(df['sexo'])]
    marcadores = df[cols_flag].assign(algum=df[cols_flag].any(axis=1))
    grupos = marcadores.groupby(df['sexo'], observed=True)
    pct = (grupos.mean() * 100).reindex(sexos)
    contagem = grupos.sum().reindex(sexos).astype(int)
    tamanhos = df['sexo'].value_counts().reindex(sexos)

    colunas = [c.replace('_ausente', '').upper() for c in cols_flag] + ['Pelo menos um exame']
    texto = [[f'{_formatar_pct(pct.iloc[i, j])}<br>({contagem.iloc[i, j]}/{tamanhos.iloc[i]})'
              for j in range(len(colunas))] for i in range(len(sexos))]

    fig = go.Figure(go.Heatmap(
        z=pct.values, x=colunas, y=[config.ROTULOS_SEXO[s] for s in sexos], text=texto,
        texttemplate='%{text}', colorscale=config.ESCALA_VERDE, zmin=0,
        colorbar=dict(title='% ausentes'),
        hovertemplate='%{y}<br>%{x}: %{text}<extra></extra>',
    ))
    fig.update_layout(height=300)
    return aplicar_layout(fig, 'Valores ausentes por sexo e exame (dado bruto)', eixo_x='Exame', eixo_y='Sexo')


def fig_ast_ggt(df):
    fig = px.scatter(
        df, x='ast', y='ggt', color='categoria', log_x=True, log_y=True, opacity=0.8,
        category_orders={'categoria': _categorias(df)}, color_discrete_map=config.CORES_CATEGORIA,
        labels=_rotulos(df), hover_data=['idade', 'sexo'],
    )
    fig.update_traces(marker=dict(size=7, line=dict(width=0.5, color='white')))

    # Mesmas marcas nos dois eixos, escolhidas para cobrir AST e GGT juntos.
    exames = pd.concat([df['ast'], df['ggt']])
    exames = exames[exames > 0]
    marcas = [m for m in MARCAS_LOG if exames.min() / 1.3 <= m <= exames.max() * 1.3]
    for eixo, coluna in [(fig.update_xaxes, 'ast'), (fig.update_yaxes, 'ggt')]:
        valores = df.loc[df[coluna] > 0, coluna]
        eixo(
            tickvals=marcas, ticktext=[f'{m:g}' for m in marcas],
            # Intervalo calculado a partir dos dados, com margem para nenhum ponto ficar cortado.
            range=[np.log10(valores.min() / 1.25), np.log10(valores.max() * 1.25)],
            showgrid=True, gridcolor=COR_GRADE, zeroline=False, minor=dict(showgrid=False),
        )
    fig.update_layout(height=560, legend=dict(title_text='Diagnóstico', itemsizing='constant'))
    return aplicar_layout(fig, 'Relação entre AST e GGT por diagnóstico (escalas logarítmicas)',
                          eixo_x=f"AST [{config.UNIDADES['ast']}], escala log",
                          eixo_y=f"GGT [{config.UNIDADES['ggt']}], escala log")


def fig_correlacao_spearman(df):
    cols = config.COLS_QUANTITATIVAS
    corr = df[cols].corr(method='spearman')
    nomes = [c.upper() if c != 'idade' else 'Idade' for c in cols]

    # Só o triângulo inferior, sem a diagonal: a matriz é simétrica e a diagonal vale sempre 1.
    valores = corr.values.copy()
    valores[np.triu_indices_from(valores)] = np.nan
    valores = valores[1:, :-1]
    texto = [['' if np.isnan(v) else f'{v:.2f}'.replace('.', ',').replace('-', '−') for v in linha]
             for linha in valores]

    fig = go.Figure(go.Heatmap(
        z=valores, x=nomes[:-1], y=nomes[1:], text=texto, texttemplate='%{text}',
        textfont=dict(size=12), zmin=-1, zmax=1, colorscale=ESCALA_CORRELACAO,
        colorbar=dict(title='Spearman'), xgap=2, ygap=2, hoverongaps=False,
        hovertemplate='%{y} × %{x}: %{text}<extra></extra>',
    ))
    fig.update_xaxes(showgrid=False, tickangle=0)
    fig.update_yaxes(showgrid=False, autorange='reversed')
    fig.update_layout(height=560)
    return aplicar_layout(fig, 'Correlação de Spearman entre idade e exames', eixo_x='Variável', eixo_y='Variável')


# ---------------------------------------------------------------------------
# Visualizações explanatórias
# ---------------------------------------------------------------------------

EXAMES_PERFIL = ['ast', 'ggt', 'bil', 'che']

# Atributo pré-atentivo da visualização 5: a categoria destacada mantém a sua cor e as demais ficam em cinza.
CATEGORIA_DESTAQUE = 'Cirrose'
COR_DESTAQUE = config.CORES_CATEGORIA[CATEGORIA_DESTAQUE]
COR_CONTEXTO = '#9E9E9E'


def fig_perfis_laboratoriais(df):
    ordem = _categorias(df)
    fig = make_subplots(rows=2, cols=2, subplot_titles=[config.rotulo(c) for c in EXAMES_PERFIL],
                        vertical_spacing=0.2, horizontal_spacing=0.08)
    for i, exame in enumerate(EXAMES_PERFIL):
        linha, coluna = divmod(i, 2)
        for cat in ordem:
            valores = df.loc[df['categoria'] == cat, exame]
            destaque = cat == CATEGORIA_DESTAQUE
            fig.add_trace(go.Box(
                y=valores, name=cat.replace(' ', '<br>'),
                marker_color=COR_DESTAQUE if destaque else COR_CONTEXTO,
                line=dict(width=2.5 if destaque else 1.5),
                boxpoints='all', jitter=0.4, pointpos=0,
                marker=dict(size=4, opacity=0.75 if destaque else 0.35),
                showlegend=False,
                hovertemplate=f'{cat} (n = {len(valores)})<br>{exame.upper()}: %{{y}}<extra></extra>',
            ), row=linha + 1, col=coluna + 1)
        fig.update_yaxes(type='log', title_text=f'{exame.upper()} [{config.UNIDADES[exame]}], log',
                         row=linha + 1, col=coluna + 1)
        fig.update_xaxes(tickangle=0, tickfont=dict(size=11), row=linha + 1, col=coluna + 1)
    fig.update_layout(height=820)
    if CATEGORIA_DESTAQUE in ordem:
        titulo = (f'AST, GGT, bilirrubina e colinesterase: {CATEGORIA_DESTAQUE.lower()} '
                  'em destaque contra os demais diagnósticos')
    else:
        titulo = 'AST, GGT, bilirrubina e colinesterase por diagnóstico'
    return aplicar_layout(fig, titulo, subtitulo=_tamanhos_grupos(df))


def fig_tercis_ggt(df):
    ordem = _categorias(df)
    niveis = list(df['ggt_nivel'].cat.categories)
    contagem = pd.crosstab(df['categoria'], df['ggt_nivel']).reindex(index=ordem, columns=niveis, fill_value=0)
    pct = contagem.div(contagem.sum(axis=1), axis=0) * 100

    longo = pct.stack().rename('pct').reset_index().merge(
        contagem.stack().rename('n').reset_index(), on=['categoria', 'ggt_nivel'])
    longo['rotulo_pct'] = longo['pct'].map(_formatar_pct)

    # Atributo pré-atentivo da visualização 6: intensidade crescente de verde, com o tercil superior
    # mais escuro e posicionado no início de todas as barras (origem comum para a comparação).
    # O diagnóstico já está identificado no eixo y; a cor representa apenas o nível de GGT.
    cores = dict(zip(niveis, [config.VERDE_CLARO, config.VERDE_MEDIO, config.VERDE_ESCURO]))
    fig = px.bar(
        longo, x='pct', y='categoria', color='ggt_nivel', orientation='h', text='rotulo_pct',
        category_orders={'ggt_nivel': niveis[::-1], 'categoria': ordem},
        color_discrete_map=cores, custom_data=['n'],
        labels={'pct': '% dos participantes do diagnóstico', 'categoria': 'Diagnóstico', 'ggt_nivel': 'Tercil de GGT'},
    )
    fig.update_traces(textposition='inside', insidetextanchor='middle',
                      hovertemplate='%{y}<br>%{fullData.name}: %{x:.1f}% (%{customdata[0]} participantes)<extra></extra>')
    fig.update_xaxes(range=[0, 100], gridcolor=COR_GRADE)
    fig.update_layout(barmode='stack')
    return aplicar_layout(fig, 'Distribuição dos tercis de GGT dentro de cada diagnóstico',
                          eixo_x='% dos participantes do diagnóstico', eixo_y='Diagnóstico',
                          subtitulo=_tamanhos_grupos(df))


def limites_referencia(df, exame):
    """Limites do boxplot dos doadores (Q1 − 1,5·IQR e Q3 + 1,5·IQR), usados como faixa de referência."""
    doadores = df.loc[df['categoria'] == 'Doador', exame]
    q1, q3 = doadores.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def fig_fora_referencia(df):
    ordem = _categorias(df)
    if 'Doador' not in ordem:
        fig = go.Figure()
        fig.add_annotation(text='Inclua os doadores no filtro: eles definem a faixa de referência.',
                           showarrow=False, font=dict(size=14))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return aplicar_layout(fig, 'Participantes fora da faixa de referência dos doadores')

    pct, texto, detalhe = [], [], []
    for cat in ordem:
        grupo = df[df['categoria'] == cat]
        linha_pct, linha_texto, linha_detalhe = [], [], []
        for exame in EXAMES_PERFIL:
            inferior, superior = limites_referencia(df, exame)
            acima = int((grupo[exame] > superior).sum())
            abaixo = int((grupo[exame] < inferior).sum())
            valor = (acima + abaixo) / len(grupo) * 100
            linha_pct.append(valor)
            linha_texto.append(f'{_formatar_pct(valor)}<br>({acima + abaixo}/{len(grupo)})')
            linha_detalhe.append(f'{acima} acima e {abaixo} abaixo da faixa')
        pct.append(linha_pct)
        texto.append(linha_texto)
        detalhe.append(linha_detalhe)

    colunas = []
    for exame in EXAMES_PERFIL:
        inferior, superior = limites_referencia(df, exame)
        faixa = f'{max(inferior, 0):.1f} a {superior:.1f}'.replace('.', ',')
        colunas.append(f'{exame.upper()}<br><sub>{faixa} {config.UNIDADES[exame]}</sub>')

    fig = go.Figure(go.Heatmap(
        z=pct, x=colunas, y=ordem, text=texto, customdata=detalhe, texttemplate='%{text}',
        colorscale=config.ESCALA_VERDE, zmin=0, zmax=100,
        colorbar=dict(title='% fora'), xgap=2, ygap=2,
        hovertemplate='%{y}<br>%{x}: %{text}<br>%{customdata}<extra></extra>',
    ))
    fig.update_yaxes(autorange='reversed')
    fig.update_layout(height=420)
    return aplicar_layout(
        fig, 'Participantes fora da faixa de referência dos doadores',
        eixo_x='Exame e faixa de referência', eixo_y='Diagnóstico',
        subtitulo='Faixa de referência = limites do boxplot dos doadores (Q1 − 1,5·IQR a Q3 + 1,5·IQR). '
                  'Valores fora dela são tratados como anomalias.',
    )


EXPLORATORIAS = [
    {'chave': 'composicao_amostra', 'titulo': 'Visualização 1 — Composição da amostra por categoria e sexo',
     'funcao': fig_composicao_amostra},
    {'chave': 'ausentes', 'titulo': 'Visualização 2 — Distribuição dos valores ausentes',
     'funcao': fig_ausentes_por_categoria, 'complementos': [fig_ausentes_por_sexo]},
    {'chave': 'ast_ggt', 'titulo': 'Visualização 3 — Relação entre AST e GGT', 'funcao': fig_ast_ggt},
    {'chave': 'spearman', 'titulo': 'Visualização 4 — Associações entre idade e exames',
     'funcao': fig_correlacao_spearman},
]

EXPLANATORIAS = [
    {'chave': 'perfis', 'titulo': 'Visualização 5 — Diferenças dos perfis laboratoriais entre categorias',
     'funcao': fig_perfis_laboratoriais},
    {'chave': 'tercis_ggt', 'titulo': 'Visualização 6 — Distribuição dos tercis de GGT por categoria',
     'funcao': fig_tercis_ggt, 'complementos': [fig_fora_referencia]},
]


# ---------------------------------------------------------------------------
# Explorador livre
# ---------------------------------------------------------------------------

def faixa_eixo(df, coluna, folga=0.05):
    """Limites de um eixo quantitativo calculados sobre o recorte inteiro, para comparar gráficos lado a lado."""
    minimo, maximo = df[coluna].min(), df[coluna].max()
    margem = (maximo - minimo) * folga or 1
    return [minimo - margem, maximo + margem]


def fig_relacao(df, x, y, cor=None, faixa_x=None, faixa_y=None):
    quant_x, quant_y = eh_quantitativa(df, x), eh_quantitativa(df, y)
    cores = config.CORES_CATEGORIA if cor == 'categoria' else None
    comum = dict(category_orders=_ordens(df), labels=_rotulos(df), color_discrete_map=cores)

    if quant_x and quant_y:
        fig = px.scatter(df, x=x, y=y, color=cor, opacity=0.75, **comum)
        fig.update_traces(marker=dict(size=11))
    elif quant_y:
        fig = px.box(df, x=x, y=y, color=cor, points='outliers', **comum)
        fig.update_traces(marker=dict(size=8))
    elif quant_x:
        fig = px.box(df, x=x, y=y, color=cor, points='outliers', orientation='h', **comum)
        fig.update_traces(marker=dict(size=8))
    else:
        # Duas qualitativas: barras agrupadas, coloridas pela variável do eixo y.
        comum['color_discrete_map'] = config.CORES_CATEGORIA if y == 'categoria' else None
        fig = px.histogram(df, x=x, color=y, barmode='group', **comum)
        fig.update_yaxes(title_text='Registros')

    if faixa_x is not None:
        fig.update_xaxes(range=faixa_x)
    if faixa_y is not None:
        fig.update_yaxes(range=faixa_y)

    coluna_legenda = cor if (quant_x or quant_y) else y
    if coluna_legenda is not None:
        fig.update_layout(
            showlegend=True,
            legend=dict(
                title_text=config.rotulo(coluna_legenda),
                font=dict(size=13),
                title_font=dict(size=13),
                itemsizing='constant',
            ),
        )

    titulo = f'{config.NOMES.get(y, y)} × {config.NOMES.get(x, x)}'
    return aplicar_layout(fig, f'{titulo} (n = {len(df)})')


# ---------------------------------------------------------------------------
# Parte Comum
# ---------------------------------------------------------------------------

def fig_cotovelo(cotovelo, k_livre=None, k_fixo=None):
    tem_silhueta = 'silhueta' in cotovelo
    titulos = ['Inércia: o cotovelo indica o k livre']
    if tem_silhueta:
        titulos.append('Silhueta: quanto maior, mais separados os clusters')
    fig = make_subplots(rows=1, cols=len(titulos), subplot_titles=titulos, horizontal_spacing=0.1)

    fig.add_scatter(x=cotovelo['k'], y=cotovelo['inercia'], mode='lines+markers', name='Inércia',
                    line=dict(color=config.VERDE, width=2.5), marker=dict(size=8), row=1, col=1)
    if tem_silhueta:
        fig.add_bar(x=cotovelo['k'], y=cotovelo['silhueta'], name='Silhueta',
                    marker_color=[config.VERDE_ESCURO if k == k_livre else config.VERDE_CLARO for k in cotovelo['k']],
                    text=cotovelo['silhueta'].map(lambda s: f'{s:.2f}'.replace('.', ',')),
                    textposition='outside', row=1, col=2)
        fig.update_yaxes(title_text='Coeficiente de silhueta', range=[0, cotovelo['silhueta'].max() * 1.25],
                         row=1, col=2)

    for coluna in range(1, len(titulos) + 1):
        if k_livre is not None:
            fig.add_vline(x=k_livre, line_dash='dash', line_color=config.VERDE_ESCURO, row=1, col=coluna,
                          annotation_text=f'k livre = {k_livre}' if coluna == 1 else None)
        if k_fixo is not None:
            fig.add_vline(x=k_fixo, line_dash='dot', line_color='#666666', row=1, col=coluna,
                          annotation_text=f'k fixo = {k_fixo}' if coluna == 1 else None,
                          annotation_position='bottom right')
        fig.update_xaxes(title_text='Número de clusters (k)', dtick=1, row=1, col=coluna)
    fig.update_yaxes(title_text='Inércia', row=1, col=1)
    fig.update_layout(showlegend=False, height=430)
    return aplicar_layout(fig, 'Método do Cotovelo — K-Means com k de 2 a 10')


def fig_clusters(clusters, passada):
    dados = clusters.assign(cluster=clusters[f'cluster_{passada}'].astype(str))
    ordem = sorted(dados['cluster'].unique(), key=int)
    fig = px.scatter(
        dados, x='x_vis', y='y_vis', color='cluster', category_orders={'cluster': ordem},
        hover_data=['classe_real', f'classe_mapeada_{passada}'], opacity=0.75,
        color_discrete_sequence=CORES_CLUSTERS,
    )
    nome = 'Passada 1 — k livre' if passada == 'livre' else 'Passada 2 — k fixo'
    return aplicar_layout(fig, f'{nome}: clusters projetados no PCA', eixo_x='PC1', eixo_y='PC2')


def fig_clusters_animado(clusters):
    quadros = []
    for passada, nome in [('livre', 'Passada 1 — k livre'), ('fixo', 'Passada 2 — k fixo')]:
        quadros.append(clusters.assign(
            passada=nome,
            classe_mapeada=clusters[f'classe_mapeada_{passada}'],
        ))
    dados = pd.concat(quadros, ignore_index=True)
    fig = px.scatter(
        dados, x='x_vis', y='y_vis', color='classe_mapeada', animation_frame='passada',
        hover_data=['classe_real'], opacity=0.75, color_discrete_map=config.CORES_CLASSES_OBESIDADE,
        category_orders={'classe_mapeada': list(config.CORES_CLASSES_OBESIDADE)},
    )
    return aplicar_layout(fig, 'Transição entre as passadas: classe mapeada de cada registro',
                          eixo_x='PC1', eixo_y='PC2')


def tabela_mapeamento(clusters, passada):
    """Para cada cluster: classe majoritária, registros e quanto do cluster essa classe representa."""
    col_cluster = f'cluster_{passada}'
    linhas = []
    for cluster, grupo in clusters.groupby(col_cluster):
        contagem = grupo['classe_real'].value_counts()
        linhas.append({
            'Cluster': int(cluster),
            'Classe mapeada (majoritária)': grupo[f'classe_mapeada_{passada}'].iloc[0],
            'Registros no cluster': len(grupo),
            'Registros da classe majoritária': int(contagem.iloc[0]),
            '% do cluster': round(contagem.iloc[0] / len(grupo) * 100, 1),
        })
    return pd.DataFrame(linhas)


def fig_classe_cluster(clusters, passada):
    """Heatmap classe real × cluster, em % de cada classe real, com a contagem de registros em cada célula."""
    col_cluster = f'cluster_{passada}'
    col_mapeada = f'classe_mapeada_{passada}'
    ordem = list(config.CORES_CLASSES_OBESIDADE)
    classes = [c for c in ordem if c in set(clusters['classe_real'])]
    mapa = clusters.groupby(col_cluster)[col_mapeada].first()
    # Colunas ordenadas pela classe atribuída ao cluster (na ordem natural das classes) e, no empate, pelo número.
    ids = sorted(mapa.index, key=lambda k: (ordem.index(mapa[k]), k))

    contagem = pd.crosstab(clusters['classe_real'], clusters[col_cluster]).reindex(
        index=classes, columns=ids, fill_value=0)
    pct = contagem.div(contagem.sum(axis=1), axis=0) * 100
    colunas = [f'Cluster {k}<br>→ {mapa[k]}' for k in ids]

    fig = go.Figure(go.Heatmap(
        z=pct.values, x=colunas, y=classes, zmin=0, zmax=100, colorscale=config.ESCALA_VERDE,
        showscale=False, xgap=3, ygap=3, customdata=contagem.values,
        hovertemplate='Classe real: %{y}<br>%{x}<br>%{z:.1f}% da classe (%{customdata} registros)<extra></extra>',
    ))
    for i, classe in enumerate(classes):
        for j, cluster in enumerate(ids):
            n = int(contagem.iat[i, j])
            if n:
                fig.add_annotation(
                    x=colunas[j], y=classe, text=f'{_formatar_pct(pct.iat[i, j])}<br>({n})', showarrow=False,
                    font=dict(size=12, color='white' if pct.iat[i, j] > 55 else '#1F2A24'),
                )
            # Contorno nas células em que o cluster recebeu a própria classe da linha: a soma delas é o recall.
            if mapa[cluster] == classe:
                fig.add_shape(type='rect', x0=j - 0.5, x1=j + 0.5, y0=i - 0.5, y1=i + 0.5,
                              line=dict(color=config.VERDE_ESCURO, width=2.5))

    fig.update_xaxes(showgrid=False, tickangle=0, tickfont=dict(size=12), automargin=True)
    fig.update_yaxes(showgrid=False, autorange='reversed', tickfont=dict(size=12))
    fig.update_layout(height=560, plot_bgcolor='white')
    nome = 'Passada 1 — k livre' if passada == 'livre' else 'Passada 2 — k fixo'
    return aplicar_layout(fig, f'{nome}: distribuição de cada classe real entre os clusters',
                          subtitulo='Percentual da linha (contagem entre parênteses). Contorno: cluster atribuído '
                                    'à própria classe; a soma dos contornos de uma linha é o recall da classe.')


def fig_matriz_confusao(matriz, titulo):
    fig = px.imshow(
        matriz, text_auto=True, color_continuous_scale=config.ESCALA_VERDE, aspect='auto',
        labels=dict(x='Classe mapeada', y='Classe real', color='Registros'),
    )
    return aplicar_layout(fig, titulo)


def fig_composicao(composicao, titulo):
    fig = px.imshow(
        composicao, text_auto=True, color_continuous_scale=config.ESCALA_VERDE, aspect='auto',
        labels=dict(x='Cluster', y='Classe real', color='Registros'),
    )
    return aplicar_layout(fig, titulo)
