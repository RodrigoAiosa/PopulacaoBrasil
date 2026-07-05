"""
Serviços para consulta de agregados do SIDRA
"""
from typing import List, Tuple, Optional, Dict, Any
import streamlit as st
import requests

from src.api.endpoints import (
    APIEndpoints, Agregados, Variaveis, NiveisTerritoriais,
    SIDRA_INVALID_SYMBOLS, PIB_PERIODOS,
)
from src.models.schemas import IndicadorDemografico, RankingItem
from src.config.settings import CACHE_TTL_AGREGADOS, API_TIMEOUT
from src.services.idhm import idhm_service


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
        except Exception:
            pass
        
        # Fallback
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
        """Busca ID de uma variável por palavra-chave no nome"""
        try:
            meta = AgregadosService.get_metadados_agregado(agregado_id)
            palavra_chave = palavra_chave.lower()
            
            for var in meta.get("variaveis", []):
                if palavra_chave in var["nome"].lower():
                    return var["id"], var["nome"], var.get("unidade", "")
        except Exception:
            pass
        
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
        """Consulta valor mais recente de uma variável para uma localidade"""
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
            
            if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                return None
            
            try:
                clean_value = str(valor_bruto).replace(",", ".")
                return float(clean_value)
            except (ValueError, TypeError):
                return None
                
        except Exception:
            return None
    
    @staticmethod
    def get_valores_populacao_lote(
        localidade_query: str,
        periodo: str = "-1"
    ) -> Dict[int, float]:
        """Busca a população de VÁRIAS localidades em UMA ÚNICA requisição"""
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
        except Exception:
            return {}

    @staticmethod
    def get_valores_renda_per_capita_lote(
        nivel: str,
        codigos: List[int],
        periodos: Optional[List[str]] = None
    ) -> Dict[int, float]:
        """
        Busca a renda per capita (PIB per capita) de VÁRIAS localidades de uma vez,
        em no máximo 1 requisição por período tentado — em vez de 1 requisição
        POR LOCALIDADE (que é o que causava a demora ao trocar de filtro).

        Tenta cada período em `periodos` (do mais recente para o mais antigo) e,
        a cada tentativa, só busca os códigos que ainda não tiveram valor
        encontrado nos períodos anteriores.
        """
        if not codigos:
            return {}

        periodos = periodos or PIB_PERIODOS
        pendentes = list(dict.fromkeys(codigos))  # remove duplicados, mantém ordem
        resultado: Dict[int, float] = {}

        for periodo in periodos:
            if not pendentes:
                break
            try:
                query = ",".join(str(c) for c in pendentes)
                data = _fetch_valores_agregado_lote(
                    Agregados.RENDA_PER_CAPITA,
                    Variaveis.PIB_PER_CAPITA,
                    f"{nivel}[{query}]",
                    periodo
                )
                if not data:
                    continue

                series = data[0].get("resultados", [{}])[0].get("series", [])
                for item in series:
                    try:
                        localidade_id = int(item["localidade"]["id"])
                        if localidade_id in resultado:
                            continue

                        serie = item.get("serie", {})
                        valor_bruto = serie.get(periodo)
                        if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                            continue

                        valor_str = str(valor_bruto).strip().replace(".", "").replace(",", ".")
                        valor_float = float(valor_str)
                        if valor_float > 0:
                            resultado[localidade_id] = valor_float
                    except (KeyError, ValueError, TypeError):
                        continue

                pendentes = [c for c in pendentes if c not in resultado]
            except Exception:
                continue

        return resultado

    @staticmethod
    def get_pib_total(nivel: str, codigo: int) -> Optional[float]:
        """
        Obtém o PIB total (em R$) para uma localidade.
        Agregado: 5938 - PIB dos Municípios
        Variável: 37 - PIB total (R$ 1.000)
        """
        periodos_para_tentar = ["2021", "2020", "2019", "2018", "2017", "-1"]
        
        for periodo in periodos_para_tentar:
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
                
                # Tenta encontrar o valor
                valor_bruto = None
                if periodo in serie and periodo != "-1":
                    valor_bruto = serie[periodo]
                else:
                    periodos_disponiveis = sorted(serie.keys())
                    if periodos_disponiveis:
                        ultimo_periodo = periodos_disponiveis[-1]
                        valor_bruto = serie[ultimo_periodo]
                
                if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                    continue
                
                try:
                    clean_value = str(valor_bruto).replace(".", "").replace(",", ".")
                    # Valor está em R$ 1.000
                    return float(clean_value) * 1000
                except (ValueError, TypeError):
                    continue
                    
            except Exception:
                continue
        
        return None

    @staticmethod
    def get_renda_per_capita(nivel: str, codigo: int) -> Optional[float]:
        """
        Obtém o PIB per capita (renda) para uma localidade.
        Tenta múltiplas abordagens:
        1. Agregado 5964 - PIB per capita direto
        2. Calcula a partir do PIB total / População
        """
        # Primeira abordagem: PIB per capita direto (Agregado 5964)
        periodos_para_tentar = ["2021", "2020", "2019", "2018", "2017", "-1"]
        
        for periodo in periodos_para_tentar:
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
                
                resultados = data[0].get("resultados", [])
                if not resultados:
                    continue
                
                series = resultados[0].get("series", [])
                if not series:
                    continue
                
                serie = series[0].get("serie", {})
                if not serie:
                    continue
                
                # Tenta encontrar o valor
                valor_bruto = None
                if periodo in serie and periodo != "-1":
                    valor_bruto = serie[periodo]
                else:
                    periodos_disponiveis = sorted(serie.keys())
                    if periodos_disponiveis:
                        ultimo_periodo = periodos_disponiveis[-1]
                        valor_bruto = serie[ultimo_periodo]
                
                if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
                    continue
                
                try:
                    valor_str = str(valor_bruto).strip()
                    valor_str = valor_str.replace(".", "").replace(",", ".")
                    valor_float = float(valor_str)
                    
                    if valor_float > 0:
                        return valor_float
                except (ValueError, TypeError):
                    continue
                    
            except Exception:
                continue
        
        # Segunda abordagem: Calcular a partir do PIB total e população
        try:
            # Obtém a população
            populacao = AgregadosService.get_valor_agregado(
                Agregados.POPULACAO_ESTIMADA,
                Variaveis.POPULACAO_ESTIMADA,
                nivel,
                codigo
            )
            
            if populacao and populacao > 0:
                # Obtém o PIB total
                pib_total = AgregadosService.get_pib_total(nivel, codigo)
                if pib_total and pib_total > 0:
                    return pib_total / populacao
        except Exception:
            pass
        
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
        
        # Renda per capita e PIB total (apenas para municípios e estados)
        pib_per_capita = None
        pib_total = None
        
        if nivel in [NiveisTerritoriais.MUNICIPIO, NiveisTerritoriais.ESTADO]:
            # Tenta obter a renda per capita
            pib_per_capita = AgregadosService.get_renda_per_capita(nivel, codigo)
            
            # Se conseguiu a renda per capita, tenta obter o PIB total também
            if pib_per_capita:
                pib_total = AgregadosService.get_pib_total(nivel, codigo)
            
            # Se não conseguiu a renda per capita, tenta calcular via PIB total
            if not pib_per_capita:
                pib_total = AgregadosService.get_pib_total(nivel, codigo)
                if pib_total and populacao and populacao > 0:
                    pib_per_capita = pib_total / populacao
        
        # IDHM (apenas Estado e Município — não é dado do IBGE/SIDRA, ver
        # src/services/idhm.py para a fonte e as limitações)
        idhm = None
        idhm_ano = None
        if nivel in [NiveisTerritoriais.MUNICIPIO, NiveisTerritoriais.ESTADO]:
            idhm_info = idhm_service.get_idhm(nivel, codigo)
            if idhm_info:
                idhm = idhm_info["valor"]
                idhm_ano = idhm_info["ano"]

        return IndicadorDemografico(
            populacao=populacao,
            area=area,
            densidade=densidade,
            pib_per_capita=pib_per_capita,
            pib_total=pib_total,
            idhm=idhm,
            idhm_ano=idhm_ano
        )
    
    @staticmethod
    def get_ranking_populacao(
        nivel: str,
        codigos: List[int],
        nomes: List[str]
    ) -> List[RankingItem]:
        """Gera ranking populacional para uma lista de localidades"""
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
    def get_ranking_completo(
        nivel: str,
        codigos: List[int],
        nomes: List[str]
    ) -> List[RankingItem]:
        """
        Gera ranking completo com população e renda per capita para uma lista de localidades.
        """
        if not codigos:
            return []

        # Busca população em lote (1 requisição)
        query = ",".join(str(c) for c in codigos)
        valores_populacao = AgregadosService.get_valores_populacao_lote(f"{nivel}[{query}]")

        # Busca renda per capita em lote (no máx. 1 requisição por período tentado,
        # em vez de 1 requisição POR MUNICÍPIO — é isso que fazia a troca de
        # filtro demorar em estados com muitos municípios)
        valores_renda = AgregadosService.get_valores_renda_per_capita_lote(nivel, codigos)

        resultados = []
        for codigo, nome in zip(codigos, nomes):
            if codigo in valores_populacao:
                populacao = valores_populacao[codigo]
                renda = valores_renda.get(codigo)
                resultados.append(
                    RankingItem(
                        nome=nome,
                        populacao=populacao,
                        renda_per_capita=renda
                    )
                )

        # Ordena por população (maior para menor)
        return sorted(resultados, key=lambda r: r.populacao, reverse=True)
    
    @staticmethod
    def get_nivel_display(nivel: str) -> str:
        """Retorna o nome display do nível territorial"""
        return NiveisTerritoriais.DISPLAY.get(nivel, nivel)


# Instância global do serviço
agregados_service = AgregadosService()
