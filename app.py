"""
Painel Demográfico do Brasil — dados públicos do IBGE
Rode com: streamlit run app.py
"""
import streamlit as st

# Configuração da página (deve ser a primeira chamada)
st.set_page_config(
    page_title="Painel Demográfico do Brasil",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importações dos módulos
from src.ui.css import get_css
from src.ui.sidebar import sidebar_filters
from src.ui.hero import render_hero_section
from src.ui.cards import render_indicators_cards
from src.ui.charts import render_ranking_chart
from src.ui.map_view import render_population_map

from src.services.localidades import localidades_service
from src.services.agregados import agregados_service
from src.services.mapas import mapas_service
from src.models.schemas import IndicadorDemografico
from src.utils.formatters import fmt_int
from src.utils.constants import UI_TEXTS
from src.api.endpoints import NiveisTerritoriais
from src.api.ibge_client import ibge_client


def main():
    """Função principal do aplicativo"""
    
    # Injetar CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Verificar conexão com a API
    with st.spinner("🔄 Verificando conexão com a API do IBGE..."):
        connection_ok = ibge_client.test_connection()
    
    if not connection_ok:
        st.warning(
            "⚠️ **Modo Offline**\n\n"
            "Não foi possível conectar à API do IBGE. "
            "O aplicativo usará dados de fallback (limitados). "
            "Verifique sua conexão com a internet e recarregue a página."
        )
    
    # Renderizar sidebar e obter seleções
    selecoes = sidebar_filters.render()
    
    nivel = selecoes["nivel"]
    codigo = selecoes["codigo"]
    modo_offline = selecoes.get("modo_offline", False)
    
    # Buscar indicadores
    with st.spinner("📊 Carregando dados demográficos..."):
        indicadores = agregados_service.get_indicadores_demograficos(nivel, codigo)
    
    # Determinar contexto para o quarto card e ranking
    if selecoes["municipio"]:
        # Nível município
        estados = localidades_service.get_estados()
        estado_obj = next(
            (e for e in estados if e.id == selecoes["estado"].id), 
            None
        )
        if estado_obj:
            municipios = localidades_service.get_municipios(estado_obj.id)
            peer_codigos = [m.id for m in municipios]
            peer_nomes = [m.nome for m in municipios]
            ranking = agregados_service.get_ranking_populacao(
                NiveisTerritoriais.MUNICIPIO,
                peer_codigos,
                peer_nomes
            )
            posicao = next(
                (i + 1 for i, r in enumerate(ranking) if r.nome == selecoes["municipio"].nome),
                None
            )
            card4_label = "Posição no estado"
            card4_value = f"{posicao}º" if posicao else "—"
            card4_unit = ""
            card4_foot = f"de {len(ranking)} municípios"
            chart_title = f"Ranking de população — municípios de {selecoes['estado'].sigla}"
            highlight_nome = selecoes["municipio"].nome
    
    elif selecoes["estado"]:
        # Nível estado
        municipios = localidades_service.get_municipios(selecoes["estado"].id)
        peer_codigos = [m.id for m in municipios]
        peer_nomes = [m.nome for m in municipios]
        ranking = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.MUNICIPIO,
            peer_codigos,
            peer_nomes
        )
        card4_label = "Municípios"
        card4_value = fmt_int(len(municipios))
        card4_unit = ""
        card4_foot = "no estado"
        chart_title = f"Top municípios de {selecoes['estado'].nome} por população"
        highlight_nome = None
    
    elif selecoes["regiao"]:
        # Nível região
        estados = localidades_service.get_estados(selecoes["regiao"].id)
        peer_codigos = [e.id for e in estados]
        peer_nomes = [e.nome for e in estados]
        ranking = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.ESTADO,
            peer_codigos,
            peer_nomes
        )
        total_municipios = sum(
            len(localidades_service.get_municipios(e.id)) for e in estados
        )
        card
