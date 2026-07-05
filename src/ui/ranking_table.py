"""
Componente de tabela de ranking com 3 colunas
"""
import streamlit as st
import pandas as pd
from typing import List, Optional

from src.models.schemas import RankingItem


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
