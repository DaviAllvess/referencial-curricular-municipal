import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(
    page_title="RCM Presidente Figueiredo - Piloto",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados
@st.cache_data
def load_data():
    json_path = "/workspace/artifacts/matriz_curricular_rcm_2026.json"
    if not os.path.exists(json_path):
        json_path = "matriz_curricular_rcm_2026.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

try:
    data = load_data()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.title("📚 RCM 2026 - Consulta & Planejamento Curricular")
st.caption("Piloto de consulta do Referencial Curricular Municipal de Presidente Figueiredo")

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros de Busca")

componentes = ["Todos"] + sorted(list(df["componente_curricular"].unique()))
comp_sel = st.sidebar.selectbox("Componente Curricular", componentes)

anos = ["Todos"] + sorted(list(df["etapa_ano"].unique()))
ano_sel = st.sidebar.selectbox("Etapa / Ano", anos)

bimestres = ["Todos"] + sorted(list(df["bimestre"].unique()))
bim_sel = st.sidebar.selectbox("Bimestre", bimestres)

dimensoes = ["Todas"] + sorted(list(df["dimensao_rcm"].unique()))
dim_sel = st.sidebar.selectbox("Dimensão do RCM", dimensoes)

# Filtragem
df_filtered = df.copy()

if comp_sel != "Todos":
    df_filtered = df_filtered[df_filtered["componente_curricular"] == comp_sel]
if ano_sel != "Todos":
    df_filtered = df_filtered[df_filtered["etapa_ano"] == ano_sel]
if bim_sel != "Todos":
    df_filtered = df_filtered[df_filtered["bimestre"] == bim_sel]
if dim_sel != "Todas":
    df_filtered = df_filtered[df_filtered["dimensao_rcm"] == dim_sel]

st.subheader(f"📋 Habilidades Encontradas ({len(df_filtered)})")

# Exibição dos cards
for idx, row in df_filtered.iterrows():
    with st.expander(f"📌 [{row['codigo_bncc']}] {row['componente_curricular']} - {row['etapa_ano']} ({row['bimestre']}º Bimestre)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**BNCC Nacional:** `{row['codigo_bncc']}`")
            st.markdown(f"**BNCC Computação:** `{row['codigo_bncc_co']}`")
            st.markdown(f"**Dimensão RCM:** {row['dimensao_rcm']}")
        with col2:
            st.markdown(f"**Inteligências Múltiplas:** {', '.join(row['inteligencias_multiplas']) if isinstance(row['inteligencias_multiplas'], list) else row['inteligencias_multiplas']}")
            st.markdown(f"**Eixo Computação:** {row['eixo_computacao']}")
        
        st.markdown(f"**Descrição da Habilidade:**\n{row['descricao_habilidade']}")
        st.info(f"🌿 **Práxis Territorial (Presidente Figueiredo):**\n{row['praxis_territorio']}")

        if st.button(f"📝 Criar Plano com esta Habilidade", key=f"btn_{idx}"):
            st.session_state['selected_habilidade'] = row.to_dict()
            st.success("Habilidade selecionada para o plano de aula abaixo!")

# Seção de Planejamento de Aula
st.divider()
st.header("✏️ Gerador de Plano de Aula")

if 'selected_habilidade' in st.session_state:
    hab = st.session_state['selected_habilidade']
    st.write(f"**Habilidade Selecionada:** `{hab['codigo_bncc']}` - {hab['componente_curricular']} ({hab['etapa_ano']})")
    
    with st.form("plano_form"):
        turma = st.text_input("Turma", value="6º Ano A")
        data_aula = st.date_input("Data da Aula")
        metodologia = st.text_area("Metodologia & Atividades", value=f"Aula baseada na práxis: {hab['praxis_territorio']}")
        recursos = st.text_input("Recursos Didáticos", value="Quadro, cartazes, material impresso RCM")
        
        submitted = st.form_submit_on_button = st.form_submit_button("💾 Salvar & Exportar Plano")
        if submitted:
            plano_txt = f"""=== PLANO DE AULA (RCM 2026) ===
Turma: {turma} | Data: {data_aula}
Componente: {hab['componente_curricular']} | Ano: {hab['etapa_ano']} | Bimestre: {hab['bimestre']}º
BNCC: {hab['codigo_bncc']} | BNCC-CO: {hab['codigo_bncc_co']}
Dimensão RCM: {hab['dimensao_rcm']}
--------------------------------------------------
METODOLOGIA:
{metodologia}

RECURSOS DIDÁTICOS:
{recursos}
"""
            st.text_area("Plano Gerado (Pronto para copiar)", value=plano_txt, height=200)
            st.download_button("📥 Baixar Plano (.txt)", data=plano_txt, file_name=f"plano_{hab['codigo_bncc']}.txt")
else:
    st.info("Selecione uma habilidade acima para preencher o plano de aula.")
