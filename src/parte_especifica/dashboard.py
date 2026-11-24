"""Dashboard da Parte Específica (Hepatite C), com uma página para os resultados da Parte Comum.

Uso, a partir da raiz do repositório:
    streamlit run src/parte_especifica/dashboard.py
"""

import pandas as pd
import streamlit as st

import config
import preparacao
from paginas import contexto, exploracao, explorador, parte_comum, resposta

st.set_page_config(page_title='Projeto Final AVD — Hepatite C', layout='wide')

# Fonte e espaçamento maiores nas opções da barra lateral.
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-size: 16.5px !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PAGINAS = {
    'Contexto': contexto,
    'Exploração': exploracao,
    'Resposta': resposta,
    'Explorador livre': explorador,
    'Parte Comum': parte_comum,
}


@st.cache_data
def carregar_hepatite():
    return preparacao.carregar_tratado()


@st.cache_data
def carregar_parte_comum():
    pasta = config.DIR_OUT_COMUM
    if not (pasta / 'resumo.csv').exists():
        return None
    return {
        'resumo': pd.read_csv(pasta / 'resumo.csv'),
        'cotovelo': pd.read_csv(pasta / 'cotovelo.csv'),
        'clusters': pd.read_csv(pasta / 'clusters.csv'),
        'matriz_livre': pd.read_csv(pasta / 'matriz_confusao_livre.csv', index_col=0),
        'matriz_fixo': pd.read_csv(pasta / 'matriz_confusao_fixo.csv', index_col=0),
        'metricas_livre': pd.read_csv(pasta / 'metricas_livre.csv'),
        'metricas_fixo': pd.read_csv(pasta / 'metricas_fixo.csv'),
        'composicao_livre': pd.read_csv(pasta / 'composicao_livre.csv', index_col=0),
        'composicao_fixo': pd.read_csv(pasta / 'composicao_fixo.csv', index_col=0),
    }


def aplicar_filtros(df, categorias, sexos, idade_min, idade_max):
    return df[
        df['categoria'].isin(categorias)
        & df['sexo'].isin(sexos)
        & df['idade'].between(idade_min, idade_max)
    ]


st.sidebar.title('Navegação')
pagina = st.sidebar.radio('Página', list(PAGINAS), key='pagina')

if not config.ARQ_TRATADO.exists():
    st.error('Arquivo tratado não encontrado. Rode antes: python src/parte_especifica/preparacao.py')
    st.stop()

df = carregar_hepatite()

st.sidebar.divider()
st.sidebar.header('Filtros')
todas_categorias = list(df['categoria'].cat.categories)
categorias = st.sidebar.multiselect('Diagnóstico', todas_categorias, default=todas_categorias, key='f_categoria')
sexos = st.sidebar.multiselect('Sexo', config.ORDEM_SEXO, default=config.ORDEM_SEXO, key='f_sexo',
                               format_func=lambda s: config.ROTULOS_SEXO[s])
limites_idade = (int(df['idade'].min()), int(df['idade'].max()))
idade_min, idade_max = st.sidebar.slider('Idade (anos)', *limites_idade, value=limites_idade, key='f_idade')

df_filtrado = aplicar_filtros(df, categorias, sexos, idade_min, idade_max)
st.sidebar.caption(f'{len(df_filtrado)} de {len(df)} registros no recorte')

if pagina == 'Parte Comum':
    st.sidebar.caption('Os filtros não se aplicam à Parte Comum, que usa outro dataset.')
    parte_comum.render(carregar_parte_comum())
    st.stop()

if df_filtrado.empty:
    st.warning('Nenhum registro atende aos filtros escolhidos. Amplie a seleção na barra lateral.')
    st.stop()

PAGINAS[pagina].render(df_filtrado)
