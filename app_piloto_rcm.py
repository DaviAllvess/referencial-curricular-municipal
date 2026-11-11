import json
from pathlib import Path

import pandas as pd
import streamlit as st


# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="RCM Presidente Figueiredo - 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# 2. CARREGAMENTO DO JSON
# ==========================================

NOME_JSON = "matriz_curricular_rcm_2026.json"


@st.cache_data
def load_data():
    pasta_app = Path(__file__).resolve().parent

    caminhos = [
        pasta_app / NOME_JSON,
        Path.cwd() / NOME_JSON,
    ]

    json_path = next((caminho for caminho in caminhos if caminho.is_file()), None)

    if json_path is None:
        raise FileNotFoundError(
            f"Não encontrei {NOME_JSON}. "
            "Coloque esse arquivo na mesma pasta de app_piloto_rcm.py."
        )

    with json_path.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if isinstance(dados, dict):
        dados = dados.get("habilidades", [])

    if not isinstance(dados, list):
        raise ValueError("O JSON precisa conter uma lista de habilidades.")

    return dados


try:
    dados = load_data()
    df = pd.DataFrame(dados)

    if df.empty:
        st.error("O arquivo JSON está vazio ou não possui habilidades.")
        st.stop()

except Exception as erro:
    st.error(f"Erro ao carregar o arquivo JSON: {erro}")
    st.stop()


# ==========================================
# 3. VERIFICAÇÃO DOS CAMPOS
# ==========================================

campos_obrigatorios = [
    "id_habilidade",
    "componente_curricular",
    "etapa_ano",
    "bimestre",
]

campos_faltantes = [campo for campo in campos_obrigatorios if campo not in df.columns]

if campos_faltantes:
    st.error(
        "Existem campos obrigatórios ausentes no JSON: "
        + ", ".join(campos_faltantes)
    )
    st.write("Campos encontrados no arquivo:")
    st.write(list(df.columns))
    st.stop()


# ==========================================
# 4. FUNÇÕES AUXILIARES
# ==========================================

def obter_texto(valor, padrao="Não informado"):
    """Converte valores do JSON/DataFrame em texto de forma segura."""
    if valor is None:
        return padrao

    if isinstance(valor, (list, tuple)):
        if not valor:
            return padrao
        return ", ".join(str(item) for item in valor)

    try:
        if pd.isna(valor):
            return padrao
    except (TypeError, ValueError):
        pass

    texto = str(valor).strip()
    return texto if texto else padrao


def obter_opcoes(coluna, opcao_todos):
    valores = (
        df[coluna]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    return [opcao_todos] + sorted(valores)


# ==========================================
# 5. CABEÇALHO
# ==========================================

st.title("📚 RCM 2026 - Consulta & Planejamento Curricular")
st.caption("Referencial Curricular Municipal de Presidente Figueiredo")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de habilidades", len(df))

with col2:
    st.metric("Componentes curriculares", df["componente_curricular"].nunique())

with col3:
    st.metric("Etapas e anos", df["etapa_ano"].nunique())


# ==========================================
# 6. FILTROS
# ==========================================

st.sidebar.header("🔍 Filtros de Busca")

componentes = obter_opcoes("componente_curricular", "Todos")
comp_sel = st.sidebar.selectbox("Componente Curricular", componentes)

anos = obter_opcoes("etapa_ano", "Todos")
ano_sel = st.sidebar.selectbox("Etapa / Ano", anos)

bimestres = obter_opcoes("bimestre", "Todos")
bim_sel = st.sidebar.selectbox("Bimestre", bimestres)

if "dimensao_rcm" in df.columns:
    dimensoes = obter_opcoes("dimensao_rcm", "Todas")
    dim_sel = st.sidebar.selectbox("Dimensão do RCM", dimensoes)
else:
    dim_sel = "Todas"


# ==========================================
# 7. APLICAÇÃO DOS FILTROS
# ==========================================

df_filtrado = df.copy()

if comp_sel != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["componente_curricular"].astype(str) == comp_sel
    ]

if ano_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["etapa_ano"].astype(str) == ano_sel]

if bim_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["bimestre"].astype(str) == bim_sel]

if dim_sel != "Todas" and "dimensao_rcm" in df.columns:
    df_filtrado = df_filtrado[df_filtrado["dimensao_rcm"].astype(str) == dim_sel]


# ==========================================
# 8. LISTAGEM DAS HABILIDADES
# ==========================================

st.divider()
st.subheader(f"📋 Habilidades Encontradas: {len(df_filtrado)}")

if df_filtrado.empty:
    st.warning("Nenhuma habilidade encontrada. Experimente alterar os filtros.")

for idx, row in df_filtrado.iterrows():
    # Usar os valores já tratados evita acessar uma coluna inexistente
    # como row["codigo_bncc"].
    codigo = obter_texto(row.get("id_habilidade"))
    componente = obter_texto(row.get("componente_curricular"))
    etapa = obter_texto(row.get("etapa_ano"))
    bimestre = obter_texto(row.get("bimestre"))

    with st.expander(
        f"📌 [{codigo}] {componente} - {etapa} ({bimestre}º Bimestre)",
        expanded=False,
    ):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Identificador da habilidade:** `{codigo}`")
            st.markdown(
                "**BNCC Computação:** "
                f"`{obter_texto(row.get('codigo_bncc_co'))}`"
            )
            st.markdown(
                "**Dimensão RCM:** "
                f"{obter_texto(row.get('dimensao_rcm'))}"
            )

        with col2:
            st.markdown(
                "**Inteligências Múltiplas:** "
                f"{obter_texto(row.get('inteligencias_multiplas'))}"
            )
            st.markdown(
                "**Eixo Computação:** "
                f"{obter_texto(row.get('eixo_computacao'))}"
            )

        st.markdown("### 📖 Descrição da Habilidade")
        st.write(obter_texto(row.get("descricao_habilidade")))

        st.info(
            "🌿 **Práxis Territorial - Presidente Figueiredo**\n\n"
            + obter_texto(row.get("praxis_territorio"))
        )

        if st.button(
            "📝 Criar Plano com esta Habilidade",
            key=f"btn_{idx}",
        ):
            st.session_state["selected_habilidade"] = row.to_dict()
            st.rerun()


# ==========================================
# 9. GERADOR DE PLANO DE AULA
# ==========================================

st.divider()
st.header("✏️ Gerador de Plano de Aula")

if "selected_habilidade" in st.session_state:
    hab = st.session_state["selected_habilidade"]

    codigo = obter_texto(hab.get("id_habilidade"))

    st.success(f"Habilidade selecionada: {codigo}")

    with st.form("plano_form"):
        turma = st.text_input("Turma", value="6º Ano A")
        data_aula = st.date_input("Data da Aula")

        metodologia = st.text_area(
            "Metodologia e Atividades",
            value=(
                "Aula baseada na práxis territorial: "
                + obter_texto(hab.get("praxis_territorio"))
            ),
        )

        recursos = st.text_input(
            "Recursos Didáticos",
            value="Quadro, cartazes e material impresso RCM",
        )

        objetivo = st.text_area(
            "Objetivo da Aula",
            value=obter_texto(hab.get("descricao_habilidade")),
        )

        submitted = st.form_submit_button("💾 Gerar Plano de Aula")

    if submitted:
        plano_txt = f"""
========================================
PLANO DE AULA - RCM 2026
PRESIDENTE FIGUEIREDO
========================================

IDENTIFICAÇÃO

Turma: {turma}
Data: {data_aula}

Componente Curricular:
{obter_texto(hab.get('componente_curricular'))}

Etapa/Ano:
{obter_texto(hab.get('etapa_ano'))}

Bimestre:
{obter_texto(hab.get('bimestre'))}

HABILIDADES

Identificador da habilidade: {codigo}

BNCC Computação:
{obter_texto(hab.get('codigo_bncc_co'))}

Descrição da Habilidade:
{obter_texto(hab.get('descricao_habilidade'))}

Dimensão RCM:
{obter_texto(hab.get('dimensao_rcm'))}

Eixo Computação:
{obter_texto(hab.get('eixo_computacao'))}

Inteligências Múltiplas:
{obter_texto(hab.get('inteligencias_multiplas'))}

OBJETIVO DA AULA

{objetivo}

METODOLOGIA E ATIVIDADES

{metodologia}

PRÁXIS TERRITORIAL

{obter_texto(hab.get('praxis_territorio'))}

RECURSOS DIDÁTICOS

{recursos}

========================================
FIM DO PLANO DE AULA
========================================
"""

        st.subheader("📄 Plano de Aula Gerado")
        st.text_area(
            "Seu plano está pronto para copiar:",
            value=plano_txt,
            height=400,
        )

        st.download_button(
            label="📥 Baixar Plano de Aula",
            data=plano_txt,
            file_name=f"plano_{codigo}.txt",
            mime="text/plain",
        )

else:
    st.info(
        "Selecione uma habilidade na lista acima "
        "para começar a criar seu plano de aula."
    )


# ==========================================
# 10. RODAPÉ
# ==========================================

st.divider()
st.caption(
    "📚 RCM 2026 | Referencial Curricular Municipal "
    "de Presidente Figueiredo - Amazonas"
)
