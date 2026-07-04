"""
Serviços para consulta de agregados do SIDRA
"""
from typing import List, Tuple, Optional, Dict, Any
import streamlit as st

from src.api.ibge_client import ibge_client
from src.api.endpoints import APIEndpoints, Agregados, Variaveis, NiveisTerritoriais
from src.models.schemas import IndicadorDemografico, RankingItem
from src.config.settings import CACHE_TTL_AGREGADOS


class AgregadosService:
    """Serviço para operações com agregados do SIDRA"""
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_AGREGADOS, show_spinner=False)
    def get_metadados_agregado(agregado_id: int) -> Dict[str, Any]:
        """Obtém metadados de um agregado"""
        url = APIEndpoints.get_agregado_metadados_url(agregado_id)
        return ibge_client.get_json_cached(url)
    
    @staticmethod
    def find_variavel_id(agregado_id: int, palavra_chave: str) -> Optional[Tuple[int, str, str]]:
        """
        Busca ID de uma variável por palavra-chave no nome
        Retorna (id, nome, unidade) ou None
        """
        meta = AgregadosService.get_metadados_agregado(agregado_id)
        palavra_chave = palavra_chave.lower()
        
        for var in meta.get("variaveis", []):
            if palavra_chave in var["nome"].lower():
                return var["id"], var["nome"], var.get("unidade", "")
        return None
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_AGREGADOS, show_spinner=False)
    def get_valor_agregado(
        agregado_id: int,
        variavel_id: int,
        nivel: str,
        codigo: int,
        periodo: str = "-1"
    ) -> Optional[float]:
        """
        Consulta valor mais recente de uma variável para uma localidade
        """
        url = APIEndpoints.get_agregado_valor_url(agregado_id, variavel_id, periodo)
        localidade = f"{nivel}[{codigo}]"
        
        try:
            data = ibge_client.get_json_cached(url, params={"localidades": localidade})
        except Exception:
            return None
        
        try:
            series = data[0]["resultados"][0]["series"]
            if not series:
                return None
            
            serie = series[0]["serie"]
            ultimo_periodo = sorted(serie.keys())[-1]
            valor_bruto = serie[ultimo_periodo]
            
            return ibge_client.parse_sidra_value(valor_bruto)
        except (KeyError, IndexError, TypeError):
            return None
    
    @staticmethod
    def get_indicadores_demograficos(nivel: str, codigo: int) -> IndicadorDemografico:
        """
        Obtém todos os indicadores demográficos para uma localidade
        """
        # População
        populacao = AgregadosService.get_valor_agregado(
            Agregados.POPULACAO_ESTIMADA,
            Variaveis.POPULACAO_ESTIMADA,
            nivel,
            codigo
        )
        
        # Área
        area_info = AgregadosService.find_variavel_id(
            Agregados.CENSO_AREA_DENSIDADE,
            Variaveis.AREA
        )
        area = None
        if area_info:
            area = AgregadosService.get_valor_agregado(
                Agregados.CENSO_AREA_DENSIDADE,
                area_info[0],
                nivel,
                codigo
            )
        
        # Densidade
        densidade_info = AgregadosService.find_variavel_id(
            Agregados.CENSO_AREA_DENSIDADE,
            Variaveis.DENSIDADE
        )
        densidade = None
        if densidade_info:
            densidade = AgregadosService.get_valor_agregado(
                Agregados.CENSO_AREA_DENSIDADE,
                densidade_info[0],
                nivel,
                codigo
            )
        
        return IndicadorDemografico(
            populacao=populacao,
            area=area,
            densidade=densidade
        )
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL_AGREGADOS, show_spinner=False)
    def get_ranking_populacao(
        nivel: str,
        codigos: List[int],
        nomes: List[str]
    ) -> List[RankingItem]:
        """
        Gera ranking populacional para uma lista de localidades
        """
        resultados = []
        for codigo, nome in zip(codigos, nomes):
            valor = AgregadosService.get_valor_agregado(
                Agregados.POPULACAO_ESTIMADA,
                Variaveis.POPULACAO_ESTIMADA,
                nivel,
                codigo
            )
            if valor is not None:
                resultados.append(RankingItem(nome=nome, populacao=valor))
        
        return sorted(resultados, key=lambda r: r.populacao, reverse=True)
    
    @staticmethod
    def get_nivel_display(nivel: str) -> str:
        """Retorna o nome display do nível territorial"""
        return NiveisTerritoriais.DISPLAY.get(nivel, nivel)


# Instância global do serviço
agregados_service = AgregadosService()
