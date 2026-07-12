"""
Componente de botão para exportação de dados
"""
import streamlit as st
from typing import Optional

from src.services.exportador import exportador_service
from src.models.schemas import Estado, Regiao


def render_export_button(
    estado: Optional[Estado] = None,
    regiao: Optional[Regiao] = None,
    nivel: str = "N1"
):
    """
    Renderiza botão de exportação com base no nível selecionado
    """
    # Determinar o tipo de dados a exportar
    if nivel == "N6" and estado:
        # Nível município - dados dos municípios do estado
        df = exportador_service.gerar_dados_municipios_estado(estado.id)
        nome_arquivo = f"dados_municipios_{estado.sigla.lower()}"
        descricao = f"Municípios do estado {estado.nome} ({len(df)} registros)"
    
    elif nivel == "N3" and estado:
        # Nível estado - dados do estado
        df = exportador_service.gerar_dados_estados(regiao.id if regiao else None)
        nome_arquivo = f"dados_estado_{estado.sigla.lower()}"
        descricao = f"Dados do estado {estado.nome}"
    
    elif nivel == "N2" and regiao:
        # Nível região - dados dos estados da região
        df = exportador_service.gerar_dados_estados(regiao.id)
        nome_arquivo = f"dados_regiao_{regiao.sigla.lower()}"
        descricao = f"Estados da região {regiao.nome} ({len(df)} registros)"
    
    else:
        # Nível Brasil - dados de TODOS os municípios
        df = exportador_service.gerar_dados_todos_municipios()
        nome_arquivo = "dados_todos_municipios_brasil"
        descricao = f"Todos os municípios do Brasil ({len(df)} registros)"
    
    # Verificar se há dados
    if df.empty:
        st.info("ℹ️ Nenhum dado disponível para exportação.")
        return
    
    # Criar container para os botões
    with st.container():
        st.markdown("#### 📊 Exportar dados")
        
        # Criar colunas para os botões
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Botão CSV
            csv_data = exportador_service.exportar_para_csv(df)
            st.download_button(
                label="📄 Baixar CSV",
                data=csv_data,
                file_name=f"{nome_arquivo}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"csv_{nome_arquivo}"
            )
        
        with col2:
            # Botão Excel (com fallback)
            try:
                excel_data = exportador_service.exportar_para_excel(df)
                st.download_button(
                    label="📊 Baixar Excel",
                    data=excel_data,
                    file_name=f"{nome_arquivo}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"excel_{nome_arquivo}"
                )
            except ImportError:
                st.warning("⚠️ Biblioteca 'openpyxl' não encontrada. Use o formato CSV.")
            except Exception:
                st.warning("⚠️ Exportação para Excel indisponível. Use o formato CSV.")
        
        with col3:
            # Informação de quantos registros
            st.caption(f"📊 {descricao}")
            
            # Prévia dos dados
            with st.expander("👁️ Ver prévia dos dados"):
                st.dataframe(
                    df.head(10),
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"Mostrando 10 de {len(df)} registros")
