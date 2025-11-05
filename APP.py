# APP.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------
# Configuração da página
# -----------------------
st.set_page_config(
    page_title="Painel Interativo SISDEPEN",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Painel Interativo SISDEPEN")
st.markdown("Visualização interativa dos dados (xlsx).")

# -----------------------
# Local do arquivo (nome que está no seu repositório)
# -----------------------
DATAFILE = Path("sisdepen_baseunica_18_28102025_173932_csv.xlsx")

# -----------------------
# Utilitários
# -----------------------
def safe_read_excel(path: Path) -> pd.DataFrame:
    """Tenta ler o excel com pandas, tratando erros comuns."""
    if not path.exists():
        st.error(f"Arquivo não encontrado: {path}")
        st.stop()
    try:
        df = pd.read_excel(path)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}")
        st.stop()
    return df

@st.cache_data
def load_and_prepare(path: Path) -> pd.DataFrame:
    df = safe_read_excel(path)
    # limpeza básica
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # padroniza nomes: cria aliases caso existam variantes
    # Mapeie colunas comuns para nomes usados no app
    colmap = {}
    cols = set(df.columns.str.lower())

    def find_col(candidates):
        for c in candidates:
            if c.lower() in cols:
                # retorna o nome original do dataframe
                for orig in df.columns:
                    if orig.lower() == c.lower():
                        return orig
        # busca aproximações (prefixo)
        for orig in df.columns:
            low = orig.lower()
            for c in candidates:
                if c.lower() in low or low in c.lower():
                    return orig
        return None

    colmap['UF'] = find_col(['UF','Estado','Unidade Federativa','uf'])
    colmap['Ano'] = find_col(['Ano','Year','ano'])
    colmap['PopCarceraria'] = find_col(['População Carcerária','Populacao Carceraria','População','População total','população carcerária','população'])
    colmap['Regime'] = find_col(['Regime','regime'])
    colmap['Sexo'] = find_col(['Sexo','sexo','Gênero','Genero'])
    colmap['Unidade'] = find_col(['Unidade Prisional','Unidade','Unidade prisional','Unidade Prisional Nome','Unidade Prisional'])

    # Se não encontrou colunas essenciais, não trava — só informa
    st.sidebar.markdown("**Colunas detectadas**")
    for k, v in colmap.items():
        st.sidebar.write(f"- {k}: `{v if v is not None else 'NÃO ENCONTRADA'}`")

    # normaliza: cria colunas usadas pelo app com nomes fixos
    if colmap['UF']:
        df['UF_app'] = df[colmap['UF']]
    else:
        df['UF_app'] = "N/D"

    if colmap['Ano']:
        df['Ano_app'] = df[colmap['Ano']]
    else:
        df['Ano_app'] = pd.NA

    if colmap['PopCarceraria']:
        # tenta converter para numérico e lidar com NA
        df['Pop_app'] = pd.to_numeric(df[colmap['PopCarceraria']], errors='coerce').fillna(0)
    else:
        # fallback: tenta inferir coluna com números grandes
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            df['Pop_app'] = df[numeric_cols[0]].fillna(0)
        else:
            df['Pop_app'] = 0

    if colmap['Regime']:
        df['Regime_app'] = df[colmap['Regime']].astype(str)
    else:
        df['Regime_app'] = "N/D"

    if colmap['Sexo']:
        df['Sexo_app'] = df[colmap['Sexo']].astype(str)
    else:
        df['Sexo_app'] = "N/D"

    if colmap['Unidade']:
        df['Unidade_app'] = df[colmap['Unidade']].astype(str)
    else:
        df['Unidade_app'] = "N/D"

    return df

# -----------------------
# Carrega dados
# -----------------------
df = load_and_prepare(DATAFILE)

# -----------------------
# Painel de filtros
# -----------------------
st.sidebar.header("Filtros")
ufs = ["Todos"] + sorted([u for u in df['UF_app'].dropna().unique().astype(str)])
anos_unique = sorted([a for a in df['Ano_app'].dropna().unique().astype(str)]) if 'Ano_app' in df.columns else []
anos = ["Todos"] + anos_unique

selected_uf = st.sidebar.selectbox("UF", ufs)
selected_ano = st.sidebar.selectbox("Ano", anos)

df_filtered = df.copy()
if selected_uf != "Todos":
    df_filtered = df_filtered[df_filtered['UF_app'].astype(str) == selected_uf]
if selected_ano != "Todos":
    df_filtered = df_filtered[df_filtered['Ano_app'].astype(str) == selected_ano]

# -----------------------
# Métricas (no topo)
# -----------------------
col1, col2, col3 = st.columns(3)
with col1:
    total_presos = int(df_filtered['Pop_app'].sum()) if 'Pop_app' in df_filtered.columns else 0
    st.metric("👮‍♂️ Total de Presos (filtro atual)", f"{total_presos:,}")
with col2:
    num_unidades = int(df_filtered['Unidade_app'].nunique()) if 'Unidade_app' in df_filtered.columns else 0
    st.metric("🏢 Unidades Prisionais (únicas)", f"{num_unidades}")
with col3:
    try:
        ultimo_ano = int(df['Ano_app'].dropna().astype(int).max())
    except Exception:
        ultimo_ano = "N/D"
    st.metric("📅 Último Ano Registrado", f"{ultimo_ano}")

st.markdown("---")
st.markdown("## Gráficos interativos")

# -----------------------
# Gráfico 1: População por UF (barra)
# -----------------------
if 'UF_app' in df_filtered.columns and df_filtered['UF_app'].nunique() > 0:
    pop_by_uf = df_filtered.groupby('UF_app', dropna=False)['Pop_app'].sum().reset_index().sort_values('Pop_app', ascending=False)
    fig1 = px.bar(pop_by_uf, x='UF_app', y='Pop_app', labels={'UF_app': 'UF', 'Pop_app': 'População'}, title='População Carcerária por UF')
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Coluna UF não encontrada ou sem dados suficientes para o gráfico por UF.")

# -----------------------
# Gráfico 2: Distribuição por Regime (pizza)
# -----------------------
if 'Regime_app' in df_filtered.columns and df_filtered['Regime_app'].nunique() > 0:
    regime_counts = df_filtered['Regime_app'].value_counts().reset_index()
    regime_counts.columns = ['Regime', 'Count']
    fig2 = px.pie(regime_counts, names='Regime', values='Count', title='Distribuição por Regime', hole=0.35)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Coluna Regime não encontrada ou sem dados suficientes.")

# -----------------------
# Gráfico 3: Sexo (histograma)
# -----------------------
if 'Sexo_app' in df_filtered.columns and df_filtered['Sexo_app'].nunique() > 0:
    sex_counts = df_filtered['Sexo_app'].value_counts().reset_index()
    sex_counts.columns = ['Sexo', 'Count']
    fig3 = px.bar(sex_counts, x='Sexo', y='Count', title='Distribuição por Sexo')
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Coluna Sexo não encontrada ou sem dados suficientes.")

# -----------------------
# Tabela interativa (mostra as primeiras linhas)
# -----------------------
st.markdown("### Amostra dos dados filtrados")
st.dataframe(df_filtered.head(200))

st.success("✅ App carregado — interaja com os filtros e gráficos acima.")
