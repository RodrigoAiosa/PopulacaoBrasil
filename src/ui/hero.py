"""
Componente Hero
"""
from typing import Optional

from src.ui.components import render_hero
from src.utils.formatters import fmt_int


def render_hero_section(
    breadcrumb: str,
    populacao: Optional[float],
    nome_local: str
):
    """
    Renderiza o hero section com informações demográficas
    """
    render_hero(
        breadcrumb=breadcrumb,
        value=fmt_int(populacao),
        label=f"habitantes estimados em {nome_local}",
        subtitle=(
            "Painel construído com as APIs públicas do IBGE (Localidades e Agregados/SIDRA). "
            "Use os filtros à esquerda para navegar por região, estado e município."
        )
    )
