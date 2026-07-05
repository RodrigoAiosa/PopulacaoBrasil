"""
Serviços para consulta de agregados do SIDRA
"""
from typing import List, Tuple, Optional, Dict, Any
import streamlit as st
import requests

from src.api.endpoints import APIEndpoints, Agregados, Variaveis, NiveisTerritoriais, SIDRA_INVALID_SYMBOLS, PIB_PERIODOS
from src.models.schemas import IndicadorDemografico, RankingItem
from src.config.settings import CACHE_TTL_AGREGADOS, API_TIMEOUT


@st.cache_data(ttl=CACHE_TTL_AGREGADOS, show_spinner=False)
def _fetch_metadados(agregado_id: int) -> Optional[Dict[str, Any]]:
    """Função cacheada para buscar metadados do agregado"""
    try:
        url = APIEndpoints.get_agregado_metadados_url(agregado_id)
        resp = requests.get(url, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


@st.cache_data(ttl=CACHE_TTL_AGREGADOS, show_spinner=False)
def _fetch_valor_agregado(agregado_id: int, variavel_id: int, localidade: str, periodo: str = "-1") -> Optional[Any]:
    """Função cacheada para buscar valor do agregado"""
    try:
        url = APIEndpoints.get_agregado_valor_url(agregado_id, variavel_id, periodo)
        resp = requests.get(url, params={"localidades": localidade}, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


@st.cache_data(ttl=CACHE_TTL_AGREGADOS, show_spinner=False)
def _fetch_valores_agregado_lote(agregado_id: int, variavel_id: int, localidade_query: str, periodo: str = "-1") -> Optional[Any]:
    """
    Função cacheada para buscar valores de VÁRIAS localidades em UMA ÚNICA requisição.
    localidade_query aceita a sintaxe nativa da API do IBGE, ex:
    "N3[all]" (todos os estados), "N6[N3[35]]" (municípios de SP),
    "N3[11,12,13]" (estados específicos).
    """
    try:
        url = APIEndpoints.get_agregado_valor_url(agregado_id, variavel_id, periodo)
        resp = requests.get(url, params={"localidades": localidade_query}, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


class AgregadosService:
    """Serviço para operações com agregados do SIDRA"""
    
    @staticmethod
    def get_metadados_agregado(agregado_id: int) -> Dict[str, Any]:
        """Obtém metadados de um agregado"""
        try:
            data = _fetch_metadados(agregado_id)
            if data:
                return data
        except Exception as e:
            st.warning(f"⚠️ Não foi possível obter metadados do agregado {agregado_id}: {str(e)}")
        
        # Fallback para metadados do agregado de população
        if agregado_id == Agregados.POPULACAO_ESTIMADA:
            return {
                "id": Agregados.POPULACAO_ESTIMADA,
                "nome": "Estimativas da População",
                "variaveis": [
                    {"id": Variaveis.POPULACAO_ESTIMADA, "nome": "População residente estimada", "unidade": "Pessoas"}
                ]
            }
        elif agregado_id == Agregados.CENSO_AREA_DENSIDADE:
            return {
                "id": Agregados.CENSO_AREA_DENSIDADE,
                "nome": "Censo 2022 - Área e Densidade",
                "variaveis": [
                    {"id": 1, "nome": "Área territorial", "unidade": "km²"},
                    {"id": 2, "nome": "Densidade demográfica", "unidade": "hab/km²"}
                ]
            }
        return {}
    
    @staticmethod
    def find_variavel_id(agregado_id: int, palavra_chave: str) -> Optional[Tuple[int, str, str]]:
        """
        Busca ID de uma variável por palavra-chave no nome
        Retorna (id, nome, unidade) ou None
        """
        try:
            meta = AgregadosService.get_metadados_agregado(agregado_id)
            palavra_chave = palavra_chave.lower()
            
            for var in meta.get("variaveis", []):
                if palavra_chave in var["nome"].lower():
                    return var["id"], var["nome"], var.get("unidade", "")
        except Exception as e:
            st.warning(f"⚠️ Erro ao buscar variável: {str(e)}")
        
        # Fallback: retorna IDs conhecidos
        if agregado_id == Agregados.CENSO_AREA_DENSIDADE:
            if "área" in palavra_chave.lower():
                return 1, "Área territorial", "km²"
            elif "densidade" in palavra_chave.lower():
                return 2, "Densidade demográfica", "hab/km²"
        return None
    
    @staticmethod
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
        try:
            localidade = f"{nivel}[{codigo}]"
            data = _fetch_valor_agregado(agregado_id, variavel_id, localidade, periodo)
            
            if not data:
                return None
            
            series = data[0]["resultados"][0]["series"]
            if not series:
                return None
            
            serie = series[0]["serie"]
            if not serie:
                return None
            
            ultimo_periodo = sorted(serie.keys())[-1]
            valor_bruto = serie[ultimo_periodo]
            
            # Parse do valor
            if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                return None
            
            try:
                clean_value = str(valor_bruto).replace(",", ".")
                return float(clean_value)
            except (ValueError, TypeError):
                return None
                
        except Exception as e:
            st.warning(f"⚠️ Erro ao obter valor do agregado: {str(e)}")
            return None
    
    @staticmethod
    def get_valores_populacao_lote(
        localidade_query: str,
        periodo: str = "-1"
    ) -> Dict[int, float]:
        """
        Busca a população de VÁRIAS localidades em UMA ÚNICA requisição HTTP
        (em vez de uma requisição por localidade). Retorna {codigo_ibge: populacao}.
        """
        try:
            data = _fetch_valores_agregado_lote(
                Agregados.POPULACAO_ESTIMADA,
                Variaveis.POPULACAO_ESTIMADA,
                localidade_query,
                periodo
            )
            if not data:
                return {}

            series = data[0]["resultados"][0]["series"]
            resultado: Dict[int, float] = {}

            for item in series:
                try:
                    localidade_id = int(item["localidade"]["id"])
                    serie = item["serie"]
                    if not serie:
                        continue

                    ultimo_periodo = sorted(serie.keys())[-1]
                    valor_bruto = serie[ultimo_periodo]

                    if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                        continue

                    clean_value = str(valor_bruto).replace(",", ".")
                    resultado[localidade_id] = float(clean_value)
                except (KeyError, ValueError, TypeError):
                    continue

            return resultado
        except Exception as e:
            st.warning(f"⚠️ Erro ao obter valores em lote: {str(e)}")
            return {}

    @staticmethod
    def get_renda_per_capita(nivel: str, codigo: int) -> Optional[float]:
        """
        Obtém o PIB per capita (renda) para uma localidade.
        Tenta múltiplos períodos até encontrar dados.
        """
        # Tentar primeiro o período mais recente, depois os anteriores
        for periodo in PIB_PERIODOS + ["-1"]:
            try:
                localidade = f"{nivel}[{codigo}]"
                data = _fetch_valor_agregado(
                    Agregados.RENDA_PER_CAPITA,
                    Variaveis.PIB_PER_CAPITA,
                    localidade,
                    periodo
                )
                
                if not data:
                    continue
                
                series = data[0]["resultados"][0]["series"]
                if not series:
                    continue
                
                serie = series[0]["serie"]
                if not serie:
                    continue
                
                # Pega o valor do período específico
                if periodo in serie:
                    valor_bruto = serie[periodo]
                else:
                    # Se o período específico não existir, pega o mais recente
                    ultimo_periodo = sorted(serie.keys())[-1]
                    valor_bruto = serie[ultimo_periodo]
                
                if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                    continue
                
                try:
                    # Remove pontos de milhar e substitui vírgula por ponto
                    clean_value = str(valor_bruto).replace(".", "").replace(",", ".")
                    return float(clean_value)
                except (ValueError, TypeError):
                    continue
                    
            except Exception as e:
                continue
        
        return None

    @staticmethod
    def get_pib_total(nivel: str, codigo: int) -> Optional[float]:
        """
        Obtém o PIB total (em R$ 1.000) para uma localidade.
        Tenta múltiplos períodos até encontrar dados.
        """
        # Tentar primeiro o período mais recente, depois os anteriores
        for periodo in PIB_PERIODOS + ["-1"]:
            try:
                localidade = f"{nivel}[{codigo}]"
                data = _fetch_valor_agregado(
                    Agregados.PIB_MUNICIPIOS,
                    Variaveis.PIB_TOTAL,
                    localidade,
                    periodo
                )
                
                if not data:
                    continue
                
                series = data[0]["resultados"][0]["series"]
                if not series:
                    continue
                
                serie = series[0]["serie"]
                if not serie:
                    continue
                
                # Pega o valor do período específico
                if periodo in serie:
                    valor_bruto = serie[periodo]
                else:
                    # Se o período específico não existir, pega o mais recente
                    ultimo_periodo = sorted(serie.keys())[-1]
                    valor_bruto = serie[ultimo_periodo]
                
                if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                    continue
                
                try:
                    # Remove pontos de milhar e substitui vírgula por ponto
                    clean_value = str(valor_bruto).replace(".", "").replace(",", ".")
                    # Valor está em R$ 1.000
                    return float(clean_value) * 1000
                except (ValueError, TypeError):
                    continue
                    
            except Exception as e:
                continue
        
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
        
        # Renda per capita (PIB per capita) - apenas para municípios e estados
        pib_per_capita = None
        pib_total = None
        
        # Busca dados de renda apenas para municípios e estados
        if nivel in [NiveisTerritoriais.MUNICIPIO, NiveisTerritoriais.ESTADO]:
            pib_per_capita = AgregadosService.get_renda_per_capita(nivel, codigo)
            pib_total = AgregadosService.get_pib_total(nivel, codigo)
        
        return IndicadorDemografico(
            populacao=populacao,
            area=area,
            densidade=densidade,
            pib_per_capita=pib_per_capita,
            pib_total=pib_total
        )
    
    @staticmethod
    def get_ranking_populacao(
        nivel: str,
        codigos: List[int],
        nomes: List[str]
    ) -> List[RankingItem]:
        """
        Gera ranking populacional para uma lista de localidades.

        Performance: faz UMA ÚNICA requisição HTTP para todas as localidades
        (usando a sintaxe nativa da API do IBGE "N3[cod1,cod2,...]"), em vez
        de uma requisição por localidade. Isso torna as trocas de filtro no
        menu praticamente instantâneas, mesmo para níveis com muitos itens
        (ex: os ~645 municípios de São Paulo).
        """
        if not codigos:
            return []

        query = ",".join(str(c) for c in codigos)
        valores = AgregadosService.get_valores_populacao_lote(f"{nivel}[{query}]")

        resultados = [
            RankingItem(nome=nome, populacao=valores[codigo])
            for codigo, nome in zip(codigos, nomes)
            if codigo in valores
        ]

        return sorted(resultados, key=lambda r: r.populacao, reverse=True)
    
    @staticmethod
    def get_nivel_display(nivel: str) -> str:
        """Retorna o nome display do nível territorial"""
        return NiveisTerritoriais.DISPLAY.get(nivel, nivel)


# Instância global do serviço
agregados_service = AgregadosService()
