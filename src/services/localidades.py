"""
Serviços para consulta de localidades (Regiões, Estados, Municípios)
"""
import logging
from typing import List, Optional
import streamlit as st

from src.api.endpoints import APIEndpoints
from src.api.http_client import get_json
from src.models.schemas import Regiao, Estado, Municipio
from src.config.settings import CACHE_TTL_LOCALIDADES

logger = logging.getLogger("populacao_brasil")


@st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
def _fetch_regioes() -> Optional[List[dict]]:
    """Função cacheada para buscar regiões"""
    return get_json(APIEndpoints.get_regioes_url())


@st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
def _fetch_estados(regiao_id: Optional[int] = None) -> Optional[List[dict]]:
    """Função cacheada para buscar estados"""
    return get_json(APIEndpoints.get_estados_url(regiao_id))


@st.cache_data(ttl=CACHE_TTL_LOCALIDADES, show_spinner=False)
def _fetch_municipios(uf_id: int) -> Optional[List[dict]]:
    """Função cacheada para buscar municípios"""
    return get_json(APIEndpoints.get_municipios_url(uf_id))


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
    def get_regioes() -> List[Regiao]:
        """Lista todas as regiões do Brasil com fallback"""
        try:
            data = _fetch_regioes()
            if data:
                return sorted(
                    [Regiao.from_api(item) for item in data],
                    key=lambda r: r.nome
                )
        except Exception as e:
            logger.warning("Falha ao buscar regiões da API do IBGE: %s", e)
            st.warning("⚠️ Usando dados de fallback para regiões (API do IBGE indisponível no momento).")
        
        # Fallback
        return sorted(
            [Regiao.from_api(item) for item in LocalidadesService._FALLBACK_REGIOES],
            key=lambda r: r.nome
        )
    
    @staticmethod
    def get_estados(regiao_id: Optional[int] = None) -> List[Estado]:
        """Lista estados, opcionalmente filtrados por região, com fallback"""
        try:
            data = _fetch_estados(regiao_id)
            if data:
                estados = [Estado.from_api(item) for item in data]
                return sorted(estados, key=lambda e: e.nome)
        except Exception as e:
            logger.warning("Falha ao buscar estados da API do IBGE: %s", e)
            st.warning("⚠️ Usando dados de fallback para estados (API do IBGE indisponível no momento).")
        
        # Fallback
        estados = [Estado.from_api(item) for item in LocalidadesService._FALLBACK_ESTADOS]
        if regiao_id:
            estados = [e for e in estados if e.regiao and e.regiao.id == regiao_id]
        return sorted(estados, key=lambda e: e.nome)
    
    @staticmethod
    def get_municipios(uf_id: int) -> List[Municipio]:
        """Lista municípios de um estado com fallback"""
        try:
            data = _fetch_municipios(uf_id)
            if data:
                return sorted(
                    [Municipio.from_api(item) for item in data],
                    key=lambda m: m.nome
                )
        except Exception as e:
            logger.warning("Falha ao buscar municípios (uf_id=%s) da API do IBGE: %s", uf_id, e)
            st.warning("⚠️ Não foi possível carregar municípios (API do IBGE indisponível no momento).")
        
        # Fallback: retorna algumas capitais conhecidas, com os códigos IBGE
        # REAIS de 7 dígitos (os códigos fictícios 1-10 usados antes quebravam
        # qualquer busca posterior por `get_municipio_by_id` ou consulta ao
        # SIDRA, já que esses IDs não existem de fato na base do IBGE).
        fallback_municipios = [
            {"id": 5300108, "nome": "Brasília"},
            {"id": 3550308, "nome": "São Paulo"},
            {"id": 3304557, "nome": "Rio de Janeiro"},
            {"id": 2927408, "nome": "Salvador"},
            {"id": 2304400, "nome": "Fortaleza"},
            {"id": 3106200, "nome": "Belo Horizonte"},
            {"id": 4106902, "nome": "Curitiba"},
            {"id": 4314902, "nome": "Porto Alegre"},
            {"id": 2611606, "nome": "Recife"},
            {"id": 1302603, "nome": "Manaus"},
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
