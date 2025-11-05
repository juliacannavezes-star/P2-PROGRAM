import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# ===============================
# CONFIGURAÇÃO INICIAL
# ===============================
st.set_page_config(
    page_title="Painel Interativo SISDEPEN",
    page_icon="📊",
    layout="wide"
)

# ===============================
# LEITURA DOS DADOS
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("sisdepen_baseunica_18_28102025_173932_csv.xlsx")
    return df

df = load_data()

st.title("📊 Painel Interativo do Sistema Penitenciário Brasileiro (SISDEPEN)")
st.markdown("### Explore os dados oficiais sobre o sistema penitenciário de forma interativa.")

# ===============================
# FILTROS INTERATIVOS
# ===============================
st.sidebar.header("🎯 Filtros")
coluna_estado = st.sidebar.selectbox("Selecione o Estado", ["Todos"] + sorted(df['UF'].dropna().unique().tolist()))
coluna_ano = st.sidebar.selectbox("Selecione o Ano", ["Todos"] + sorted(df['Ano'].dropna().unique().tolist()))

if coluna_estado != "Todos":
    df = df[df["UF"] == coluna_estado]
if coluna_ano != "Todos":
    df = df[df["Ano"] == coluna_ano]

# ===============================
# GRÁFICOS INTERATIVOS
# ===============================
st.markdown("## 📍 Distribuição Geral")

# Exemplo 1: População carcerária por estado
if "UF" in df.columns:
    fig1 = px.bar(
        df.groupby("UF")["População Carcerária"].sum().reset_index(),
        x="UF", y="População Carcerária",
        title="População Carcerária por Estado",
        color="UF"
    )
    st.plotly_chart(fig1, use_container_width=True)

# Exemplo 2: Regime prisional
if "Regime" in df.columns:
    fig2 = px.pie(
        df, names="Regime",
        title="Distribuição por Regime Prisional",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig2, use_container_width=True)

# Exemplo 3: Gênero
if "Sexo" in df.columns:
    fig3 = px.histogram(
        df, x="Sexo",
        title="Distribuição por Sexo",
        color="Sexo"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ===============================
# ÍCONES INFORMATIVOS
# ===============================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👮‍♂️ Total de Presos", int(df["População Carcerária"].sum()))
with col2:
    st.metric("🏢 Número de Unidades", df["Unidade Prisional"].nunique())
with col3:
    st.metric("📅 Último Ano Registrado", int(df["Ano"].max()) if "Ano" in df.columns else "N/D")

st.success("✅ Dados carregados com sucesso! Interaja com os gráficos para explorar mais detalhes.")
