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

    st.plotly_chart(graficos.fig_cotovelo(dados['cotovelo'], k_livre, k_fixo), width='stretch', key='pc_cotovelo')
    st.caption(
        'A inércia sempre diminui quando k aumenta; o k livre é o ponto em que essa queda perde força (o cotovelo). '
        'A silhueta varia de −1 a 1 e compara a proximidade ao próprio cluster com a proximidade ao cluster vizinho. '
        'Os valores próximos de zero indicam pouca separação nos agrupamentos testados. '
        'O maior valor de silhueta ocorre em k = 2, enquanto o cotovelo indica k = 6.'
    )

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
        st.plotly_chart(graficos.fig_composicao(dados[f'composicao_{passada}'],
                                                f'Classe real × cluster — passada {passada}'),
                        width='stretch', key='pc_composicao')

    st.divider()
    st.subheader('Do cluster à classe original')
    st.markdown(
        'O K-Means não conhece as classes. Depois do agrupamento, cada cluster recebe a classe que mais aparece '
        'entre os seus registros (classe majoritária), indicada no rótulo de cada coluna (“Cluster N → classe”). '
        'No heatmap, cada linha é uma classe real e mostra como os seus registros se distribuem entre os clusters, '
        'em percentual da linha, com a contagem entre parênteses. As células com contorno são aquelas em que o '
        'cluster recebeu a própria classe da linha, e a soma delas é o recall da classe. Classes que não são '
        'majoritárias em nenhum cluster não têm célula com contorno e, por isso, continuam com recall zero.'
    )
    st.plotly_chart(graficos.fig_classe_cluster(dados['clusters'], passada), width='stretch',
                    key='pc_classe_cluster')
    st.markdown('**Mapeamento de cada cluster**')
    st.dataframe(graficos.tabela_mapeamento(dados['clusters'], passada), width='stretch', hide_index=True)

    with st.expander('Transição animada entre as passadas'):
        st.plotly_chart(graficos.fig_clusters_animado(dados['clusters']), width='stretch', key='pc_animacao')
