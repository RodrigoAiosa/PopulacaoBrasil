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
    
    # Coordenadas aproximadas de algumas cidades principais
    _COORDENADAS_CIDADES: Dict[str, Tuple[float, float]] = {
        "São Paulo": [-23.5505, -46.6333],
        "Rio de Janeiro": [-22.9068, -43.1729],
        "Brasília": [-15.7975, -47.8919],
        "Salvador": [-12.9777, -38.5016],
        "Fortaleza": [-3.7172, -38.5434],
        "Belo Horizonte": [-19.9191, -43.9387],
        "Manaus": [-3.1190, -60.0217],
        "Curitiba": [-25.4290, -49.2671],
        "Recife": [-8.0476, -34.8770],
        "Porto Alegre": [-30.0346, -51.2177],
        "Belém": [-1.4558, -48.4902],
        "Goiânia": [-16.6869, -49.2648],
        "Guarulhos": [-23.4538, -46.5333],
        "Campinas": [-22.9056, -47.0608],
        "São Bernardo do Campo": [-23.6939, -46.5650],
        "Santo André": [-23.6636, -46.5383],
        "Osasco": [-23.5324, -46.7916],
        "São José dos Campos": [-23.1896, -45.8841],
        "Ribeirão Preto": [-21.1779, -47.8107],
        "Uberlândia": [-18.9128, -48.2755],
        "Londrina": [-23.3105, -51.1628],
        "Joinville": [-26.3045, -48.8487],
        "Niterói": [-22.8832, -43.1039],
        "São Luís": [-2.5307, -44.3028],
        "Maceió": [-9.6663, -35.7350],
        "Natal": [-5.7945, -35.2110],
        "Teresina": [-5.0919, -42.8034],
        "Campo Grande": [-20.4697, -54.6201],
        "Jaboatão dos Guararapes": [-8.1126, -35.0147],
        "Contagem": [-19.9322, -44.0536],
        "Feira de Santana": [-12.2561, -38.9593],
        "Cuiabá": [-15.5989, -56.0949],
        "Juiz de Fora": [-21.7595, -43.3398],
        "Aparecida de Goiânia": [-16.8218, -49.2445],
        "Ananindeua": [-1.3654, -48.3723],
        "Duque de Caxias": [-22.7858, -43.3047],
        "Nova Iguaçu": [-22.7556, -43.4605],
        "São José do Rio Preto": [-20.8196, -49.3797],
        "Sorocaba": [-23.5015, -47.4525],
        "Florianópolis": [-27.5949, -48.5482],
    }
    
    @classmethod
    def get_coordenadas_estado(cls, sigla: str) -> Optional[Tuple[float, float]]:
        """Retorna coordenadas de um estado pela sigla"""
        return cls._COORDENADAS_ESTADOS.get(sigla.upper())
    
    @classmethod
    def get_coordenadas_cidade(cls, nome: str) -> Optional[Tuple[float, float]]:
        """Retorna coordenadas de uma cidade pelo nome"""
        # Busca exata
        if nome in cls._COORDENADAS_CIDADES:
            return cls._COORDENADAS_CIDADES[nome]
        
        # Busca parcial (para cidades com nomes compostos)
        for cidade, coords in cls._COORDENADAS_CIDADES.items():
            if cidade in nome or nome in cidade:
                return coords
        
        return None
    
    @classmethod
    def preparar_dados_mapa(
        cls,
        ranking_data: List,
        estados_data: List,
        municipio_selecionado: Optional[str] = None,
        estado_selecionado: Optional[str] = None
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
    def criar_mapa_populacao(
        cls, 
        dados_mapa: List[DadosMapa],
        municipio_selecionado: Optional[str] = None,
        estado_selecionado: Optional[str] = None
    ) -> folium.Map:
        """
        Cria mapa com círculos proporcionais à população e destaque para município selecionado
        """
        if not dados_mapa:
            return None
        
        # Determinar centro do mapa
        center_lat = MAP_CENTER_LAT
        center_lon = MAP_CENTER_LON
        zoom_start = MAP_ZOOM_START
        
        # Se um município foi selecionado, centralizar o mapa nele
        if municipio_selecionado:
            coords = cls.get_coordenadas_cidade(municipio_selecionado)
            if coords:
                center_lat, center_lon = coords
                zoom_start = 10  # Zoom mais próximo para cidade
        
        # Criar mapa base
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles="CartoDB dark_matter"
        )
        
        # Calcular min/max para normalização
        pop_values = [d.populacao for d in dados_mapa]
        max_pop = max(pop_values) if pop_values else 1
        min_pop = min(pop_values) if pop_values else 0
        
        # Adicionar marcadores dos estados
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
        
        # Se um município foi selecionado, adicionar marcador de destaque
        if municipio_selecionado:
            coords = cls.get_coordenadas_cidade(municipio_selecionado)
            if coords:
                lat, lon = coords
                
                # Marcador personalizado para o município
                popup_text = f"""
                <div style="font-family: 'IBM Plex Sans', sans-serif; min-width: 180px;">
                    <b style="font-size: 18px; color: #C9962E;">📍 {municipio_selecionado}</b><br>
                    <span style="font-size: 14px; color: #1F6F5C;"><b>📍 Cidade selecionada</b></span>
                </div>
                """
                
                # Marcador com ícone personalizado
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"📍 {municipio_selecionado} (selecionado)",
                    icon=folium.Icon(
                        color="orange",
                        icon="star",
                        prefix="fa"
                    )
                ).add_to(m)
                
                # Adicionar um círculo de destaque ao redor da cidade
                folium.Circle(
                    location=[lat, lon],
                    radius=20000,  # 20km
                    color="#C9962E",
                    fill=True,
                    fill_color="#C9962E",
                    fill_opacity=0.15,
                    weight=3,
                    popup=f"📍 {municipio_selecionado}"
                ).add_to(m)
        
        # Se um estado foi selecionado (mas não município), destacar o estado
        elif estado_selecionado:
            # Encontrar o estado no mapa
            for dados in dados_mapa:
                if dados.nome == estado_selecionado:
                    # Adicionar um círculo de destaque ao redor do estado
                    folium.Circle(
                        location=[dados.lat, dados.lon],
                        radius=150000,  # 150km
                        color="#C9962E",
                        fill=True,
                        fill_color="#C9962E",
                        fill_opacity=0.08,
                        weight=2,
                        popup=f"📍 {estado_selecionado} (selecionado)"
                    ).add_to(m)
                    break
        
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
