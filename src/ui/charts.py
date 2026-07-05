"""
Gráficos e visualizações
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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
        # Não exibe nada se não houver dados
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


def render_ranking_table(
    ranking: List[RankingItem],
    title: str,
    highlight_nome: Optional[str] = None,
    max_items: Optional[int] = None
):
    """
    Renderiza uma tabela de ranking com 3 colunas:
    - Posição
    - Município
    - População
    - Renda per Capita
    
    Ordenada por população (maior para menor)
    """
    if not ranking:
        # Não exibe nada se não houver dados
        return
    
    # Limitar itens se especificado
    if max_items:
        ranking = ranking[:max_items]
    
    # Preparar dados para o DataFrame
    dados = []
    for i, item in enumerate(ranking, 1):
        # Destacar o item selecionado
        is_highlight = highlight_nome and item.nome == highlight_nome
        
        dados.append({
            "Posição": f"{i}º",
            "Município": item.nome,
            "População": item.populacao_formatada,
            "Renda per Capita": item.renda_per_capita_formatada,
            "_highlight": is_highlight
        })
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Remover coluna auxiliar para exibição
    df_display = df[["Posição", "Município", "População", "Renda per Capita"]]
    
    # Exibir título
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    
    # Exibir tabela estilizada
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Posição": st.column_config.TextColumn(
                "#",
                width="small"
            ),
            "Município": st.column_config.TextColumn(
                "Município",
                width="large"
            ),
            "População": st.column_config.TextColumn(
                "População",
                width="medium"
            ),
            "Renda per Capita": st.column_config.TextColumn(
                "Renda per Capita",
                width="medium"
            )
        }
    )
    
    # Mostrar total de municípios
    st.caption(f"📊 Mostrando {len(ranking)} municípios")
