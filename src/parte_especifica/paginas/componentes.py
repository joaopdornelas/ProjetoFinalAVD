import streamlit as st

import notas


def texto_ou_pendente(texto, descricao):
    if texto and texto.strip():
        st.markdown(texto)
    else:
        st.info(f'{descricao} ainda não definido em notas.py.')


def mostrar_nota(chave):
    nota = notas.NOTAS.get(chave)
    if not nota:
        st.info('Nota analítica ainda não escrita em notas.py.')
        return
    st.markdown(f"**O que está sendo mostrado.** {nota.get('o_que_mostra', '')}")
    st.markdown(f"**Insight.** {nota.get('insight', '')}")
    st.markdown(f"**Por que este gráfico.** {nota.get('por_que_esse_grafico', '')}")


def mostrar_visualizacoes(df, visualizacoes, descricao):
    if not visualizacoes:
        st.info(f'Nenhuma visualização {descricao} registrada em graficos.py.')
        return
    for item in visualizacoes:
        st.subheader(item['titulo'])
        st.plotly_chart(item['funcao'](df), width='stretch', key=f"graf_{item['chave']}")
        mostrar_nota(item['chave'])
        st.divider()
