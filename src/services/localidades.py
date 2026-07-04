"""
Serviços para consulta de localidades (Regiões, Estados, Municípios)
"""
from typing import List, Optional
import streamlit as st

from src.api.ibge_client import ibge_client
from src.api.endpoints import APIEndpoints
from src.models.schemas import Regiao, Estado, Municipio
from src.config.settings import CACHE_TTL_LOCALIDADES


class LocalidadesService:
    """Serviço para operações com localidades"""
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
    def get_regioes() -> List[Regiao]:
        """Lista todas as regiões do Brasil"""
        data = ibge_client.get_json_cached(APIEndpoints.get_regioes_url())
        return sorted(
            [Regiao.from_api(item) for item in data],
            key=lambda r: r.nome
        )
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
    def get_estados(regiao_id: Optional[int] = None) -> List[Estado]:
        """Lista estados, opcionalmente filtrados por região"""
        url = APIEndpoints.get_estados_url(regiao_id)
        data = ibge_client.get_json_cached(url)
        return sorted(
            [Estado.from_api(item) for item in data],
            key=lambda e: e.nome
        )
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
    def get_municipios(uf_id: int) -> List[Municipio]:
        """Lista municípios de um estado"""
        url = APIEndpoints.get_municipios_url(uf_id)
        data = ibge_client.get_json_cached(url)
        return sorted(
            [Municipio.from_api(item) for item in data],
            key=lambda m: m.nome
        )
    
    @staticmethod
    def get_estado_by_id(estado_id: int) -> Optional[Estado]:
        """Busca um estado específico pelo ID"""
        estados = LocalidadesService.get_estados()
        return next((e for e in estados if e.id == estado_id), None)
    
    @staticmethod
    def get_municipio_by_id(uf_id: int, municipio_id: int) -> Optional[Municipio]:
        """Busca um município específico pelo ID"""
        municipios = LocalidadesService.get_municipios(uf_id)
        return next((m for m in municipios if m.id == municipio_id), None)


# Instância global do serviço
localidades_service = LocalidadesService()
