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
from src.ui.charts import render_ranking_chart, render_ranking_table
from src.ui.map_view import render_population_map

from src.services.localidades import localidades_service
from src.services.agregados import agregados_service
from src.services.mapas import mapas_service
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
    
    # Obter nomes para o mapa
    nome_municipio = selecoes["municipio"].nome if selecoes["municipio"] else None
    nome_estado = selecoes["estado"].nome if selecoes["estado"] else None
    
    # Buscar indicadores
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
                
                # Usa o ranking completo com renda
                ranking = agregados_service.get_ranking_completo(
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
                chart_title = f"Ranking dos municípios de {selecoes['estado'].sigla}"
                highlight_nome = selecoes["municipio"].nome
            else:
                # Defensivo: o estado do município selecionado não foi encontrado
                # na lista atual de estados (ex.: API do IBGE indisponível nesta
                # consulta específica, retornando um conjunto de fallback
                # diferente do usado quando a seleção foi feita). Sem este bloco,
                # as variáveis abaixo ficariam indefinidas e o app quebraria com
                # UnboundLocalError mais adiante — em vez disso, mostramos um
                # estado vazio claro para o usuário.
                ranking = []
                card4_label = "Posição no estado"
                card4_value = "—"
                card4_unit = ""
                card4_foot = "dado indisponível no momento"
                chart_title = f"Ranking dos municípios de {selecoes['estado'].sigla}"
                highlight_nome = selecoes["municipio"].nome
        
        elif selecoes["estado"]:
            # Nível estado
            municipios = localidades_service.get_municipios(selecoes["estado"].id)
            peer_codigos = [m.id for m in municipios]
            peer_nomes = [m.nome for m in municipios]
            
            # Usa o ranking completo com renda
            ranking = agregados_service.get_ranking_completo(
                NiveisTerritoriais.MUNICIPIO,
                peer_codigos,
                peer_nomes
            )
            
            card4_label = "Municípios"
            card4_value = fmt_int(len(municipios))
            card4_unit = ""
            card4_foot = "no estado"
            chart_title = f"Ranking dos municípios de {selecoes['estado'].nome}"
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
    
        # Dados do mapa
        todos_estados = localidades_service.get_estados()

        if selecoes["regiao"]:
            estados_filtrados = localidades_service.get_estados(selecoes["regiao"].id)
            estados_para_mapa = [
                {"nome": e.nome, "sigla": e.sigla} for e in estados_filtrados
            ]
            ranking_mapa = ranking
        elif selecoes["estado"] or selecoes["municipio"]:
            estados_para_mapa = [
                {"nome": e.nome, "sigla": e.sigla} for e in todos_estados
            ]
            ranking_mapa = agregados_service.get_ranking_populacao(
                NiveisTerritoriais.ESTADO,
                [e.id for e in todos_estados],
                [e.nome for e in todos_estados]
            )
        else:
            estados_para_mapa = [
                {"nome": e.nome, "sigla": e.sigla} for e in todos_estados
            ]
            ranking_mapa = ranking

        dados_mapa = mapas_service.preparar_dados_mapa(
            ranking_mapa,
            estados_para_mapa,
            municipio_selecionado=nome_municipio,
            estado_selecionado=nome_estado
        )
    
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
    
    # Renderizar ranking (tabela para municípios/estados, gráfico para regiões/brasil)
    esta_na_visao_municipio_estado = selecoes["municipio"] or selecoes["estado"]
    esta_na_visao_brasil = not (
        selecoes["regiao"] or selecoes["estado"] or selecoes["municipio"]
    )
    
    if esta_na_visao_municipio_estado:
        # Para municípios e estados, mostra a tabela com 3 colunas
        render_ranking_table(
            ranking=ranking,
            title=chart_title,
            highlight_nome=highlight_nome,
            max_items=None  # Mostra todos
        )
    else:
        # Para regiões e Brasil, mostra o gráfico de barras
        max_items_ranking = len(ranking) if esta_na_visao_brasil else None
        render_ranking_chart(
            ranking=ranking,
            title=chart_title,
            highlight_nome=highlight_nome,
            max_items=max_items_ranking
        )
    
    # Renderizar mapa com destaque para município/estado selecionado
    if selecoes["regiao"]:
        titulo_mapa = f"🗺️ Mapa: população por estado - Região {selecoes['regiao'].nome}"
    else:
        titulo_mapa = "🗺️ Mapa: população por estado - Brasil"
    
    render_population_map(
        dados_mapa, 
        ranking_mapa, 
        titulo_mapa,
        municipio_selecionado=nome_municipio,
        estado_selecionado=nome_estado
    )
    
    # Rodapé
    st.caption(UI_TEXTS["source"])
    
    # Mostrar status do modo offline
    if modo_offline:
        st.info("📡 **Modo Offline Ativo** - Dados limitados disponíveis.")


if __name__ == "__main__":
    main()
