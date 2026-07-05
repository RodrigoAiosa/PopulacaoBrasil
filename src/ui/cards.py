"""
Cards de indicadores
"""
import streamlit as st

from src.ui.components import render_card
from src.utils.formatters import fmt_int, fmt_dec
from src.models.schemas import IndicadorDemografico


def render_indicators_cards(
    indicadores: IndicadorDemografico,
    card4_label: str,
    card4_value: str,
    card4_unit: str = "",
    card4_foot: str = ""
):
    """
    Renderiza os 4 cards de indicadores
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_card(
            "População estimada",
            fmt_int(indicadores.populacao),
            "hab.",
            "Estimativas IBGE"
        )
    
    with col2:
        render_card(
            "Área territorial",
            fmt_dec(indicadores.area, 0),
            "km²",
            "Censo 2022"
        )
    
    with col3:
        render_card(
            "Densidade demográfica",
            fmt_dec(indicadores.densidade, 1),
            "hab/km²",
            "Censo 2022"
        )
    
    with col4:
        # Verifica se temos dados de renda
        if indicadores.pib_per_capita is not None:
            # Mostra renda per capita no 4º card
            render_card(
                "Renda per capita",
                indicadores.pib_per_capita_formatado,
                "",
                "PIB per capita (IBGE)"
            )
        else:
            # Fallback para o card original
            render_card(
                card4_label,
                card4_value,
                card4_unit,
                card4_foot
            )
