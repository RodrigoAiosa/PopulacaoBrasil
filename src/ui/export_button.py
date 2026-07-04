"""
Componente de botão para exportação de dados
"""
import streamlit as st
import pandas as pd
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
        df = exportador_service.gerar_dados_municipios(estado.id)
        nome_arquivo = f"dados_municipios_{estado.sigla.lower()}"
        label = f"📥 Baixar dados dos municípios de {estado.sigla}"
        descricao = f"Municípios do estado {estado.nome}"
    elif nivel == "N3" and estado:
        # Nível estado - dados do estado
        df = exportador_service.gerar_dados_estados(regiao.id if regiao else None)
        nome_arquivo = f"dados_estado_{estado.sigla.lower()}"
        label = f"📥 Baixar dados do estado {estado.sigla}"
        descricao = f"Dados do estado {estado.nome}"
    elif nivel == "N2" and regiao:
        # Nível região - dados dos estados da região
        df = exportador_service.gerar_dados_estados(regiao.id)
        nome_arquivo = f"dados_regiao_{regiao.sigla.lower()}"
        label = f"📥 Baixar dados da região {regiao.nome}"
        descricao = f"Estados da região {regiao.nome}"
    else:
        # Nível Brasil - dados de todos os estados
        df = exportador_service.gerar_dados_brasil()
        nome_arquivo = "dados_brasil"
        label = "📥 Baixar dados do Brasil"
        descricao = "Todos os estados do Brasil"
    
    # Verificar se há dados
    if df.empty:
        st.info("ℹ️ Nenhum dado disponível para exportação.")
        return
    
    # Criar colunas para os botões
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Botão CSV
        csv_data = exportador_service.exportar_para_csv(df)
        st.download_button(
            label="📄 CSV",
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
                label="📊 Excel",
                data=excel_data,
                file_name=f"{nome_arquivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key=f"excel_{nome_arquivo}"
            )
        except Exception as e:
            # Se falhar, mostrar mensagem e oferecer apenas CSV
            st.warning("⚠️ Exportação para Excel indisponível. Use o formato CSV.")
    
    with col3:
        # Informação de quantos registros
        st.caption(f"📊 {len(df)} registros | {descricao}")
