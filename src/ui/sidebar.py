"""
Sidebar com filtros em cascata
"""
import streamlit as st
from typing import Tuple, Optional, Dict, Any

from src.services.localidades import localidades_service
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
        self._ultima_regiao = None
        self._ultimo_estado = None
    
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
        
        # Verificar se a região mudou
        nova_regiao = None
        if regiao_nome_sel != FILTER_OPTIONS["todas_regioes"]:
            nova_regiao = next(
                r for r in self.regioes if r.nome == regiao_nome_sel
            )
        
        # Se a região mudou, resetar estado e município
        if self.regiao_selecionada != nova_regiao:
            self.regiao_selecionada = nova_regiao
            self.estado_selecionado = None
            self.municipio_selecionado = None
            # Forçar recarregamento da página para transição instantânea
            st.rerun()
        
        # Seletor de estado (atualizado com base na região)
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
        
        # Manter o estado selecionado se ainda estiver na lista
        estado_label_sel = st.sidebar.selectbox(
            "Estado",
            [FILTER_OPTIONS["todos_estados"]] + estado_labels,
            key="estado_select"
        )
        
        novo_estado = None
        if estado_label_sel != FILTER_OPTIONS["todos_estados"]:
            idx = estado_labels.index(estado_label_sel)
            novo_estado = self.estados[idx]
        
        # Se o estado mudou, resetar município
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
        
        # ==================== BOTÃO DE EXPORTAÇÃO ====================
        st.sidebar.markdown("---")
        self._render_export_button()
        # ============================================================
        
        # ==================== LINKEDIN RODAPÉ ====================
        st.sidebar.markdown("---")
        self._render_linkedin_footer()
        # ============================================================
        
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
        """
        Renderiza o botão de exportação na sidebar
        """
        from src.services.exportador import exportador_service
        from src.api.endpoints import NiveisTerritoriais
        
        st.sidebar.markdown("### 📊 Exportar Dados")
        st.sidebar.caption("Baixe os dados em CSV")
        
        # Determinar o tipo de dados a exportar
        nivel = self._determinar_nivel()
        
        if nivel == "N6" and self.estado_selecionado:
            # Nível município - dados dos municípios do estado
            df = exportador_service.gerar_dados_municipios_estado(self.estado_selecionado.id)
            nome_arquivo = f"dados_municipios_{self.estado_selecionado.sigla.lower()}"
            label = f"📥 CSV - Municípios de {self.estado_selecionado.sigla}"
        
        elif nivel == "N3" and self.estado_selecionado:
            # Nível estado - dados do estado
            df = exportador_service.gerar_dados_estados(self.regiao_selecionada.id if self.regiao_selecionada else None)
            nome_arquivo = f"dados_estado_{self.estado_selecionado.sigla.lower()}"
            label = f"📥 CSV - Estado {self.estado_selecionado.sigla}"
        
        elif nivel == "N2" and self.regiao_selecionada:
            # Nível região - dados dos estados da região
            df = exportador_service.gerar_dados_estados(self.regiao_selecionada.id)
            nome_arquivo = f"dados_regiao_{self.regiao_selecionada.sigla.lower()}"
            label = f"📥 CSV - Região {self.regiao_selecionada.nome}"
        
        else:
            # Nível Brasil - dados de TODOS os municípios
            df = exportador_service.gerar_dados_todos_municipios()
            nome_arquivo = "dados_todos_municipios_brasil"
            label = "📥 CSV - Todos os municípios"
        
        # Verificar se há dados
        if df.empty:
            st.sidebar.info("ℹ️ Sem dados disponíveis")
            return
        
        # Botão de download
        csv_data = exportador_service.exportar_para_csv(df)
        st.sidebar.download_button(
            label=label,
            data=csv_data,
            file_name=f"{nome_arquivo}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"sidebar_csv_{nome_arquivo}"
        )
        
        # Mostrar quantidade de registros
        st.sidebar.caption(f"📊 {len(df)} registros")
    
    def _render_linkedin_footer(self):
        """
        Renderiza o rodapé com logo do LinkedIn
        """
        linkedin_url = "https://www.linkedin.com/in/rodrigoaiosa/"
        
        # HTML com logo do LinkedIn
        linkedin_html = f"""
        <div style="text-align: center; padding: 10px 0;">
            <a href="{linkedin_url}" target="_blank" style="text-decoration: none;">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="#EAF2EE">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
                <br>
                <span style="color: #EAF2EE; font-size: 12px; opacity: 0.7;">Rodrigo Aiôsa</span>
            </a>
        </div>
        """
        
        st.sidebar.markdown(linkedin_html, unsafe_allow_html=True)
        
        # Versão alternativa com texto simples (caso o SVG não funcione)
        st.sidebar.markdown(
            f"""
            <div style="text-align: center; padding: 5px 0;">
                <a href="{linkedin_url}" target="_blank" style="color: #EAF2EE; text-decoration: none; font-size: 13px; opacity: 0.8;">
                    🔗 linkedin.com/in/rodrigoaiosa
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
            return 1  # Brasil
    
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
