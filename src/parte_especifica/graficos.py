"""Funções de gráfico: cada uma recebe um DataFrame e devolve uma figura plotly."""

import pandas as pd
import plotly.express as px
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


# ---------------------------------------------------------------------------
# As 6 visualizações oficiais (4 exploratórias e 2 explanatórias) são definidas pelo grupo.
# Cada uma vira uma função fig_<nome>(df) e é registrada numa das listas abaixo, por exemplo:
#     EXPLORATORIAS.append({'chave': 'exp1', 'titulo': '...', 'funcao': fig_exp1})
# A chave liga o gráfico à nota analítica em notas.NOTAS.
# ---------------------------------------------------------------------------

EXPLORATORIAS = []
EXPLANATORIAS = []


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
