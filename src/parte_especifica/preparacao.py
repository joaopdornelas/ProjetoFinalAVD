"""Transforma o CSV bruto do Hepatitis C no CSV tratado usado pelo EDA e pelo dashboard.

Uso, a partir da raiz do repositório:
    python src/parte_especifica/preparacao.py
"""

import warnings

import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

import config

# ---------------------------------------------------------------------------
# Decisões do grupo. Cada uma precisa de justificativa no relatório.
# ---------------------------------------------------------------------------

# Destino das linhas "0s=suspect Blood Donor": 'manter', 'juntar_doadores' ou 'excluir'.
DESTINO_SUSPEITOS = 'manter'

# Tratamento dos ausentes: None (ainda não decidido), 'mediana_global', 'mediana_por_grupo' ou 'knn'.
ESTRATEGIA_AUSENTES = None
VIZINHOS_KNN = 5

# Tratamento dos outliers: None (manter) ou 'clip' (limitar aos percentis abaixo).
TRATAMENTO_OUTLIERS = None
PERCENTIS_CLIP = (0.01, 0.99)
COLS_OUTLIERS = config.COLS_EXAMES

# Discretizações: cada entrada cria uma nova variável qualitativa ordenada a partir de uma quantitativa.
#   'origem':  coluna quantitativa de origem
#   'tecnica': 'cut' (limites fixos e interpretáveis) ou 'qcut' (quantis, grupos de tamanho igual)
#   'limites': lista de limites para 'cut' ou número de grupos para 'qcut'
#   'rotulos': nomes das faixas, em ordem crescente
# Convenção de nomes: 'faixa_etaria' para a idade e '<exame>_nivel' para um exame (ex.: 'alt_nivel').
# Formato:
#   DISCRETIZACOES = {
#       'faixa_etaria': {'origem': 'idade', 'tecnica': 'cut', 'limites': [...], 'rotulos': [...]},
#       '<exame>_nivel': {'origem': '<exame>', 'tecnica': 'cut', 'limites': [...], 'rotulos': [...]},
#   }
DISCRETIZACOES = {
    'faixa_etaria': {
        'origem': 'idade',
        'tecnica': 'cut',
        'limites': [19, 39, 59, float('inf')],
        'rotulos': ['19 a 39 anos', '40 a 59 anos', '60 anos ou mais'],
    },
    'ggt_nivel': {
        'origem': 'ggt',
        'tecnica': 'qcut',
        'limites': 3,
        'rotulos': ['Tercil inferior', 'Tercil intermediário', 'Tercil superior'],
    },
}


def carregar_bruto():
    return pd.read_csv(config.ARQ_BRUTO, index_col=0)


def renomear_colunas(df):
    return df.rename(columns=config.MAPA_COLUNAS)


def separar_categoria(df):
    df = df.copy()
    partes = df['categoria'].str.split('=', n=1, expand=True)
    df['categoria_cod'] = partes[0]
    df['categoria'] = partes[1]
    return df


def tratar_suspeitos(df):
    suspeitos = df['categoria'] == 'suspect Blood Donor'
    if DESTINO_SUSPEITOS == 'manter':
        return df
    if DESTINO_SUSPEITOS == 'juntar_doadores':
        df = df.copy()
        df.loc[suspeitos, 'categoria'] = 'Blood Donor'
        df.loc[suspeitos, 'categoria_cod'] = '0'
        return df
    if DESTINO_SUSPEITOS == 'excluir':
        return df.loc[~suspeitos].copy()
    raise ValueError(f'DESTINO_SUSPEITOS inválido: {DESTINO_SUSPEITOS}')


def marcar_ausentes(df):
    df = df.copy()
    for col in config.COLS_EXAMES:
        if df[col].isna().any():
            df[f'{col}_ausente'] = df[col].isna()
    return df


def tratar_ausentes(df):
    if ESTRATEGIA_AUSENTES is None:
        return df

    df = df.copy()
    cols = [c for c in config.COLS_EXAMES if df[c].isna().any()]

    if ESTRATEGIA_AUSENTES == 'mediana_global':
        for col in cols:
            df[col] = df[col].fillna(df[col].median())
    elif ESTRATEGIA_AUSENTES == 'mediana_por_grupo':
        for col in cols:
            df[col] = df[col].fillna(df.groupby('categoria')[col].transform('median'))
    elif ESTRATEGIA_AUSENTES == 'knn':
        scaler = StandardScaler()
        padronizado = scaler.fit_transform(df[config.COLS_QUANTITATIVAS])
        imputado = KNNImputer(n_neighbors=VIZINHOS_KNN).fit_transform(padronizado)
        df[config.COLS_QUANTITATIVAS] = scaler.inverse_transform(imputado)
        df['idade'] = df['idade'].round().astype(int)
    else:
        raise ValueError(f'ESTRATEGIA_AUSENTES inválida: {ESTRATEGIA_AUSENTES}')
    return df


def tratar_outliers(df):
    if TRATAMENTO_OUTLIERS is None:
        return df
    if TRATAMENTO_OUTLIERS == 'clip':
        df = df.copy()
        p_inf, p_sup = PERCENTIS_CLIP
        for col in COLS_OUTLIERS:
            df[col] = df[col].clip(df[col].quantile(p_inf), df[col].quantile(p_sup))
        return df
    raise ValueError(f'TRATAMENTO_OUTLIERS inválido: {TRATAMENTO_OUTLIERS}')


def discretizar(df):
    df = df.copy()
    for nova, regra in DISCRETIZACOES.items():
        origem = df[regra['origem']]
        if regra['tecnica'] == 'cut':
            df[nova] = pd.cut(origem, bins=regra['limites'], labels=regra['rotulos'], include_lowest=True)
        elif regra['tecnica'] == 'qcut':
            df[nova] = pd.qcut(origem, q=regra['limites'], labels=regra['rotulos'])
        else:
            raise ValueError(f"Técnica inválida em {nova}: {regra['tecnica']}")
        fora = int(df[nova].isna().sum() - origem.isna().sum())
        if fora:
            warnings.warn(f'{fora} valores de {regra["origem"]} ficaram fora dos limites de {nova}.')
    return df


def ajustar_tipos(df):
    df = df.copy()
    ordem = [c for c in config.ORDEM_CATEGORIAS if c in set(df['categoria'])]
    df['categoria'] = pd.Categorical(df['categoria'], categories=ordem, ordered=True)
    df['sexo'] = pd.Categorical(df['sexo'], categories=config.ORDEM_SEXO)
    for nova, regra in DISCRETIZACOES.items():
        if nova in df:
            df[nova] = pd.Categorical(df[nova], categories=regra['rotulos'], ordered=True)
    return df


def colunas_qualitativas(df):
    return config.COLS_QUALITATIVAS + [c for c in DISCRETIZACOES if c in df]


def preparar():
    df = carregar_bruto()
    df = renomear_colunas(df)
    df = separar_categoria(df)
    df = tratar_suspeitos(df)
    df = marcar_ausentes(df)
    df = tratar_ausentes(df)
    df = tratar_outliers(df)
    df = discretizar(df)
    df = ajustar_tipos(df)
    return df


def carregar_tratado():
    df = pd.read_csv(config.ARQ_TRATADO, index_col=0)
    return ajustar_tipos(df)


def main():
    df = preparar()

    restantes = int(df[config.COLS_EXAMES].isna().sum().sum())
    if restantes:
        warnings.warn(
            f'{restantes} valores ausentes ainda sem tratamento. '
            'Defina ESTRATEGIA_AUSENTES antes da versão final.'
        )

    config.DIR_OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.ARQ_TRATADO, index_label='paciente')
    print(f'{len(df)} linhas e {df.shape[1]} colunas gravadas em {config.ARQ_TRATADO}')


if __name__ == '__main__':
    main()
