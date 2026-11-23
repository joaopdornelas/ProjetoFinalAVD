import streamlit as st

import config
import graficos
import preparacao

SEM_COR = '(nenhuma)'


def _variaveis(df):
    quantitativas = [c for c in config.COLS_QUANTITATIVAS if c in df]
    qualitativas = preparacao.colunas_qualitativas(df) + [c for c in df.columns if c.endswith('_ausente')]
    return quantitativas, qualitativas


def render(df):
    st.title('Explorador livre')
    st.caption('Escolha duas variáveis quaisquer; o tipo de gráfico acompanha o tipo das variáveis.')

    quantitativas, qualitativas = _variaveis(df)
    todas = quantitativas + qualitativas

    c1, c2, c3 = st.columns(3)
    x = c1.selectbox('Eixo x', todas, index=todas.index('idade'), format_func=config.rotulo, key='exp_x')
    y = c2.selectbox('Eixo y', todas, index=todas.index('alb'), format_func=config.rotulo, key='exp_y')
    opcoes_cor = [SEM_COR] + qualitativas
    cor = c3.selectbox('Cor', opcoes_cor, index=opcoes_cor.index('categoria'),
                       format_func=lambda c: c if c == SEM_COR else config.rotulo(c), key='exp_cor')
    cor = None if cor == SEM_COR or cor in (x, y) else cor

    st.plotly_chart(graficos.fig_relacao(df, x, y, cor), width='stretch', key='exp_principal')

    st.divider()
    st.subheader('Comparação lado a lado')
    recorte = st.selectbox('Comparar por', qualitativas, format_func=config.rotulo, key='exp_recorte')
    valores = [v for v in df[recorte].dropna().unique()]
    if len(valores) < 2:
        st.info('O filtro atual deixa menos de dois grupos para comparar.')
        return

    valores = sorted(valores, key=str)
    e1, e2 = st.columns(2)
    for coluna, padrao, chave in [(e1, 0, 'exp_lado_a'), (e2, 1, 'exp_lado_b')]:
        with coluna:
            valor = st.selectbox(config.rotulo(recorte), valores, index=padrao, key=chave)
            parte = df[df[recorte] == valor]
            fig = graficos.fig_relacao(parte, x, y, cor)
            fig.update_layout(title=f'{config.NOMES.get(recorte, recorte)} = {valor} (n = {len(parte)})')
            st.plotly_chart(fig, width='stretch', key=f'{chave}_graf')
