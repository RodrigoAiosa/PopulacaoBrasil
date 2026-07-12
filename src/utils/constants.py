"""
Constantes gerais do projeto
"""

# Textos da UI
UI_TEXTS = {
    "app_title": "Painel Demográfico do Brasil",
    "app_icon": "🗺️",
    "sidebar_title": "🗺️ Filtros",
    "sidebar_caption": "Região, Estado e Município (cidade) em cascata.",
    "hero_sub": "Painel construído com as APIs públicas do IBGE (Localidades e Agregados/SIDRA). Use os filtros à esquerda para navegar por região, estado e município.",
    "source": "Dados: IBGE — API de Localidades, API de Agregados (SIDRA) e API de Malhas Geográficas. Estimativas de população: tabela 6579. Área e densidade: Censo Demográfico 2022 (tabela 4714)."
}

# Opções de seleção
FILTER_OPTIONS = {
    "todas_regioes": "Brasil — todas as regiões",
    "todos_estados": "Todos os estados da seleção",
    "todos_municipios": "Todos os municípios do estado",
}

# Cores do tema
THEME_COLORS = {
    "primary": "#1F6F5C",
    "primary_dark": "#123A30",
    "gold": "#C9962E",
    "brick": "#B54B3A",
    "highlight": "#C9962E",  # mesmo que gold
}

# Configurações de gráficos
CHART_CONFIG = {
    "max_items_ranking": 10,
    "chart_height": 420,
    "bar_color_default": "#1F6F5C",
    "bar_color_highlight": "#C9962E",
}
