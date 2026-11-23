import streamlit as st

import graficos
import notas
from paginas import componentes


def render(df):
    st.title('Resposta à pergunta de pesquisa')
    componentes.texto_ou_pendente(notas.PERGUNTA, 'Pergunta de pesquisa')
    st.divider()

    componentes.mostrar_visualizacoes(df, graficos.EXPLANATORIAS, 'explanatória')

    st.subheader('Resposta')
    componentes.texto_ou_pendente(notas.RESPOSTA, 'Resposta à pergunta de pesquisa')
