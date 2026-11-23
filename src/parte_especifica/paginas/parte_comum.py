import streamlit as st

import graficos


def render(dados):
    st.title('Parte Comum — K-Means no dataset Obesity')
    if dados is None:
        st.error('Arquivos de out/parte_comum não encontrados. Rode o notebook kmeans_metricas.ipynb.')
        return

    resumo = dados['resumo'].set_index('passada')
    k_livre = int(resumo.loc['livre', 'k'])
    k_fixo = int(resumo.loc['fixo', 'k'])

    m1, m2 = st.columns(2)
    m1.metric(f'Acurácia — Passada 1 (k livre = {k_livre})', f"{resumo.loc['livre', 'acuracia']:.1%}")
    m2.metric(f'Acurácia — Passada 2 (k fixo = {k_fixo})', f"{resumo.loc['fixo', 'acuracia']:.1%}")
    st.caption('A acurácia mede a concordância entre os clusters e as classes reais após o mapeamento '
               'de cada cluster para a sua classe majoritária.')

    st.plotly_chart(graficos.fig_cotovelo(dados['cotovelo'], k_livre), width='stretch', key='pc_cotovelo')

    st.divider()
    passada = st.radio('Passada', ['livre', 'fixo'], horizontal=True, key='pc_passada',
                       format_func=lambda p: f'Passada 1 — k livre ({k_livre})' if p == 'livre'
                       else f'Passada 2 — k fixo ({k_fixo})')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(graficos.fig_clusters(dados['clusters'], passada), width='stretch', key='pc_clusters')
    with c2:
        matriz = dados[f'matriz_{passada}']
        st.plotly_chart(graficos.fig_matriz_confusao(matriz, f'Matriz de confusão — passada {passada}'),
                        width='stretch', key='pc_matriz')

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('**Precisão e recall por classe**')
        st.dataframe(dados[f'metricas_{passada}'].round(3), width='stretch', hide_index=True)
    with c4:
        composicao = dados.get(f'composicao_{passada}')
        if composicao is not None:
            st.plotly_chart(graficos.fig_composicao(composicao, f'Classe real × cluster — passada {passada}'),
                            width='stretch', key='pc_composicao')

    with st.expander('Transição animada entre as passadas'):
        st.plotly_chart(graficos.fig_clusters_animado(dados['clusters']), width='stretch', key='pc_animacao')
