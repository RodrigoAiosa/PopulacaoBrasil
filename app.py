"""
Painel Demográfico do Brasil — dados públicos do IBGE
Rode com: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go

from services import ibge_api as ibge

st.set_page_config(
    page_title="Painel Demográfico do Brasil",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design tokens & CSS global
# ---------------------------------------------------------------------------
CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">

<style>
:root{
    --bg: #EEF2ED;
    --surface: #FFFFFF;
    --ink: #12241F;
    --muted: #5B6B63;
    --primary: #1F6F5C;
    --primary-dark: #123A30;
    --gold: #C9962E;
    --brick: #B54B3A;
    --line: #D8E0D9;
}

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }
.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1180px; }

section[data-testid="stSidebar"] {
    background: var(--primary-dark);
}
section[data-testid="stSidebar"] * { color: #EAF2EE !important; }
section[data-testid="stSidebar"] .stSelectbox label { font-weight: 600; letter-spacing: .03em; text-transform: uppercase; font-size: 0.75rem; opacity: .85; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.25);
}

/* ---------- Hero ---------- */
.hero {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border-radius: 18px;
    padding: 2.6rem 2.8rem;
    color: #F4F8F5;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
    animation: fadeUp .6s ease-out;
}
.hero::after{
    content:"";
    position:absolute; right:-60px; top:-60px;
    width:260px; height:260px; border-radius:50%;
    background: radial-gradient(circle, rgba(201,150,46,0.35), transparent 70%);
}
.hero-eyebrow {
    font-size: 0.8rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--gold);
    font-weight: 600;
    margin-bottom: .6rem;
}
.hero-number {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: clamp(2.6rem, 6vw, 4.2rem);
    line-height: 1;
    margin: 0;
}
.hero-label {
    font-size: 1rem;
    color: #D8E9E1;
    margin-top: .5rem;
}
.hero-sub {
    margin-top: 1rem;
    max-width: 640px;
    color: #CFE3D9;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* ---------- Cards ---------- */
.card-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.8rem;
}
@media (max-width: 900px){ .card-grid { grid-template-columns: repeat(2, 1fr); } }

.card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    animation: fadeUp .6s ease-out;
}
.card-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: var(--muted);
    font-weight: 600;
}
.card-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--primary-dark);
    margin-top: .3rem;
}
.card-unit {
    font-size: 0.8rem;
    color: var(--muted);
    margin-left: .3rem;
    font-family: 'IBM Plex Sans', sans-serif;
}
.card-foot {
    font-size: 0.78rem;
    color: var(--gold);
    margin-top: .4rem;
    font-weight: 500;
}

/* ---------- Section headers ---------- */
.section-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--primary-dark);
    margin: 1.6rem 0 .8rem 0;
    border-left: 4px solid var(--gold);
    padding-left: .6rem;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers de formatação
# ---------------------------------------------------------------------------
def fmt_int(v):
    if v is None:
        return "—"
    return f"{int(round(v)):,}".replace(",", ".")


def fmt_dec(v, casas=1):
    if v is None:
        return "—"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def card(label, value, unit="", foot=""):
    st.markdown(
        f"""<div class="card">
                <div class="card-label">{label}</div>
                <div class="card-value">{value}<span class="card-unit">{unit}</span></div>
                <div class="card-foot">{foot}</div>
            </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar — filtros em cascata: Região > Estado > Município
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 🗺️ Filtros")
st.sidebar.caption("Região, Estado e Município (cidade) em cascata.")

TODAS_REGIOES = "Brasil — todas as regiões"
TODOS_ESTADOS = "Todos os estados da seleção"
TODOS_MUNICIPIOS = "Todos os municípios do estado"

regioes = ibge.get_regioes()
regiao_nome_sel = st.sidebar.selectbox(
    "Região", [TODAS_REGIOES] + [r["nome"] for r in regioes]
)
regiao_obj = next((r for r in regioes if r["nome"] == regiao_nome_sel), None)

estados = ibge.get_estados(regiao_obj["id"] if regiao_obj else None)
estado_labels = [f'{e["nome"]} ({e["sigla"]})' for e in estados]
estado_label_sel = st.sidebar.selectbox("Estado", [TODOS_ESTADOS] + estado_labels)
estado_obj = None
if estado_label_sel != TODOS_ESTADOS:
    idx = estado_labels.index(estado_label_sel)
    estado_obj = estados[idx]

if estado_obj:
    municipios = ibge.get_municipios(estado_obj["id"])
    municipio_nomes = [m["nome"] for m in municipios]
    municipio_nome_sel = st.sidebar.selectbox(
        "Cidade / Município", [TODOS_MUNICIPIOS] + municipio_nomes
    )
else:
    municipios = []
    st.sidebar.selectbox(
        "Cidade / Município", ["Selecione um estado primeiro"], disabled=True
    )
    municipio_nome_sel = TODOS_MUNICIPIOS

municipio_obj = None
if estado_obj and municipio_nome_sel != TODOS_MUNICIPIOS:
    municipio_obj = next(m for m in municipios if m["nome"] == municipio_nome_sel)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Fonte: [API de Localidades e Agregados do IBGE]"
    "(https://servicodados.ibge.gov.br/api/docs) — dados públicos e gratuitos."
)

# ---------------------------------------------------------------------------
# Determina o nível territorial selecionado
# ---------------------------------------------------------------------------
if municipio_obj:
    nivel, codigo = "N6", municipio_obj["id"]
    nome_local = municipio_obj["nome"]
    regiao_nome = estado_obj["regiao"]["nome"] if "regiao" in estado_obj else regiao_nome_sel
    breadcrumb = f"{regiao_nome} · {estado_obj['sigla']} · {nome_local}"
elif estado_obj:
    nivel, codigo = "N3", estado_obj["id"]
    nome_local = f'{estado_obj["nome"]} ({estado_obj["sigla"]})'
    regiao_nome = estado_obj["regiao"]["nome"] if "regiao" in estado_obj else regiao_nome_sel
    breadcrumb = f"{regiao_nome} · {estado_obj['nome']}"
elif regiao_obj:
    nivel, codigo = "N2", regiao_obj["id"]
    nome_local = regiao_obj["nome"]
    breadcrumb = f"Região {regiao_obj['nome']}"
else:
    nivel, codigo = "N1", 1
    nome_local = "Brasil"
    breadcrumb = "Visão nacional"

# ---------------------------------------------------------------------------
# Busca os indicadores
# ---------------------------------------------------------------------------
with st.spinner("Consultando a API do IBGE..."):
    populacao = ibge.get_valor_agregado(
        ibge.AGREGADO_POPULACAO_ESTIMADA, ibge.VARIAVEL_POPULACAO_ESTIMADA, nivel, codigo
    )

    area_info = ibge.find_variavel_id(ibge.AGREGADO_CENSO_AREA_DENSIDADE, "Área")
    densidade_info = ibge.find_variavel_id(ibge.AGREGADO_CENSO_AREA_DENSIDADE, "Densidade")

    area = ibge.get_valor_agregado(
        ibge.AGREGADO_CENSO_AREA_DENSIDADE, area_info[0], nivel, codigo
    ) if area_info else None
    densidade = ibge.get_valor_agregado(
        ibge.AGREGADO_CENSO_AREA_DENSIDADE, densidade_info[0], nivel, codigo
    ) if densidade_info else None

    # Nº de municípios / contexto administrativo + ranking de um nível abaixo
    if municipio_obj:
        peer_codigos = tuple(m["id"] for m in municipios)
        peer_nomes = tuple(m["nome"] for m in municipios)
        ranking = ibge.get_ranking_populacao("N6", peer_codigos, peer_nomes)
        posicao = next(
            (i + 1 for i, r in enumerate(ranking) if r["nome"] == municipio_obj["nome"]),
            None,
        )
        card4_label, card4_value, card4_unit, card4_foot = (
            "Posição no estado",
            f"{posicao}º" if posicao else "—",
            "",
            f"de {len(ranking)} municípios",
        )
        chart_title = f"Ranking de população — municípios de {estado_obj['sigla']}"
        highlight_nome = municipio_obj["nome"]
    elif estado_obj:
        peer_codigos = tuple(m["id"] for m in municipios)
        peer_nomes = tuple(m["nome"] for m in municipios)
        ranking = ibge.get_ranking_populacao("N6", peer_codigos, peer_nomes)
        card4_label, card4_value, card4_unit, card4_foot = (
            "Municípios",
            fmt_int(len(municipios)),
            "",
            "no estado",
        )
        chart_title = f"Top municípios de {estado_obj['nome']} por população"
        highlight_nome = None
    elif regiao_obj:
        peer_codigos = tuple(e["id"] for e in estados)
        peer_nomes = tuple(e["nome"] for e in estados)
        ranking = ibge.get_ranking_populacao("N3", peer_codigos, peer_nomes)
        total_municipios = sum(len(ibge.get_municipios(e["id"])) for e in estados)
        card4_label, card4_value, card4_unit, card4_foot = (
            "Municípios",
            fmt_int(total_municipios),
            "",
            f"em {len(estados)} estados",
        )
        chart_title = f"Estados da região {regiao_obj['nome']} por população"
        highlight_nome = None
    else:
        todos_estados = ibge.get_estados()
        peer_codigos = tuple(e["id"] for e in todos_estados)
        peer_nomes = tuple(e["nome"] for e in todos_estados)
        ranking = ibge.get_ranking_populacao("N3", peer_codigos, peer_nomes)
        card4_label, card4_value, card4_unit, card4_foot = (
            "Estados", "27", "", "+ Distrito Federal"
        )
        chart_title = "Estados do Brasil por população"
        highlight_nome = None

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">{breadcrumb}</div>
        <p class="hero-number">{fmt_int(populacao)}</p>
        <div class="hero-label">habitantes estimados em {nome_local}</div>
        <div class="hero-sub">
            Painel construído com as APIs públicas do IBGE (Localidades e Agregados/SIDRA).
            Use os filtros à esquerda para navegar por região, estado e município.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cards de indicadores
# ---------------------------------------------------------------------------
st.markdown('<div class="card-grid">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    card("População estimada", fmt_int(populacao), "hab.", "Estimativas IBGE")
with col2:
    card("Área territorial", fmt_dec(area, 0), "km²", "Censo 2022")
with col3:
    card("Densidade demográfica", fmt_dec(densidade, 1), "hab/km²", "Censo 2022")
with col4:
    card(card4_label, card4_value, card4_unit, card4_foot)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Gráfico de ranking
# ---------------------------------------------------------------------------
st.markdown(f'<div class="section-title">{chart_title}</div>', unsafe_allow_html=True)

top = ranking[:10] if ranking else []
if top:
    nomes_chart = [r["nome"] for r in reversed(top)]
    valores_chart = [r["populacao"] for r in reversed(top)]
    cores = [
        "#C9962E" if highlight_nome and n == highlight_nome else "#1F6F5C"
        for n in nomes_chart
    ]
    fig = go.Figure(
        go.Bar(
            x=valores_chart,
            y=nomes_chart,
            orientation="h",
            marker_color=cores,
            text=[fmt_int(v) for v in valores_chart],
            textposition="outside",
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color="#12241F"),
        xaxis=dict(showgrid=True, gridcolor="#D8E0D9", title="Habitantes"),
        yaxis=dict(title=""),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem dados de ranking disponíveis para esta seleção.")

# ---------------------------------------------------------------------------
# Mapa coroplético — população por estado
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Mapa: população por estado</div>', unsafe_allow_html=True)

with st.spinner("Carregando malha geográfica..."):
    geojson = ibge.get_malha_estados()
    todos_estados_mapa = ibge.get_estados()
    ranking_mapa = ibge.get_ranking_populacao(
        "N3",
        tuple(e["id"] for e in todos_estados_mapa),
        tuple(e["nome"] for e in todos_estados_mapa),
    )

# Descobre dinamicamente a chave de código no GeoJSON (ex.: "codarea")
props_amostra = geojson["features"][0]["properties"] if geojson.get("features") else {}
id_key = next(
    (k for k in props_amostra if "cod" in k.lower() or k.lower() in ("id", "sigla")),
    None,
)

if id_key and ranking_mapa:
    nome_para_id = {e["nome"]: str(e["id"]) for e in todos_estados_mapa}
    locations = [nome_para_id[r["nome"]] for r in ranking_mapa if r["nome"] in nome_para_id]
    valores_mapa = [r["populacao"] for r in ranking_mapa if r["nome"] in nome_para_id]

    fig_map = go.Figure(
        go.Choropleth(
            geojson=geojson,
            locations=locations,
            z=valores_mapa,
            featureidkey=f"properties.{id_key}",
            colorscale=[[0, "#EAF2EE"], [0.5, "#1F6F5C"], [1, "#123A30"]],
            marker_line_color="#FFFFFF",
            marker_line_width=0.6,
            colorbar_title="Habitantes",
        )
    )
    fig_map.update_geos(
        fitbounds="locations", visible=False, projection_type="mercator"
    )
    fig_map.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans"),
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Não foi possível montar o mapa (malha geográfica indisponível no momento).")

st.caption(
    "Dados: IBGE — API de Localidades, API de Agregados (SIDRA) e API de Malhas Geográficas. "
    "Estimativas de população: tabela 6579. Área e densidade: Censo Demográfico 2022 (tabela 4714)."
)
