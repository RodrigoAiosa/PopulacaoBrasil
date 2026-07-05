"""
Sidebar com filtros em cascata
"""
import streamlit as st
from typing import Tuple, Optional, Dict, Any

from src.services.localidades import localidades_service
from src.services.exportador import exportador_service
from src.models.schemas import Regiao, Estado, Municipio
from src.utils.constants import FILTER_OPTIONS


class SidebarFilters:
    """
    Gerenciador dos filtros da sidebar
    """
    
    def __init__(self):
        self.regioes = []
        self.estados = []
        self.municipios = []
        
        self.regiao_selecionada: Optional[Regiao] = None
        self.estado_selecionado: Optional[Estado] = None
        self.municipio_selecionado: Optional[Municipio] = None
        
        self._connection_error = False
    
    def render(self) -> Dict[str, Any]:
        """
        Renderiza a sidebar com filtros e retorna seleções
        """
        st.sidebar.markdown("## 🗺️ Filtros")
        st.sidebar.caption("Região, Estado e Município (cidade) em cascata.")
        
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
        
        # Seletor de região
        regiao_nomes = [FILTER_OPTIONS["todas_regioes"]] + [r.nome for r in self.regioes]
        regiao_nome_sel = st.sidebar.selectbox(
            "Região", 
            regiao_nomes,
            key="regiao_select"
        )
        
        nova_regiao = None
        if regiao_nome_sel != FILTER_OPTIONS["todas_regioes"]:
            nova_regiao = next(
                r for r in self.regioes if r.nome == regiao_nome_sel
            )
        
        if self.regiao_selecionada != nova_regiao:
            self.regiao_selecionada = nova_regiao
            self.estado_selecionado = None
            self.municipio_selecionado = None
            st.rerun()
        
        # Seletor de estado
        try:
            self.estados = localidades_service.get_estados(
                self.regiao_selecionada.id if self.regiao_selecionada else None
            )
        except Exception as e:
            st.sidebar.warning(f"⚠️ Erro ao carregar estados: {str(e)[:100]}...")
            self.estados = []
        
        estado_labels = [
            f'{e.nome} ({e.sigla})' for e in self.estados
        ]
        
        estado_label_sel = st.sidebar.selectbox(
            "Estado",
            [FILTER_OPTIONS["todos_estados"]] + estado_labels,
            key="estado_select"
        )
        
        novo_estado = None
        if estado_label_sel != FILTER_OPTIONS["todos_estados"]:
            idx = estado_labels.index(estado_label_sel)
            novo_estado = self.estados[idx]
        
        if self.estado_selecionado != novo_estado:
            self.estado_selecionado = novo_estado
            self.municipio_selecionado = None
            if novo_estado is not None:
                st.rerun()
        
        # Seletor de município
        if self.estado_selecionado:
            try:
                self.municipios = localidades_service.get_municipios(
                    self.estado_selecionado.id
                )
            except Exception as e:
                st.sidebar.warning(f"⚠️ Erro ao carregar municípios: {str(e)[:100]}...")
                self.municipios = []
            
            municipio_nomes = [m.nome for m in self.municipios]
            municipio_nome_sel = st.sidebar.selectbox(
                "Cidade / Município",
                [FILTER_OPTIONS["todos_municipios"]] + municipio_nomes,
                key="municipio_select"
            )
            
            if municipio_nome_sel != FILTER_OPTIONS["todos_municipios"]:
                self.municipio_selecionado = next(
                    m for m in self.municipios if m.nome == municipio_nome_sel
                )
            else:
                self.municipio_selecionado = None
        else:
            st.sidebar.selectbox(
                "Cidade / Município",
                ["Selecione um estado primeiro"],
                disabled=True,
                key="municipio_disabled"
            )
            self.municipio_selecionado = None
        
        # Botão de exportação
        st.sidebar.markdown("---")
        self._render_export_button()
        
        # LinkedIn rodapé
        self._render_linkedin_footer()
        
        # Fonte dos dados
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
                        Rodrigo Aiosa
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
