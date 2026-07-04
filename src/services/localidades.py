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
    
    # Dados de fallback (caso a API esteja indisponível)
    _FALLBACK_REGIOES = [
        {"id": 1, "nome": "Norte", "sigla": "N"},
        {"id": 2, "nome": "Nordeste", "sigla": "NE"},
        {"id": 3, "nome": "Sudeste", "sigla": "SE"},
        {"id": 4, "nome": "Sul", "sigla": "S"},
        {"id": 5, "nome": "Centro-Oeste", "sigla": "CO"},
    ]
    
    _FALLBACK_ESTADOS = [
        {"id": 11, "nome": "Rondônia", "sigla": "RO", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 12, "nome": "Acre", "sigla": "AC", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 13, "nome": "Amazonas", "sigla": "AM", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 14, "nome": "Roraima", "sigla": "RR", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 15, "nome": "Pará", "sigla": "PA", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 16, "nome": "Amapá", "sigla": "AP", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 17, "nome": "Tocantins", "sigla": "TO", "regiao": {"id": 1, "nome": "Norte", "sigla": "N"}},
        {"id": 21, "nome": "Maranhão", "sigla": "MA", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 22, "nome": "Piauí", "sigla": "PI", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 23, "nome": "Ceará", "sigla": "CE", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 24, "nome": "Rio Grande do Norte", "sigla": "RN", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 25, "nome": "Paraíba", "sigla": "PB", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 26, "nome": "Pernambuco", "sigla": "PE", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 27, "nome": "Alagoas", "sigla": "AL", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 28, "nome": "Sergipe", "sigla": "SE", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 29, "nome": "Bahia", "sigla": "BA", "regiao": {"id": 2, "nome": "Nordeste", "sigla": "NE"}},
        {"id": 31, "nome": "Minas Gerais", "sigla": "MG", "regiao": {"id": 3, "nome": "Sudeste", "sigla": "SE"}},
        {"id": 32, "nome": "Espírito Santo", "sigla": "ES", "regiao": {"id": 3, "nome": "Sudeste", "sigla": "SE"}},
        {"id": 33, "nome": "Rio de Janeiro", "sigla": "RJ", "regiao": {"id": 3, "nome": "Sudeste", "sigla": "SE"}},
        {"id": 35, "nome": "São Paulo", "sigla": "SP", "regiao": {"id": 3, "nome": "Sudeste", "sigla": "SE"}},
        {"id": 41, "nome": "Paraná", "sigla": "PR", "regiao": {"id": 4, "nome": "Sul", "sigla": "S"}},
        {"id": 42, "nome": "Santa Catarina", "sigla": "SC", "regiao": {"id": 4, "nome": "Sul", "sigla": "S"}},
        {"id": 43, "nome": "Rio Grande do Sul", "sigla": "RS", "regiao": {"id": 4, "nome": "Sul", "sigla": "S"}},
        {"id": 50, "nome": "Mato Grosso do Sul", "sigla": "MS", "regiao": {"id": 5, "nome": "Centro-Oeste", "sigla": "CO"}},
        {"id": 51, "nome": "Mato Grosso", "sigla": "MT", "regiao": {"id": 5, "nome": "Centro-Oeste", "sigla": "CO"}},
        {"id": 52, "nome": "Goiás", "sigla": "GO", "regiao": {"id": 5, "nome": "Centro-Oeste", "sigla": "CO"}},
        {"id": 53, "nome": "Distrito Federal", "sigla": "DF", "regiao": {"id": 5, "nome": "Centro-Oeste", "sigla": "CO"}},
    ]
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
    def get_regioes() -> List[Regiao]:
        """Lista todas as regiões do Brasil com fallback"""
        try:
            data = ibge_client.get_json_cached(APIEndpoints.get_regioes_url())
            if data:
                return sorted(
                    [Regiao.from_api(item) for item in data],
                    key=lambda r: r.nome
                )
        except Exception as e:
            st.warning(f"⚠️ Usando dados de fallback para regiões. Erro: {str(e)}")
        
        # Fallback
        return sorted(
            [Regiao.from_api(item) for item in LocalidadesService._FALLBACK_REGIOES],
            key=lambda r: r.nome
        )
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
    def get_estados(regiao_id: Optional[int] = None) -> List[Estado]:
        """Lista estados, opcionalmente filtrados por região, com fallback"""
        try:
            url = APIEndpoints.get_estados_url(regiao_id)
            data = ibge_client.get_json_cached(url)
            if data:
                estados = [Estado.from_api(item) for item in data]
                return sorted(estados, key=lambda e: e.nome)
        except Exception as e:
            st.warning(f"⚠️ Usando dados de fallback para estados. Erro: {str(e)}")
        
        # Fallback
        estados = [Estado.from_api(item) for item in LocalidadesService._FALLBACK_ESTADOS]
        if regiao_id:
            estados = [e for e in estados if e.regiao and e.regiao.id == regiao_id]
        return sorted(estados, key=lambda e: e.nome)
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
    def get_municipios(uf_id: int) -> List[Municipio]:
        """Lista municípios de um estado com fallback"""
        try:
            url = APIEndpoints.get_municipios_url(uf_id)
            data = ibge_client.get_json_cached(url)
            if data:
                return sorted(
                    [Municipio.from_api(item) for item in data],
                    key=lambda m: m.nome
                )
        except Exception as e:
            st.warning(f"⚠️ Não foi possível carregar municípios. Erro: {str(e)}")
        
        # Fallback: retorna alguns municípios conhecidos
        fallback_municipios = [
            {"id": 1, "nome": "Brasília"},
            {"id": 2, "nome": "São Paulo"},
            {"id": 3, "nome": "Rio de Janeiro"},
            {"id": 4, "nome": "Salvador"},
            {"id": 5, "nome": "Fortaleza"},
            {"id": 6, "nome": "Belo Horizonte"},
        ]
        return sorted(
            [Municipio.from_api(item) for item in fallback_municipios],
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
