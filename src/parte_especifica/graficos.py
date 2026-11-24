"""Funções de gráfico: cada uma recebe um DataFrame e devolve uma figura plotly."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import config

TEMPLATE = 'plotly_white'


def aplicar_layout(fig, titulo, eixo_x=None, eixo_y=None):
    fig.update_layout(title=titulo, template=TEMPLATE, margin=dict(t=70, l=20, r=20, b=20))
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
    cont = grupos.sum().reindex(ordem).astype(int)
    tamanhos = df['categoria'].value_counts().reindex(ordem)

    exames = [c.replace('_ausente', '').upper() for c in cols_flag]
    texto = [[f'{pct.iloc[i, j]:.1f}%<br>({cont.iloc[i, j]}/{tamanhos.iloc[i]})' for j in range(len(cols_flag))]
             for i in range(len(ordem))]

    fig = go.Figure(go.Heatmap(
        z=pct.values, x=exames, y=[_rotulo_com_n(df, c) for c in ordem], text=texto,
        texttemplate='%{text}', colorscale='Oranges', zmin=0,
        colorbar=dict(title='% ausentes'),
        hovertemplate='%{y}<br>%{x}: %{text}<extra></extra>',
    ))
    fig.update_yaxes(autorange='reversed')
    return aplicar_layout(fig, 'Valores ausentes por diagnóstico e exame (dado bruto)',
                          eixo_x='Exame', eixo_y='Diagnóstico')


def fig_ast_ggt(df):
    fig = px.scatter(
        df, x='ast', y='ggt', color='categoria', log_x=True, log_y=True, opacity=0.75,
        category_orders={'categoria': _categorias(df)}, color_discrete_map=config.CORES_CATEGORIA,
        labels=_rotulos(df), hover_data=['idade', 'sexo'],
    )
    return aplicar_layout(fig, 'Relação entre AST e GGT por diagnóstico (escalas logarítmicas)',
                          eixo_x=f"AST [{config.UNIDADES['ast']}], escala log",
                          eixo_y=f"GGT [{config.UNIDADES['ggt']}], escala log")


def fig_correlacao_spearman(df):
    cols = config.COLS_QUANTITATIVAS
    corr = df[cols].corr(method='spearman')
    nomes = [c.upper() if c != 'idade' else 'Idade' for c in cols]
    fig = px.imshow(
        corr.values, x=nomes, y=nomes, text_auto='.2f', zmin=-1, zmax=1, color_continuous_scale='RdBu_r',
        labels=dict(color='Spearman'), aspect='auto',
    )
    return aplicar_layout(fig, 'Correlação de Spearman entre idade e exames', eixo_x='Variável', eixo_y='Variável')


# ---------------------------------------------------------------------------
# Visualizações explanatórias
# ---------------------------------------------------------------------------

EXAMES_PERFIL = ['ast', 'ggt', 'bil', 'che']

# Atributo pré-atentivo da visualização 5: a categoria destacada mantém a sua cor e as demais ficam em cinza.
CATEGORIA_DESTAQUE = 'Cirrose'
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
                y=valores, name=f"{cat.replace(' ', '<br>')}<br>(n = {len(valores)})",
                marker_color=config.CORES_CATEGORIA[cat] if destaque else COR_CONTEXTO,
                line=dict(width=2.5 if destaque else 1.5),
                boxpoints='all', jitter=0.4, pointpos=0,
                marker=dict(size=4, opacity=0.75 if destaque else 0.35),
                showlegend=False,
            ), row=linha + 1, col=coluna + 1)
        fig.update_yaxes(type='log', title_text=f'{exame.upper()} [{config.UNIDADES[exame]}], log',
                         row=linha + 1, col=coluna + 1)
        fig.update_xaxes(tickangle=0, tickfont=dict(size=10), row=linha + 1, col=coluna + 1)
    fig.update_layout(height=820)
    titulo = f'AST, GGT, bilirrubina e colinesterase: {CATEGORIA_DESTAQUE.lower()} em destaque contra os demais diagnósticos'
    return aplicar_layout(fig, titulo)


def fig_tercis_ggt(df):
    ordem = _categorias(df)
    niveis = list(df['ggt_nivel'].cat.categories)
    cont = pd.crosstab(df['categoria'], df['ggt_nivel']).reindex(index=ordem, columns=niveis, fill_value=0)
    pct = cont.div(cont.sum(axis=1), axis=0) * 100

    longo = pct.stack().rename('pct').reset_index().merge(
        cont.stack().rename('n').reset_index(), on=['categoria', 'ggt_nivel'])
    longo['rotulo_cat'] = longo['categoria'].map(lambda c: _rotulo_com_n(df, c))

    # Atributo pré-atentivo da visualização 6: intensidade crescente de azul, com o tercil superior
    # mais escuro e posicionado no início de todas as barras (origem comum para a comparação).
    cores = dict(zip(niveis, ['#c6dbef', '#6baed6', '#08519c']))
    fig = px.bar(
        longo, x='pct', y='rotulo_cat', color='ggt_nivel', orientation='h', text=longo['pct'].round(1),
        category_orders={'ggt_nivel': niveis[::-1], 'rotulo_cat': [_rotulo_com_n(df, c) for c in ordem]},
        color_discrete_map=cores, custom_data=['n'],
        labels={'pct': '% dos participantes do diagnóstico', 'rotulo_cat': 'Diagnóstico', 'ggt_nivel': 'Tercil de GGT'},
    )
    fig.update_traces(texttemplate='%{text}%', textposition='inside',
                      hovertemplate='%{y}<br>%{fullData.name}: %{x:.1f}% (%{customdata[0]} participantes)<extra></extra>')
    fig.update_xaxes(range=[0, 100])
    fig.update_layout(barmode='stack')
    return aplicar_layout(fig, 'Distribuição dos tercis de GGT dentro de cada diagnóstico',
                          eixo_x='% dos participantes do diagnóstico', eixo_y='Diagnóstico')


EXPLORATORIAS = [
    {'chave': 'composicao_amostra', 'titulo': 'Visualização 1 — Composição da amostra por categoria e sexo',
     'funcao': fig_composicao_amostra},
    {'chave': 'ausentes', 'titulo': 'Visualização 2 — Distribuição dos valores ausentes',
     'funcao': fig_ausentes_por_categoria},
    {'chave': 'ast_ggt', 'titulo': 'Visualização 3 — Relação entre AST e GGT', 'funcao': fig_ast_ggt},
    {'chave': 'spearman', 'titulo': 'Visualização 4 — Associações entre idade e exames',
     'funcao': fig_correlacao_spearman},
]

EXPLANATORIAS = [
    {'chave': 'perfis', 'titulo': 'Visualização 5 — Diferenças dos perfis laboratoriais entre categorias',
     'funcao': fig_perfis_laboratoriais},
    {'chave': 'tercis_ggt', 'titulo': 'Visualização 6 — Distribuição dos tercis de GGT por categoria',
     'funcao': fig_tercis_ggt},
]


# ---------------------------------------------------------------------------
# Explorador livre
# ---------------------------------------------------------------------------

def fig_relacao(df, x, y, cor=None):
    quant_x, quant_y = eh_quantitativa(df, x), eh_quantitativa(df, y)
    cores = config.CORES_CATEGORIA if cor == 'categoria' else None
    comum = dict(category_orders=_ordens(df), labels=_rotulos(df), color_discrete_map=cores)

    if quant_x and quant_y:
        fig = px.scatter(df, x=x, y=y, color=cor, opacity=0.75, **comum)
    elif quant_y:
        fig = px.box(df, x=x, y=y, color=cor, points='outliers', **comum)
    elif quant_x:
        fig = px.box(df, x=x, y=y, color=cor, points='outliers', orientation='h', **comum)
    else:
        cores = config.CORES_CATEGORIA if y == 'categoria' else None
        comum['color_discrete_map'] = cores
        fig = px.histogram(df, x=x, color=y, barmode='group', **comum)
        fig.update_yaxes(title_text='Registros')

    titulo = f'{config.NOMES.get(y, y)} × {config.NOMES.get(x, x)}'
    return aplicar_layout(fig, f'{titulo} (n = {len(df)})')


# ---------------------------------------------------------------------------
# Parte Comum
# ---------------------------------------------------------------------------

def fig_cotovelo(cotovelo, k_livre=None):
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_scatter(x=cotovelo['k'], y=cotovelo['inercia'], mode='lines+markers', name='Inércia')
    if 'silhueta' in cotovelo:
        fig.add_scatter(x=cotovelo['k'], y=cotovelo['silhueta'], mode='lines+markers', name='Silhueta',
                        line=dict(dash='dot', color='gray'), secondary_y=True)
    if k_livre is not None:
        fig.add_vline(x=k_livre, line_dash='dash', line_color='firebrick',
                      annotation_text=f'k livre = {k_livre}')
    fig.update_yaxes(title_text='Inércia', secondary_y=False)
    fig.update_yaxes(title_text='Coeficiente de silhueta', secondary_y=True)
    return aplicar_layout(fig, 'Método do Cotovelo — K-Means com k de 2 a 10', eixo_x='Número de clusters (k)')


def fig_clusters(clusters, passada):
    dados = clusters.assign(cluster=clusters[f'cluster_{passada}'].astype(str))
    ordem = sorted(dados['cluster'].unique(), key=int)
    fig = px.scatter(
        dados, x='x_vis', y='y_vis', color='cluster', category_orders={'cluster': ordem},
        hover_data=['classe_real', f'classe_mapeada_{passada}'], opacity=0.75,
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
        hover_data=['classe_real'], opacity=0.75,
    )
    return aplicar_layout(fig, 'Transição entre as passadas: classe mapeada de cada registro',
                          eixo_x='PC1', eixo_y='PC2')


def fig_matriz_confusao(matriz, titulo):
    fig = px.imshow(
        matriz, text_auto=True, color_continuous_scale='Blues', aspect='auto',
        labels=dict(x='Classe mapeada', y='Classe real', color='Registros'),
    )
    return aplicar_layout(fig, titulo)


def fig_composicao(composicao, titulo):
    fig = px.imshow(
        composicao, text_auto=True, color_continuous_scale='Greens', aspect='auto',
        labels=dict(x='Cluster', y='Classe real', color='Registros'),
    )
    return aplicar_layout(fig, titulo)
