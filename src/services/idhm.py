"""
Serviço de IDHM (Índice de Desenvolvimento Humano Municipal)

Importante: o IDHM NÃO é calculado nem publicado pelo IBGE / SIDRA — ele é
calculado pelo PNUD, Ipea e Fundação João Pinheiro (Atlas do Desenvolvimento
Humano no Brasil / atlasbrasil.org.br), com base no Censo Demográfico do
IBGE. Não existe uma API pública em tempo real para esse dado, por isso:

- Nível ESTADO (N3) e BRASIL (N1): valores fixos, verificados a partir do
  Censo 2010 (última edição com IDHM oficial para todas as unidades da
  federação). Fonte: Atlas do Desenvolvimento Humano no Brasil 2013 —
  PNUD / Ipea / FJP. É seguro manter isso como dado estático: o Censo 2010
  não muda, e um novo IDHM oficial só é recalculado a cada novo Censo.

- Nível MUNICÍPIO (N6): são 5.570 municípios — inviável fixar no código com
  segurança de precisão. Este serviço tenta ler um CSV local opcional em
  DATA_IDHM_MUNICIPIOS_PATH (ver settings.py) com colunas
  `codigo_ibge,idhm,ano`. Se o arquivo não existir ou o código não for
  encontrado, retorna None e a UI mostra "—" (sem inventar valor).

  Para popular esse CSV, uma fonte pronta para exportar é o Atlas Brasil
  (https://www.atlasbrasil.org.br/consulta) ou a base "Atlas do
  Desenvolvimento Humano (ADH)" disponível em basedosdados.org.
"""
from typing import Optional, Dict, Any
import csv
import os

import streamlit as st

from src.api.endpoints import NiveisTerritoriais
from src.config.settings import DATA_IDHM_MUNICIPIOS_PATH


# IDHM 2010 por Unidade da Federação (chave = código IBGE do estado)
# Fonte: Atlas do Desenvolvimento Humano no Brasil 2013 (PNUD/Ipea/FJP),
# dados do Censo Demográfico IBGE 2010.
IDHM_ESTADOS_2010: Dict[int, float] = {
    11: 0.690,  # Rondônia
    12: 0.663,  # Acre
    13: 0.674,  # Amazonas
    14: 0.707,  # Roraima
    15: 0.646,  # Pará
    16: 0.708,  # Amapá
    17: 0.699,  # Tocantins
    21: 0.639,  # Maranhão
    22: 0.646,  # Piauí
    23: 0.682,  # Ceará
    24: 0.684,  # Rio Grande do Norte
    25: 0.658,  # Paraíba
    26: 0.673,  # Pernambuco
    27: 0.631,  # Alagoas
    28: 0.665,  # Sergipe
    29: 0.660,  # Bahia
    31: 0.731,  # Minas Gerais
    32: 0.740,  # Espírito Santo
    33: 0.761,  # Rio de Janeiro
    35: 0.783,  # São Paulo
    41: 0.749,  # Paraná
    42: 0.774,  # Santa Catarina
    43: 0.746,  # Rio Grande do Sul
    50: 0.729,  # Mato Grosso do Sul
    51: 0.725,  # Mato Grosso
    52: 0.735,  # Goiás
    53: 0.824,  # Distrito Federal
}

IDHM_BRASIL_2010: float = 0.727

IDHM_ANO_REFERENCIA = "2010"


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def _carregar_idhm_municipios(caminho: str) -> Dict[int, Dict[str, Any]]:
    """
    Carrega o CSV local de IDHM por município, se existir.
    Formato esperado (cabeçalho): codigo_ibge,idhm,ano
    """
    if not caminho or not os.path.isfile(caminho):
        return {}

    resultado: Dict[int, Dict[str, Any]] = {}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    codigo = int(row["codigo_ibge"])
                    valor = float(str(row["idhm"]).replace(",", "."))
                    ano = row.get("ano", "").strip() or None
                    resultado[codigo] = {"valor": valor, "ano": ano}
                except (KeyError, ValueError, TypeError):
                    continue
    except Exception:
        return {}

    return resultado


class IDHMService:
    """Serviço de consulta ao IDHM por localidade"""

    @staticmethod
    def get_idhm(nivel: str, codigo: int) -> Optional[Dict[str, Any]]:
        """
        Retorna {'valor': float, 'ano': str} para o nível/código informado,
        ou None se não houver dado disponível (a UI deve exibir "—" nesse caso,
        nunca um valor inventado).
        """
        if nivel == NiveisTerritoriais.BRASIL:
            return {"valor": IDHM_BRASIL_2010, "ano": IDHM_ANO_REFERENCIA}

        if nivel == NiveisTerritoriais.ESTADO:
            valor = IDHM_ESTADOS_2010.get(codigo)
            if valor is None:
                return None
            return {"valor": valor, "ano": IDHM_ANO_REFERENCIA}

        if nivel == NiveisTerritoriais.MUNICIPIO:
            dados_municipios = _carregar_idhm_municipios(DATA_IDHM_MUNICIPIOS_PATH)
            item = dados_municipios.get(codigo)
            if item is None:
                return None
            return {"valor": item["valor"], "ano": item["ano"] or IDHM_ANO_REFERENCIA}

        return None


# Instância global do serviço
idhm_service = IDHMService()
