import streamlit as st

import notas

CAMPOS_NOTA = [
    ('o_que_mostra', 'O que está sendo mostrado'),
    ('insight', 'Resultados da amostra completa'),
    ('por_que_esse_grafico', 'Por que este gráfico'),
    ('relacao_com_pergunta', 'Relação com a pergunta'),
]


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
    # O container com chave "nota_..." recebe a fonte menor definida no CSS do dashboard.
    with st.container(key=f'nota_{chave}'):
        for campo, titulo in CAMPOS_NOTA:
            if nota.get(campo):
                st.markdown(f'**{titulo}**')
                st.markdown(nota[campo])
        if nota.get('atributo_preatentivo'):
            with st.expander('Atributo pré-atentivo'):
                st.markdown(nota['atributo_preatentivo'])


def mostrar_visualizacoes(df, visualizacoes, descricao):
    if not visualizacoes:
        st.info(f'Nenhuma visualização {descricao} registrada em graficos.py.')
        return
    for item in visualizacoes:
        st.subheader(item['titulo'])
        st.plotly_chart(item['funcao'](df), width='stretch', key=f"graf_{item['chave']}")
        for i, complemento in enumerate(item.get('complementos', [])):
            st.plotly_chart(complemento(df), width='stretch', key=f"graf_{item['chave']}_{i}")
        mostrar_nota(item['chave'])
        st.divider()
