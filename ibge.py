"""
Cliente para as APIs públicas e gratuitas do IBGE.

APIs utilizadas (nenhuma exige chave de acesso):
- Localidades:        https://servicodados.ibge.gov.br/api/v1/localidades
- Agregados (SIDRA):  https://servicodados.ibge.gov.br/api/v3/agregados
- Malhas geográficas: https://servicodados.ibge.gov.br/api/v3/malhas

Documentação oficial: https://servicodados.ibge.gov.br/api/docs
"""

from __future__ import annotations

import requests
import streamlit as st

BASE_LOC = "https://servicodados.ibge.gov.br/api/v1/localidades"
BASE_AGG = "https://servicodados.ibge.gov.br/api/v3/agregados"
BASE_MALHA = "https://servicodados.ibge.gov.br/api/v3/malhas"

TIMEOUT = 15

# Agregados (tabelas do SIDRA) usados no painel
AGREGADO_POPULACAO_ESTIMADA = 6579   # Estimativas da população (anual, todos os níveis)
VARIAVEL_POPULACAO_ESTIMADA = 9324   # "População residente estimada"

AGREGADO_CENSO_AREA_DENSIDADE = 4714  # Censo 2022: População, Área territorial e Densidade

# Símbolos especiais do SIDRA que não representam números válidos
SIDRA_SIMBOLOS_INVALIDOS = {"-", "..", "...", "X", ""}


def _get_json(url: str, params: dict | None = None):
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# Localidades
# --------------------------------------------------------------------------

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_regioes() -> list[dict]:
    """Lista as 5 grandes regiões do Brasil."""
    data = _get_json(f"{BASE_LOC}/regioes")
    return sorted(data, key=lambda r: r["nome"])


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_estados(regiao_id: int | None = None) -> list[dict]:
    """Lista estados, opcionalmente filtrados por uma região."""
    if regiao_id:
        data = _get_json(f"{BASE_LOC}/regioes/{regiao_id}/estados")
    else:
        data = _get_json(f"{BASE_LOC}/estados")
    return sorted(data, key=lambda e: e["nome"])


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_municipios(uf_id: int) -> list[dict]:
    """Lista municípios de um estado (por ID ou sigla da UF)."""
    data = _get_json(f"{BASE_LOC}/estados/{uf_id}/municipios")
    return sorted(data, key=lambda m: m["nome"])


# --------------------------------------------------------------------------
# Agregados / SIDRA
# --------------------------------------------------------------------------

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_metadados_agregado(agregado_id: int) -> dict:
    """Metadados de um agregado (nome, variáveis disponíveis, níveis territoriais etc.)."""
    return _get_json(f"{BASE_AGG}/{agregado_id}/metadados")


def find_variavel_id(agregado_id: int, palavra_chave: str) -> tuple[int, str, str] | None:
    """
    Busca dinamicamente o ID de uma variável de um agregado a partir de uma
    palavra-chave no nome (ex.: "Área", "Densidade"), evitando fixar IDs
    incertos no código. Retorna (id, nome, unidade) ou None se não encontrar.
    """
    meta = get_metadados_agregado(agregado_id)
    palavra_chave = palavra_chave.lower()
    for var in meta.get("variaveis", []):
        if palavra_chave in var["nome"].lower():
            return var["id"], var["nome"], var.get("unidade", "")
    return None


def _nivel_para_localidade(nivel: str, codigo: int | str) -> str:
    """Monta o parâmetro de localidade da API (ex.: N3[35], N6[3550308])."""
    return f"{nivel}[{codigo}]"


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def get_valor_agregado(
    agregado_id: int,
    variavel_id: int,
    nivel: str,
    codigo: int | str,
    periodo: str = "-1",
) -> float | None:
    """
    Consulta o valor mais recente de uma variável de um agregado do SIDRA
    para uma localidade específica.

    nivel: "N1" (Brasil), "N2" (Região), "N3" (Estado), "N6" (Município)
    codigo: código IBGE da localidade (1 para Brasil)
    """
    localidade = _nivel_para_localidade(nivel, codigo)
    url = f"{BASE_AGG}/{agregado_id}/periodos/{periodo}/variaveis/{variavel_id}"
    try:
        data = _get_json(url, params={"localidades": localidade})
    except requests.RequestException:
        return None

    try:
        resultados = data[0]["resultados"][0]["series"]
        if not resultados:
            return None
        serie = resultados[0]["serie"]
        ultimo_periodo = sorted(serie.keys())[-1]
        valor_bruto = serie[ultimo_periodo]
    except (KeyError, IndexError, TypeError):
        return None

    if valor_bruto in SIDRA_SIMBOLOS_INVALIDOS:
        return None
    try:
        return float(str(valor_bruto).replace(",", "."))
    except ValueError:
        return None


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def get_ranking_populacao(nivel: str, codigos: tuple, nomes: tuple) -> list[dict]:
    """
    Busca a população estimada para uma lista de localidades do mesmo nível
    e retorna uma lista ordenada [{"nome": ..., "populacao": ...}, ...].
    Usado para montar os gráficos de ranking (top municípios / estados).
    """
    resultados = []
    for codigo, nome in zip(codigos, nomes):
        valor = get_valor_agregado(
            AGREGADO_POPULACAO_ESTIMADA, VARIAVEL_POPULACAO_ESTIMADA, nivel, codigo
        )
        if valor is not None:
            resultados.append({"nome": nome, "populacao": valor})
    return sorted(resultados, key=lambda r: r["populacao"], reverse=True)


# --------------------------------------------------------------------------
# Malhas geográficas
# --------------------------------------------------------------------------

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_malha_estados() -> dict:
    """GeoJSON com o contorno das 27 unidades da federação (resolução leve)."""
    url = f"{BASE_MALHA}/BR"
    return _get_json(url, params={"resolucao": 2, "formato": "application/vnd.geo+json"})
