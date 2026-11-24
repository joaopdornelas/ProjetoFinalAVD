from pathlib import Path

DIR_RAIZ = Path(__file__).resolve().parents[2]

ARQ_BRUTO = DIR_RAIZ / 'data' / 'parte_especifica' / 'HepatitisCdata.csv'
DIR_OUT = DIR_RAIZ / 'out' / 'parte_especifica'
ARQ_TRATADO = DIR_OUT / 'hepatite_tratado.csv'
DIR_FIGURAS = DIR_OUT / 'figuras'
DIR_OUT_COMUM = DIR_RAIZ / 'out' / 'parte_comum'
ARQ_RELATORIO = DIR_RAIZ / 'relatorio.pdf'

RANDOM_STATE = 42

MAPA_COLUNAS = {
    'Category': 'categoria',
    'Age': 'idade',
    'Sex': 'sexo',
    'ALB': 'alb',
    'ALP': 'alp',
    'ALT': 'alt',
    'AST': 'ast',
    'BIL': 'bil',
    'CHE': 'che',
    'CHOL': 'chol',
    'CREA': 'crea',
    'GGT': 'ggt',
    'PROT': 'prot',
}

COLS_EXAMES = ['alb', 'alp', 'alt', 'ast', 'bil', 'che', 'chol', 'crea', 'ggt', 'prot']
COLS_QUANTITATIVAS = ['idade'] + COLS_EXAMES
COLS_QUALITATIVAS = ['categoria', 'sexo']

NOMES = {
    'categoria': 'Diagnóstico',
    'categoria_cod': 'Código do diagnóstico',
    'idade': 'Idade',
    'sexo': 'Sexo',
    'alb': 'Albumina (ALB)',
    'alp': 'Fosfatase alcalina (ALP)',
    'alt': 'Alanina aminotransferase (ALT)',
    'ast': 'Aspartato aminotransferase (AST)',
    'bil': 'Bilirrubina (BIL)',
    'che': 'Colinesterase (CHE)',
    'chol': 'Colesterol (CHOL)',
    'crea': 'Creatinina (CREA)',
    'ggt': 'Gama-glutamil transferase (GGT)',
    'prot': 'Proteína total (PROT)',
    'faixa_etaria': 'Faixa etária',
    'ggt_nivel': 'Tercil de GGT',
}

# A página do dataset na UCI não informa as unidades. Estas são as usuais para cada exame e batem
# com as faixas de valores da base, mas ainda precisam ser conferidas no artigo de origem
# (Hoffmann et al., 2018).
UNIDADES = {
    'idade': 'anos',
    'alb': 'g/L',
    'alp': 'U/L',
    'alt': 'U/L',
    'ast': 'U/L',
    'bil': 'µmol/L',
    'che': 'kU/L',
    'chol': 'mmol/L',
    'crea': 'µmol/L',
    'ggt': 'U/L',
    'prot': 'g/L',
}

# Rótulo original do CSV (texto depois do "=" em Category) e o nome usado no projeto.
MAPA_CATEGORIAS = {
    'Blood Donor': 'Doador',
    'suspect Blood Donor': 'Doador suspeito',
    'Hepatitis': 'Hepatite',
    'Fibrosis': 'Fibrose',
    'Cirrhosis': 'Cirrose',
}
ORDEM_CATEGORIAS = ['Doador', 'Doador suspeito', 'Hepatite', 'Fibrose', 'Cirrose']
CATEGORIAS_DOADORES = ['Doador', 'Doador suspeito']
CORES_CATEGORIA = {
    'Doador': '#0072B2',
    'Doador suspeito': '#56B4E9',
    'Hepatite': '#E69F00',
    'Fibrose': '#D55E00',
    'Cirrose': '#CC79A7',
}

ORDEM_SEXO = ['m', 'f']
ROTULOS_SEXO = {'m': 'Masculino', 'f': 'Feminino'}


def rotulo(coluna):
    """Nome da coluna para eixos e legendas, com a unidade entre colchetes quando houver."""
    nome = NOMES.get(coluna, coluna)
    unidade = UNIDADES.get(coluna)
    return f'{nome} [{unidade}]' if unidade else nome
