import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# CONFIGURAÇÕES INICIAIS
# ---------------------------
st.set_page_config(
    page_title="Painel Interativo - Sistema Penitenciário",
    page_icon="⚖️",
    layout="wide"
)

# ---------------------------
# LEITURA DOS DADOS
# ---------------------------
@st.cache_data
def carregar_dados():
    df = pd.read_excel("sisdepen_baseunica_18_28102025_173932_csv.xlsx")
    return df

df = carregar_dados()

st.title("⚖️ Painel Interativo - Sistema Penitenciário Brasileiro")
st.markdown("### Dados oficiais - Fonte: Sisdepen (Ministério da Justiça)")
st.divider()

# ---------------------------
# FILTROS INTERATIVOS
# ---------------------------
col1, col2 = st.columns(2)
with col1:
    estado = st.selectbox("📍 Selecione o Estado:", sorted(df["UF"].dropna().unique()))
with col2:
    ano = st.selectbox("📅 Selecione o Ano:", sorted(df["Ano"].dropna().unique()))

filtro = df[(df["UF"] == estado) & (df["Ano"] == ano)]

# ---------------------------
# GRÁFICOS INTERATIVOS
# ---------------------------
st.subheader(f"📊 Indicadores de {estado} em {ano}")

if not filtro.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            filtro,
            x="Natureza da Prisão",
            y="Quantidade",
            title="🚔 Natureza das Prisões",
            color="Natureza da Prisão",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(
            filtro,
            names="Sexo",
            values="Quantidade",
            title="🧍 Distribuição por Sexo",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Gráfico extra
    st.subheader("🏛️ Tipos de Estabelecimentos Prisionais")
    fig3 = px.bar(
        filtro,
        x="Tipo de Estabelecimento",
        y="Quantidade",
        color="Tipo de Estabelecimento",
        title="Distribuição dos Estabelecimentos"
    )
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("Nenhum dado disponível para o filtro selecionado.")
