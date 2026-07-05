"""
Sidebar com filtros em cascata e busca dinâmica
"""
import streamlit as st
from typing import Tuple, Optional, Dict, Any, List

from src.services.localidades import localidades_service
from src.services.exportador import exportador_service
from src.models.schemas import Regiao, Estado, Municipio
from src.utils.constants import FILTER_OPTIONS


class SidebarFilters:
    """
    Gerenciador dos filtros da sidebar com busca dinâmica
    """
    
    def __init__(self):
        self.regioes = []
        self.estados = []
        self.municipios = []
        
        self.regiao_selecionada: Optional[Regiao] = None
        self.estado_selecionado: Optional[Estado] = None
        self.municipio_selecionado: Optional[Municipio] = None
        
        self._connection_error = False
        
        # Cache para busca
        self._search_cache = {}
    
    def render(self) -> Dict[str, Any]:
        """
        Renderiza a sidebar com filtros e retorna seleções
        """
        st.sidebar.markdown("## 🗺️ Filtros")
        st.sidebar.caption("Região, Estado e Município (cidade) em cascata. 🔍 Digite para buscar.")
        
        # Carregar regiões
        try:
            self.regioes = localidades_service.get_regioes()
            if not self.regioes:
                self._connection_error = True
                st.sidebar.warning(
                    "⚠️ Não foi possível carregar os dados do IBGE.\n"
                    "Usando dados de fallback (limitados)."
                )
        except Exception as e:
            self._connection_error = True
            st.sidebar.warning(f"⚠️ Erro ao conectar com a API: {str(e)[:100]}...")
        
        # ==================== REGIÃO ====================
        self._render_regiao_select()
        
        # ==================== ESTADO ====================
        self._render_estado_select()
        
        # ==================== MUNICÍPIO ====================
        self._render_municipio_select()
        
        # ==================== EXPORTAÇÃO ====================
        st.sidebar.markdown("---")
        self._render_export_button()
        
        # ==================== LINKEDIN ====================
        self._render_linkedin_footer()
        
        # ==================== FONTE ====================
        st.sidebar.markdown("---")
        st.sidebar.caption(
            "Fonte: [API de Localidades e Agregados do IBGE]"
            "(https://servicodados.ibge.gov.br/api/docs) — dados públicos e gratuitos."
        )
        
        return {
            "regiao": self.regiao_selecionada,
            "estado": self.estado_selecionado,
            "municipio": self.municipio_selecionado,
            "nivel": self._determinar_nivel(),
            "codigo": self._determinar_codigo(),
            "breadcrumb": self._get_breadcrumb(),
            "nome_local": self._get_nome_local(),
            "modo_offline": self._connection_error
        }
    
    def _render_regiao_select(self):
        """Renderiza seletor de região com busca"""
        regiao_nomes = [FILTER_OPTIONS["todas_regioes"]] + [r.nome for r in self.regioes]
        
        # Campo de busca para região
        search_regiao = st.sidebar.text_input(
            "🔍 Buscar região",
            placeholder="Digite o nome da região...",
            key="search_regiao",
            label_visibility="collapsed"
        )
        
        # Filtrar regiões
        if search_regiao:
            search_lower = search_regiao.lower()
            regiao_filtradas = [r for r in self.regioes if search_lower in r.nome.lower()]
            regiao_nomes_filtrados = [FILTER_OPTIONS["todas_regioes"]] + [r.nome for r in regiao_filtradas]
        else:
            regiao_nomes_filtrados = regiao_nomes
        
        # Seletor com opção de buscar
        regiao_nome_sel = st.sidebar.selectbox(
            "Região", 
            regiao_nomes_filtrados,
            key="regiao_select"
        )
        
        # Determinar seleção
        nova_regiao = None
        if regiao_nome_sel and regiao_nome_sel != FILTER_OPTIONS["todas_regioes"]:
            # Busca a região pelo nome (pode ser filtrada)
            for r in self.regioes:
                if r.nome == regiao_nome_sel:
                    nova_regiao = r
                    break
        
        # Se a região mudou, resetar estado e município
        if self.regiao_selecionada != nova_regiao:
            self.regiao_selecionada = nova_regiao
            self.estado_selecionado = None
            self.municipio_selecionado = None
            # Limpa a busca de estado e município
            if 'search_estado' in st.session_state:
                st.session_state.search_estado = ""
            if 'search_municipio' in st.session_state:
                st.session_state.search_municipio = ""
            st.rerun()
    
    def _render_estado_select(self):
        """Renderiza seletor de estado com busca dinâmica"""
        # Carregar estados baseado na região selecionada
        try:
            self.estados = localidades_service.get_estados(
                self.regiao_selecionada.id if self.regiao_selecionada else None
            )
        except Exception as e:
            st.sidebar.warning(f"⚠️ Erro ao carregar estados: {str(e)[:100]}...")
            self.estados = []
        
        if not self.estados:
            st.sidebar.selectbox(
                "Estado",
                ["Selecione uma região primeiro"],
                disabled=True,
                key="estado_disabled"
            )
            return
        
        # Campo de busca para estado
        search_estado = st.sidebar.text_input(
            "🔍 Buscar estado",
            placeholder="Digite o nome do estado...",
            key="search_estado",
            label_visibility="collapsed"
        )
        
        # Lista de estados com formatação
        estado_labels = [f'{e.nome} ({e.sigla})' for e in self.estados]
        
        # Filtrar estados pela busca
        if search_estado:
            search_lower = search_estado.lower()
            indices_filtrados = []
            for i, e in enumerate(self.estados):
                if search_lower in e.nome.lower() or search_lower in e.sigla.lower():
                    indices_filtrados.append(i)
            
            estado_labels_filtrados = [estado_labels[i] for i in indices_filtrados]
            estados_filtrados = [self.estados[i] for i in indices_filtrados]
        else:
            estado_labels_filtrados = [FILTER_OPTIONS["todos_estados"]] + estado_labels
            estados_filtrados = self.estados
        
        # Seletor com busca
        estado_label_sel = st.sidebar.selectbox(
            "Estado",
            estado_labels_filtrados,
            key="estado_select"
        )
        
        # Determinar seleção
        novo_estado = None
        if estado_label_sel and estado_label_sel != FILTER_OPTIONS["todos_estados"]:
            # Busca o estado pelo label
            for e in estados_filtrados:
                label = f'{e.nome} ({e.sigla})'
                if label == estado_label_sel:
                    novo_estado = e
                    break
        
        # Se o estado mudou, resetar município
        if self.estado_selecionado != novo_estado:
            self.estado_selecionado = novo_estado
            self.municipio_selecionado = None
            if 'search_municipio' in st.session_state:
                st.session_state.search_municipio = ""
            if novo_estado is not None:
                st.rerun()
    
    def _render_municipio_select(self):
        """Renderiza seletor de município com busca dinâmica"""
        # Carregar municípios baseado no estado selecionado
        if self.estado_selecionado:
            try:
                self.municipios = localidades_service.get_municipios(
                    self.estado_selecionado.id
                )
            except Exception as e:
                st.sidebar.warning(f"⚠️ Erro ao carregar municípios: {str(e)[:100]}...")
                self.municipios = []
        else:
            self.municipios = []
        
        if not self.municipios:
            st.sidebar.selectbox(
                "Cidade / Município",
                ["Selecione um estado primeiro"],
                disabled=True,
                key="municipio_disabled"
            )
            self.municipio_selecionado = None
            return
        
        # Campo de busca para município
        search_municipio = st.sidebar.text_input(
            "🔍 Buscar cidade",
            placeholder="Digite o nome da cidade...",
            key="search_municipio",
            label_visibility="collapsed"
        )
        
        # Lista de municípios
        municipio_nomes = [m.nome for m in self.municipios]
        
        # Filtrar municípios pela busca
        if search_municipio:
            search_lower = search_municipio.lower()
            indices_filtrados = []
            for i, m in enumerate(self.municipios):
                if search_lower in m.nome.lower():
                    indices_filtrados.append(i)
            
            municipio_nomes_filtrados = [municipio_nomes[i] for i in indices_filtrados]
            municipios_filtrados = [self.municipios[i] for i in indices_filtrados]
        else:
            municipio_nomes_filtrados = [FILTER_OPTIONS["todos_municipios"]] + municipio_nomes
            municipios_filtrados = self.municipios
        
        # Seletor com busca
        municipio_nome_sel = st.sidebar.selectbox(
            "Cidade / Município",
            municipio_nomes_filtrados,
            key="municipio_select"
        )
        
        # Determinar seleção
        if municipio_nome_sel and municipio_nome_sel != FILTER_OPTIONS["todos_municipios"]:
            # Busca o município pelo nome
            for m in municipios_filtrados:
                if m.nome == municipio_nome_sel:
                    self.municipio_selecionado = m
                    break
        else:
            self.municipio_selecionado = None
    
    def _render_export_button(self):
        """Renderiza o botão de exportação na sidebar."""
        st.sidebar.markdown("### 📊 Exportar Dados")
        st.sidebar.caption("Baixe os dados em CSV")
        
        nivel = self._determinar_nivel()
        
        if nivel == "N6" and self.estado_selecionado:
            cache_key = f"municipios_{self.estado_selecionado.id}"
            nome_arquivo = f"dados_municipios_{self.estado_selecionado.sigla.lower()}"
            label_gerar = f"📊 Gerar CSV — Municípios de {self.estado_selecionado.sigla}"
            label_baixar = f"📥 CSV - Municípios de {self.estado_selecionado.sigla}"
            estado_id = self.estado_selecionado.id
            gerar_fn = lambda: exportador_service.gerar_dados_municipios_estado(estado_id)

        elif nivel == "N3" and self.estado_selecionado:
            cache_key = f"estado_{self.estado_selecionado.id}"
            nome_arquivo = f"dados_estado_{self.estado_selecionado.sigla.lower()}"
            label_gerar = f"📊 Gerar CSV — Estado {self.estado_selecionado.sigla}"
            label_baixar = f"📥 CSV - Estado {self.estado_selecionado.sigla}"
            regiao_id = self.regiao_selecionada.id if self.regiao_selecionada else None
            gerar_fn = lambda: exportador_service.gerar_dados_estados(regiao_id)

        elif nivel == "N2" and self.regiao_selecionada:
            cache_key = f"regiao_{self.regiao_selecionada.id}"
            nome_arquivo = f"dados_regiao_{self.regiao_selecionada.sigla.lower()}"
            label_gerar = f"📊 Gerar CSV — Região {self.regiao_selecionada.nome}"
            label_baixar = f"📥 CSV - Região {self.regiao_selecionada.nome}"
            regiao_id = self.regiao_selecionada.id
            gerar_fn = lambda: exportador_service.gerar_dados_estados(regiao_id)

        else:
            cache_key = "brasil_todos_municipios"
            nome_arquivo = "dados_todos_municipios_brasil"
            label_gerar = "📊 Gerar CSV — Todos os municípios do Brasil"
            label_baixar = "📥 CSV - Todos os municípios"
            gerar_fn = lambda: exportador_service.gerar_dados_todos_municipios()

        session_key = f"export_df_{cache_key}"

        if session_key not in st.session_state:
            gerar_clicado = st.sidebar.button(
                label_gerar, use_container_width=True, key=f"gerar_{cache_key}"
            )
            if not gerar_clicado:
                st.sidebar.caption("Clique para gerar o arquivo (pode levar alguns segundos).")
                return

            with st.sidebar:
                with st.spinner("Gerando arquivo..."):
                    try:
                        st.session_state[session_key] = gerar_fn()
                    except Exception as e:
                        st.sidebar.error(f"❌ Erro ao gerar dados: {str(e)[:100]}")
                        return

        df = st.session_state.get(session_key)

        if df is None or df.empty:
            st.sidebar.info("ℹ️ Sem dados disponíveis para exportar")
            return

        csv_data = exportador_service.exportar_para_csv(df)

        with st.sidebar.container():
            st.download_button(
                label=label_baixar,
                data=csv_data,
                file_name=f"{nome_arquivo}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"sidebar_export_{cache_key}"
            )
            st.caption(f"📊 {len(df):,} registros")
    
    def _render_linkedin_footer(self):
        """Renderiza o rodapé com logo do LinkedIn centralizado"""
        linkedin_url = "https://www.linkedin.com/in/rodrigoaiosa/"
        
        st.sidebar.markdown(
            f"""
            <div style="
                text-align: center; 
                padding: 16px 0 8px 0;
                margin-top: 8px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            ">
                <a href="{linkedin_url}" target="_blank" style="
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    opacity: 0.7;
                ">
                    <div style="
                        width: 52px;
                        height: 52px;
                        margin: 0 auto 8px auto;
                        background: #0A66C2;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: all 0.4s ease;
                        color: white;
                        font-size: 28px;
                        font-weight: 700;
                        font-family: 'Helvetica', 'Arial', sans-serif;
                    ">
                        in
                    </div>
                    <div style="
                        color: #EAF2EE;
                        font-size: 14px;
                        font-weight: 600;
                        letter-spacing: 0.3px;
                    ">
                        Rodrigo Aiôsa
                    </div>
                    <div style="
                        color: #EAF2EE;
                        font-size: 11px;
                        opacity: 0.5;
                        margin-top: 3px;
                        letter-spacing: 0.2px;
                    ">
                        linkedin.com/in/rodrigoaiosa
                    </div>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _determinar_nivel(self) -> str:
        """Determina o nível territorial baseado nas seleções"""
        if self.municipio_selecionado:
            return "N6"
        elif self.estado_selecionado:
            return "N3"
        elif self.regiao_selecionada:
            return "N2"
        else:
            return "N1"
    
    def _determinar_codigo(self) -> int:
        """Determina o código IBGE baseado nas seleções"""
        if self.municipio_selecionado:
            return self.municipio_selecionado.id
        elif self.estado_selecionado:
            return self.estado_selecionado.id
        elif self.regiao_selecionada:
            return self.regiao_selecionada.id
        else:
            return 1
    
    def _get_breadcrumb(self) -> str:
        """Monta o breadcrumb para display"""
        if self.municipio_selecionado:
            regiao_nome = self.estado_selecionado.regiao.nome if self.estado_selecionado.regiao else ""
            return f"{regiao_nome} · {self.estado_selecionado.sigla} · {self.municipio_selecionado.nome}"
        elif self.estado_selecionado:
            regiao_nome = self.estado_selecionado.regiao.nome if self.estado_selecionado.regiao else ""
            return f"{regiao_nome} · {self.estado_selecionado.nome}"
        elif self.regiao_selecionada:
            return f"Região {self.regiao_selecionada.nome}"
        else:
            return "Visão nacional"
    
    def _get_nome_local(self) -> str:
        """Retorna o nome da localidade selecionada"""
        if self.municipio_selecionado:
            return self.municipio_selecionado.nome
        elif self.estado_selecionado:
            return f'{self.estado_selecionado.nome} ({self.estado_selecionado.sigla})'
        elif self.regiao_selecionada:
            return self.regiao_selecionada.nome
        else:
            return "Brasil"


# Instância global
sidebar_filters = SidebarFilters()
