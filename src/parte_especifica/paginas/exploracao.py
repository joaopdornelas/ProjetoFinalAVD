import streamlit as st

import graficos
from paginas import componentes


def render(df):
    st.title('Exploração')
    st.caption('Visualizações exploratórias, cada uma seguida da sua nota analítica.')
    componentes.mostrar_visualizacoes(df, graficos.EXPLORATORIAS, 'exploratória')
