import streamlit as st

import config
import notas
from paginas import componentes


def render(df):
    st.title('Hepatite C: exames laboratoriais e diagnóstico')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Pergunta de pesquisa')
        componentes.texto_ou_pendente(notas.PERGUNTA, 'Pergunta de pesquisa')
    with col2:
        st.subheader('Público-alvo')
        componentes.texto_ou_pendente(notas.PUBLICO_ALVO, 'Público-alvo')

    with st.expander('Enquadramento: classificação ou agrupamento'):
        componentes.texto_ou_pendente(notas.ENQUADRAMENTO, 'Enquadramento')

    st.subheader('Sobre os dados')
    st.markdown(
        'Exames de sangue e dados demográficos de doadores de sangue e de pacientes com hepatite C '
        'em diferentes estágios (hepatite, fibrose e cirrose). Fonte: *HCV data*, UCI Machine Learning '
        'Repository (Lichtinghagen, Klawonn e Hoffmann, 2020), licença CC BY 4.0.'
    )

    doadores = df['categoria'].isin(config.CATEGORIAS_DOADORES)
    cols_ausente = [c for c in df.columns if c.endswith('_ausente')]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric('Registros no recorte', len(df))
    m2.metric('Doadores', int(doadores.sum()))
    m3.metric('Pacientes com doença hepática', int((~doadores).sum()))
    m4.metric('Valores ausentes no bruto', int(df[cols_ausente].sum().sum()) if cols_ausente else 0)

    st.markdown('**Registros por diagnóstico e sexo**')
    tabela = df.groupby(['categoria', 'sexo'], observed=False).size().unstack(fill_value=0)
    tabela = tabela.rename(columns=config.ROTULOS_SEXO)
    tabela['Total'] = tabela.sum(axis=1)
    st.dataframe(tabela, width='stretch')

    st.subheader('Exportar')
    d1, d2 = st.columns(2)
    d1.download_button(
        'Baixar o recorte filtrado (CSV)',
        df.to_csv(index=False).encode('utf-8'),
        file_name='hepatite_recorte.csv',
        mime='text/csv',
    )
    if config.ARQ_RELATORIO.exists():
        d2.download_button(
            'Baixar o relatório (PDF)',
            config.ARQ_RELATORIO.read_bytes(),
            file_name='relatorio.pdf',
            mime='application/pdf',
        )
    else:
        d2.caption('O relatório em PDF ainda não está na raiz do projeto.')
