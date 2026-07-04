"""
Serviços para operações com mapas
"""
from typing import Dict, List, Tuple, Optional
import streamlit as st
import folium
from folium.plugins import MarkerCluster

from src.models.schemas import DadosMapa
from src.config.settings import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_ZOOM_START


class MapasService:
    """Serviço para criação e manipulação de mapas"""
    
    # Coordenadas aproximadas dos estados brasileiros
    _COORDENADAS_ESTADOS: Dict[str, Tuple[float, float]] = {
        "AC": [-9.0238, -70.8120],
        "AL": [-9.5710, -36.7820],
        "AM": [-3.4653, -62.2159],
        "AP": [0.9019, -51.9577],
        "BA": [-12.5797, -41.7007],
        "CE": [-5.4984, -39.3206],
        "DF": [-15.7998, -47.8645],
        "ES": [-19.1834, -40.3089],
        "GO": [-15.8270, -49.8362],
        "MA": [-4.9609, -45.2744],
        "MG": [-18.5122, -44.5550],
        "MS": [-20.7722, -54.7851],
        "MT": [-12.6819, -56.9211],
        "PA": [-3.4168, -52.3506],
        "PB": [-7.2760, -36.0294],
        "PE": [-8.0586, -38.3175],
        "PI": [-6.2470, -42.3551],
        "PR": [-24.9568, -51.6461],
        "RJ": [-22.2259, -42.7069],
        "RN": [-5.4026, -36.9541],
        "RO": [-11.5057, -63.5806],
        "RR": [1.8849, -61.2209],
        "RS": [-29.6954, -53.8725],
        "SC": [-27.2437, -50.2640],
        "SE": [-10.5431, -37.4310],
        "SP": [-23.5505, -46.6333],
        "TO": [-9.7088, -48.4615],
    }
    
    @classmethod
    def get_coordenadas_estado(cls, sigla: str) -> Optional[Tuple[float, float]]:
        """Retorna coordenadas de um estado pela sigla"""
        return cls._COORDENADAS_ESTADOS.get(sigla.upper())
    
    @classmethod
    def preparar_dados_mapa(
        cls,
        ranking_data: List,
        estados_data: List
    ) -> List[DadosMapa]:
        """
        Prepara dados para exibição no mapa
        """
        # Mapeamento nome -> sigla
        siglas = {e["nome"]: e["sigla"] for e in estados_data}
        
        dados_mapa = []
        for item in ranking_data:
            sigla = siglas.get(item.nome)
            if sigla and sigla in cls._COORDENADAS_ESTADOS:
                lat, lon = cls._COORDENADAS_ESTADOS[sigla]
                dados_mapa.append(
                    DadosMapa(
                        sigla=sigla,
                        nome=item.nome,
                        populacao=item.populacao,
                        lat=lat,
                        lon=lon
                    )
                )
        
        return dados_mapa
    
    @classmethod
    def criar_mapa_populacao(cls, dados_mapa: List[DadosMapa]) -> folium.Map:
        """
        Cria mapa com círculos proporcionais à população
        """
        if not dados_mapa:
            return None
        
        # Criar mapa base
        m = folium.Map(
            location=[MAP_CENTER_LAT, MAP_CENTER_LON],
            zoom_start=MAP_ZOOM_START,
            tiles="CartoDB dark_matter"
        )
        
        # Calcular min/max para normalização
        pop_values = [d.populacao for d in dados_mapa]
        max_pop = max(pop_values)
        min_pop = min(pop_values)
        
        # Adicionar marcadores
        for dados in dados_mapa:
            # Tamanho proporcional (8 a 45)
            if max_pop > min_pop:
                normalized = (dados.populacao - min_pop) / (max_pop - min_pop)
                radius = 8 + (normalized * 37)
            else:
                radius = 20
            
            # Popup
            popup_text = f"""
            <div style="font-family: 'IBM Plex Sans', sans-serif; min-width: 150px;">
                <b style="font-size: 16px; color: #1F6F5C;">{dados.nome}</b><br>
                <span style="font-size: 14px;">👥 População: <b>{dados.populacao_formatada}</b></span>
            </div>
            """
            
            # Círculo
            folium.CircleMarker(
                location=[dados.lat, dados.lon],
                radius=radius,
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"{dados.nome}: {dados.populacao_formatada} habitantes",
                color="#1F6F5C",
                fill=True,
                fill_color="#1F6F5C",
                fill_opacity=0.6,
                weight=2,
            ).add_to(m)
            
            # Rótulo com sigla
            folium.Marker(
                location=[dados.lat - (radius * 0.04), dados.lon],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10px; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;">{dados.sigla}</div>'
                )
            ).add_to(m)
        
        return m
    
    @classmethod
    def criar_mapa_clusters(
        cls,
        dados: List[Dict],
        lat_key: str = "lat",
        lon_key: str = "lon",
        popup_template: str = None
    ) -> folium.Map:
        """
        Cria mapa com clusters de marcadores
        """
        if not dados:
            return None
        
        m = folium.Map(
            location=[MAP_CENTER_LAT, MAP_CENTER_LON],
            zoom_start=MAP_ZOOM_START,
            tiles="CartoDB dark_matter"
        )
        
        cluster = MarkerCluster().add_to(m)
        
        for item in dados:
            if lat_key in item and lon_key in item:
                popup = folium.Popup(
                    popup_template.format(**item) if popup_template else str(item),
                    max_width=200
                )
                
                folium.Marker(
                    location=[item[lat_key], item[lon_key]],
                    popup=popup,
                    tooltip=item.get("tooltip", item.get("nome", "")),
                ).add_to(cluster)
        
        return m


# Instância global do serviço
mapas_service = MapasService()
