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
        regiao_nome_sel = st.sidebar.selectbox("Região", regiao_nomes)
        
        if regiao_nome_sel != FILTER_OPTIONS["todas_regioes"]:
            self.regiao_selecionada = next(
                r for r in self.regioes if r.nome == regiao_nome_sel
            )
        
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
            [FILTER_OPTIONS["todos_estados"]] + estado_labels
        )
        
        if estado_label_sel != FILTER_OPTIONS["todos_estados"]:
            idx = estado_labels.index(estado_label_sel)
            self.estado_selecionado = self.estados[idx]
        
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
                [FILTER_OPTIONS["todos_municipios"]] + municipio_nomes
            )
            
            if municipio_nome_sel != FILTER_OPTIONS["todos_municipios"]:
                self.municipio_selecionado = next(
                    m for m in self.municipios if m.nome == municipio_nome_sel
                )
        else:
            st.sidebar.selectbox(
                "Cidade / Município",
                ["Selecione um estado primeiro"],
                disabled=True
            )
        
        # Status de conexão
        if self._connection_error:
            st.sidebar.warning("📡 Modo offline - dados limitados")
        
        # Rodapé da sidebar
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
