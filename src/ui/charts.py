"""
Gráficos e visualizações
"""
import streamlit as st
import plotly.graph_objects as go
from typing import List, Optional

from src.models.schemas import RankingItem
from src.utils.formatters import fmt_int
from src.utils.constants import THEME_COLORS, CHART_CONFIG


def render_ranking_chart(
    ranking: List[RankingItem],
    title: str,
    highlight_nome: Optional[str] = None,
    max_items: int = None
):
    """
    Renderiza gráfico de ranking populacional
    """
    if max_items is None:
        max_items = CHART_CONFIG["max_items_ranking"]
    
    top = ranking[:max_items] if ranking else []
    
    if not top:
        st.info("Sem dados de ranking disponíveis para esta seleção.")
        return
    
    # Preparar dados
    nomes = [r.nome for r in reversed(top)]
    valores = [r.populacao for r in reversed(top)]
    
    # Cores: destaque para item selecionado
    cores = [
        THEME_COLORS["highlight"] 
        if highlight_nome and n == highlight_nome 
        else THEME_COLORS["primary"]
        for n in nomes
    ]
    
    # Criar gráfico
    fig = go.Figure(
        go.Bar(
            x=valores,
            y=nomes,
            orientation="h",
            marker_color=cores,
            text=[fmt_int(v) for v in valores],
            textposition="outside",
            textfont=dict(color="#000000"),
        )
    )
    
    # Layout
    # Altura proporcional à quantidade de itens, para não espremer as barras
    # quando exibimos a lista completa (ex: os 27 estados na visão Brasil).
    altura_por_item = 26
    altura_dinamica = max(CHART_CONFIG["chart_height"], len(top) * altura_por_item)

    fig.update_layout(
        height=altura_dinamica,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color="#000000"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#D8E0D9",
            title="Habitantes",
            tickfont=dict(color="#000000"),
            title_font=dict(color="#000000")
        ),
        yaxis=dict(
            title="",
            tickfont=dict(color="#000000")
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)
