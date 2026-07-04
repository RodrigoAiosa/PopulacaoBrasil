"""
Painel Demográfico do Brasil — dados públicos do IBGE
Rode com: streamlit run app.py
"""
import streamlit as st

# Configuração da página (deve ser a primeira chamada)
st.set_page_config(
    page_title="Painel Demográfico do Brasil",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importações dos módulos
from src.ui.css import get_css
from src.ui.sidebar import sidebar_filters
from src.ui.hero import render_hero_section
from src.ui.cards import render_indicators_cards
from src.ui.charts import render_ranking_chart
from src.ui.map_view import render_population_map

from src.services.localidades import localidades_service
from src.services.agregados import agregados_service
from src.services.mapas import mapas_service
from src.models.schemas import IndicadorDemografico
from src.utils.formatters import fmt_int
from src.utils.constants import UI_TEXTS
from src.api.endpoints import NiveisTerritoriais


def main():
    """Função principal do aplicativo"""
    
    # Injetar CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Renderizar sidebar e obter seleções
    selecoes = sidebar_filters.render()
    
    nivel = selecoes["nivel"]
    codigo = selecoes["codigo"]
    modo_offline = selecoes.get("modo_offline", False)
    
    # Buscar indicadores (sem spinner para transição instantânea)
    indicadores = agregados_service.get_indicadores_demograficos(nivel, codigo)
    
    # Determinar contexto para o quarto card e ranking
    if selecoes["municipio"]:
        # Nível município
        estados = localidades_service.get_estados()
        estado_obj = next(
            (e for e in estados if e.id == selecoes["estado"].id), 
            None
        )
        if estado_obj:
            municipios = localidades_service.get_municipios(estado_obj.id)
            peer_codigos = [m.id for m in municipios]
            peer_nomes = [m.nome for m in municipios]
            ranking = agregados_service.get_ranking_populacao(
                NiveisTerritoriais.MUNICIPIO,
                peer_codigos,
                peer_nomes
            )
            posicao = next(
                (i + 1 for i, r in enumerate(ranking) if r.nome == selecoes["municipio"].nome),
                None
            )
            card4_label = "Posição no estado"
            card4_value = f"{posicao}º" if posicao else "—"
            card4_unit = ""
            card4_foot = f"de {len(ranking)} municípios"
            chart_title = f"Ranking de população — municípios de {selecoes['estado'].sigla}"
            highlight_nome = selecoes["municipio"].nome
    
    elif selecoes["estado"]:
        # Nível estado
        municipios = localidades_service.get_municipios(selecoes["estado"].id)
        peer_codigos = [m.id for m in municipios]
        peer_nomes = [m.nome for m in municipios]
        ranking = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.MUNICIPIO,
            peer_codigos,
            peer_nomes
        )
        card4_label = "Municípios"
        card4_value = fmt_int(len(municipios))
        card4_unit = ""
        card4_foot = "no estado"
        chart_title = f"Top municípios de {selecoes['estado'].nome} por população"
        highlight_nome = None
    
    elif selecoes["regiao"]:
        # Nível região
        estados = localidades_service.get_estados(selecoes["regiao"].id)
        peer_codigos = [e.id for e in estados]
        peer_nomes = [e.nome for e in estados]
        ranking = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.ESTADO,
            peer_codigos,
            peer_nomes
        )
        total_municipios = sum(
            len(localidades_service.get_municipios(e.id)) for e in estados
        )
        card4_label = "Municípios"
        card4_value = fmt_int(total_municipios)
        card4_unit = ""
        card4_foot = f"em {len(estados)} estados"
        chart_title = f"Estados da região {selecoes['regiao'].nome} por população"
        highlight_nome = None
    
    else:
        # Nível Brasil
        todos_estados = localidades_service.get_estados()
        peer_codigos = [e.id for e in todos_estados]
        peer_nomes = [e.nome for e in todos_estados]
        ranking = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.ESTADO,
            peer_codigos,
            peer_nomes
        )
        card4_label = "Estados"
        card4_value = "27"
        card4_unit = ""
        card4_foot = "+ Distrito Federal"
        chart_title = "Estados do Brasil por população"
        highlight_nome = None
    
    # Renderizar hero
    render_hero_section(
        breadcrumb=selecoes["breadcrumb"],
        populacao=indicadores.populacao,
        nome_local=selecoes["nome_local"]
    )
    
    # Renderizar cards
    render_indicators_cards(
        indicadores=indicadores,
        card4_label=card4_label,
        card4_value=card4_value,
        card4_unit=card4_unit,
        card4_foot=card4_foot
    )
    
    # Renderizar gráfico de ranking
    st.markdown(f'<div class="section-title">{chart_title}</div>', unsafe_allow_html=True)
    render_ranking_chart(ranking, chart_title, highlight_nome)
    
    # Renderizar mapa - FILTRADO POR REGIÃO
    # Preparar dados para o mapa baseado na seleção
    todos_estados = localidades_service.get_estados()
    
    # Filtrar estados pela região selecionada
    if selecoes["regiao"]:
        # Se uma região está selecionada, mostrar apenas os estados dela
        estados_filtrados = localidades_service.get_estados(selecoes["regiao"].id)
        estados_para_mapa = [
            {"nome": e.nome, "sigla": e.sigla} for e in estados_filtrados
        ]
        codigos_para_mapa = [e.id for e in estados_filtrados]
        nomes_para_mapa = [e.nome for e in estados_filtrados]
        
        ranking_mapa = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.ESTADO,
            codigos_para_mapa,
            nomes_para_mapa
        )
    else:
        # Sem região selecionada, mostrar todos os estados
        estados_para_mapa = [
            {"nome": e.nome, "sigla": e.sigla} for e in todos_estados
        ]
        ranking_mapa = agregados_service.get_ranking_populacao(
            NiveisTerritoriais.ESTADO,
            [e.id for e in todos_estados],
            [e.nome for e in todos_estados]
        )
    
    dados_mapa = mapas_service.preparar_dados_mapa(
        ranking_mapa,
        estados_para_mapa
    )
    
    # Título do mapa dinâmico
    if selecoes["regiao"]:
        titulo_mapa = f"🗺️ Mapa: população por estado - Região {selecoes['regiao'].nome}"
    else:
        titulo_mapa = "🗺️ Mapa: população por estado - Brasil"
    
    render_population_map(dados_mapa, ranking_mapa, titulo_mapa)
    
    # Rodapé
    st.caption(UI_TEXTS["source"])
    
    # Mostrar status do modo offline
    if modo_offline:
        st.info("📡 **Modo Offline Ativo** - Dados limitados disponíveis.")


if __name__ == "__main__":
    main()
