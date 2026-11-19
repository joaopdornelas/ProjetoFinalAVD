# ProjetoFinalAVD

Projeto final da disciplina de Análise e Visualização de Dados (AVD) — 2026.2.

- **Parte Comum:** EDA e agrupamento com K-Means (duas passadas) sobre dataset fornecido, com matriz de confusão e métricas.
- **Parte Específica:** EDA, storytelling e dashboard interativo em Streamlit sobre dataset escolhido pelo grupo.

## Estrutura

```
ProjetoFinalAVD/
├─ README.md
├─ requirements.txt
├─ docs/                      # declaração de uso de IA e matriz de contribuição
├─ data/
│  ├─ parte_comum/            # dataset da Parte Comum
│  └─ parte_especifica/       # dataset da Parte Específica
├─ out/
│  ├─ parte_comum/
│  └─ parte_especifica/
├─ notebooks/
│  └─ parte_comum/
│     ├─ eda.ipynb
│     └─ kmeans_metricas.ipynb
├─ src/
│  ├─ parte_comum/
│  └─ parte_especifica/
│     ├─ eda.ipynb
│     └─ dashboard.py
└─ relatorio.pdf
```

## Instalação

Requer Python 3.11 ou superior.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

## Execução

```bash
# Parte Comum
jupyter notebook notebooks/parte_comum/eda.ipynb
jupyter notebook notebooks/parte_comum/kmeans_metricas.ipynb

# Parte Específica
jupyter notebook src/parte_especifica/eda.ipynb
streamlit run src/parte_especifica/dashboard.py
```

## Autores

- João Pedro Rodrigues
