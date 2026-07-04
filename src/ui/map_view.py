"""
Componente de mapa
"""
import streamlit as st
from typing import List, Optional
from streamlit_folium import st_folium

from src.services.mapas import mapas_service
from src.models.schemas import DadosMapa, RankingItem
from src.utils.formatters import fmt_int
from src.config.settings import MAP_HEIGHT


def render_population_map(
    dados_mapa: List[DadosMapa],
    ranking_data: List[RankingItem],
    titulo: str = "🗺️ Mapa: população por estado"
):
    """
    Renderiza mapa de população por estado
    """
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)
    
    if not dados_mapa:
        st.info("Não foi possível carregar os dados para o mapa.")
        return
    
    # Criar mapa
    mapa = mapas_service.criar_mapa_populacao(dados_mapa)
    
    if mapa:
        # Container estilizado
        st.markdown('<div class="folium-map-container">', unsafe_allow_html=True)
        st_folium(mapa, use_container_width=True, height=MAP_HEIGHT, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Legenda
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Total de estados", len(dados_mapa))
        with col2:
            if dados_mapa:
                max_item = max(dados_mapa, key=lambda x: x.populacao)
                min_item = min(dados_mapa, key=lambda x: x.populacao)
                st.caption(
                    f"🗺️ **População por estado** — círculos proporcionais à população. "
                    f"Maior: {max_item.nome} ({fmt_int(max_item.populacao)} hab.) | "
                    f"Menor: {min_item.nome} ({fmt_int(min_item.populacao)} hab.)"
                )
    else:
        st.warning("Não foi possível gerar o mapa.")


def render_location_map(
    dados: List[dict],
    lat_key: str = "lat",
    lon_key: str = "lon",
    popup_template: Optional[str] = None,
    titulo: str = "🗺️ Mapa"
):
    """
    Renderiza mapa com marcadores em cluster
    """
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)
    
    if not dados:
        st.info("Sem dados para exibir no mapa.")
        return
    
    mapa = mapas_service.criar_mapa_clusters(
        dados,
        lat_key=lat_key,
        lon_key=lon_key,
        popup_template=popup_template
    )
    
    if mapa:
        st.markdown('<div class="folium-map-container">', unsafe_allow_html=True)
        st_folium(mapa, use_container_width=True, height=MAP_HEIGHT, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Não foi possível gerar o mapa.")
