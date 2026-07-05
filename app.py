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
    
    # Buscar indicadores — com spinner visível.
    # Antes não havia spinner (para dar sensação de transição instantânea),
    # mas isso fazia a tela parecer travada/quebrada durante uma consulta
    # mais lenta à API do IBGE. Como os dados ficam em cache por 6h, o
    # spinner só aparece de fato na primeira consulta de cada contexto.
    with st.spinner("📊 Carregando dados do IBGE..."):
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
            # Nível Brasil (seleção padrão) — TODOS os 26 estados + DF
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
    
        # Dados do mapa (sempre em nível de estado, filtrado por região se houver).
        # Reaproveita o `ranking` já calculado acima quando ele já é por
        # estado (visão Brasil ou Região), evitando buscar os mesmos dados
        # da API duas vezes.
        todos_estados = localidades_service.get_estados()

        if selecoes["regiao"]:
            estados_filtrados = localidades_service.get_estados(selecoes["regiao"].id)
            estados_para_mapa = [
                {"nome": e.nome, "sigla": e.sigla} for e in estados_filtrados
            ]
            ranking_mapa = ranking  # já é o ranking de estados desta região
        elif selecoes["estado"] or selecoes["municipio"]:
            # Nestes níveis, `ranking` é de municípios — o mapa precisa do
            # ranking de TODOS os estados do Brasil, então buscamos à parte.
            estados_para_mapa = [
                {"nome": e.nome, "sigla": e.sigla} for e in todos_estados
            ]
            ranking_mapa = agregados_service.get_ranking_populacao(
                NiveisTerritoriais.ESTADO,
                [e.id for e in todos_estados],
                [e.nome for e in todos_estados]
            )
        else:
            # Visão Brasil: `ranking` já é exatamente isso
            estados_para_mapa = [
                {"nome": e.nome, "sigla": e.sigla} for e in todos_estados
            ]
            ranking_mapa = ranking

        dados_mapa = mapas_service.preparar_dados_mapa(
            ranking_mapa,
            estados_para_mapa
        )
    
    # Renderizar hero
    render_hero_section(
        breadcrumb=selecoes["breadcrumb"],
        populacao=indicadores.populacao,
        nome_local=selecoes["nome_local"]
    )
    
    # Renderizar cards (agora com suporte a Renda Per Capita e PIB)
    render_indicators_cards(
        indicadores=indicadores,
        card4_label=card4_label,
        card4_value=card4_value,
        card4_unit=card4_unit,
        card4_foot=card4_foot
    )
    
    # Renderizar gráfico de ranking
    # Na visão Brasil (nenhum filtro selecionado), mostramos TODOS os estados
    # (27 + DF) em vez de cortar no top 10 padrão.
    esta_na_visao_brasil = not (
        selecoes["regiao"] or selecoes["estado"] or selecoes["municipio"]
    )
    max_items_ranking = len(ranking) if esta_na_visao_brasil else None

    st.markdown(f'<div class="section-title">{chart_title}</div>', unsafe_allow_html=True)
    render_ranking_chart(ranking, chart_title, highlight_nome, max_items=max_items_ranking)
    
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
