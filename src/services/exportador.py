"""
Serviço para exportação de dados em Excel/CSV
"""
import pandas as pd
from typing import List, Dict, Any
import streamlit as st
from io import BytesIO, StringIO

from src.services.localidades import localidades_service
from src.services.agregados import agregados_service
from src.api.endpoints import NiveisTerritoriais


class ExportadorService:
    """Serviço para exportação de dados demográficos"""
    
    @staticmethod
    def gerar_dados_municipios(estado_id: int) -> pd.DataFrame:
        """
        Gera dados completos dos municípios de um estado com percentuais
        """
        # Buscar dados
        municipios = localidades_service.get_municipios(estado_id)
        estado = localidades_service.get_estado_by_id(estado_id)
        
        if not municipios or not estado:
            return pd.DataFrame()
        
        # Buscar população de cada município
        dados = []
        for municipio in municipios:
            pop = agregados_service.get_valor_agregado(
                agregado_id=6579,  # População estimada
                variavel_id=9324,   # População residente
                nivel=NiveisTerritoriais.MUNICIPIO,
                codigo=municipio.id
            )
            
            if pop is not None:
                dados.append({
                    "municipio_id": municipio.id,
                    "municipio_nome": municipio.nome,
                    "populacao": pop
                })
        
        if not dados:
            return pd.DataFrame()
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Calcular totais
        total_geral = df["populacao"].sum()
        
        # Buscar população do estado e região para percentuais
        pop_estado = agregados_service.get_valor_agregado(
            agregado_id=6579,
            variavel_id=9324,
            nivel=NiveisTerritoriais.ESTADO,
            codigo=estado_id
        ) or total_geral
        
        # Buscar população da região
        regiao_id = estado.regiao.id if estado.regiao else None
        pop_regiao = None
        if regiao_id:
            pop_regiao = agregados_service.get_valor_agregado(
                agregado_id=6579,
                variavel_id=9324,
                nivel=NiveisTerritoriais.REGIAO,
                codigo=regiao_id
            )
        
        # Calcular percentuais
        df["% TOTAL GERAL POPULAÇÃO"] = (df["populacao"] / total_geral * 100).round(2)
        df["% TOTAL POPULAÇÃO POR REGIÃO"] = (df["populacao"] / pop_regiao * 100).round(2) if pop_regiao else 0
        df["% TOTAL POPULAÇÃO POR ESTADO"] = (df["populacao"] / pop_estado * 100).round(2)
        
        # Adicionar informações de região e estado
        df["REGIÃO"] = estado.regiao.nome if estado.regiao else ""
        df["ESTADO"] = estado.nome
        df["CIDADE"] = df["municipio_nome"]
        df["MUNICIPIO"] = df["municipio_nome"]
        
        # Reordenar colunas conforme solicitado
        colunas = [
            "REGIÃO",
            "ESTADO",
            "CIDADE",
            "MUNICIPIO",
            "POPULAÇÃO",
            "% TOTAL GERAL POPULAÇÃO",
            "% TOTAL POPULAÇÃO POR REGIÃO",
            "% TOTAL POPULAÇÃO POR ESTADO"
        ]
        
        # Garantir que todas as colunas existam
        for col in colunas:
            if col not in df.columns:
                df[col] = ""
        
        return df[colunas]
    
    @staticmethod
    def gerar_dados_estados(regiao_id: int = None) -> pd.DataFrame:
        """
        Gera dados dos estados (com ou sem filtro de região)
        """
        # Buscar estados
        estados = localidades_service.get_estados(regiao_id)
        
        if not estados:
            return pd.DataFrame()
        
        # Buscar população de cada estado
        dados = []
        for estado in estados:
            pop = agregados_service.get_valor_agregado(
                agregado_id=6579,
                variavel_id=9324,
                nivel=NiveisTerritoriais.ESTADO,
                codigo=estado.id
            )
            
            if pop is not None:
                dados.append({
                    "estado_id": estado.id,
                    "estado_nome": estado.nome,
                    "estado_sigla": estado.sigla,
                    "regiao_nome": estado.regiao.nome if estado.regiao else "",
                    "populacao": pop
                })
        
        if not dados:
            return pd.DataFrame()
        
        df = pd.DataFrame(dados)
        
        # Calcular totais
        total_geral = df["populacao"].sum()
        
        # Calcular percentuais por região
        df_regiao = df.groupby("regiao_nome")["populacao"].sum().reset_index()
        df_regiao.columns = ["regiao_nome", "populacao_regiao"]
        df = df.merge(df_regiao, on="regiao_nome", how="left")
        
        # Calcular percentuais
        df["% TOTAL GERAL POPULAÇÃO"] = (df["populacao"] / total_geral * 100).round(2)
        df["% TOTAL POPULAÇÃO POR REGIÃO"] = (df["populacao"] / df["populacao_regiao"] * 100).round(2)
        df["% TOTAL POPULAÇÃO POR ESTADO"] = 100.0  # Para estados, é 100% do próprio estado
        
        # Mapear colunas
        df["REGIÃO"] = df["regiao_nome"]
        df["ESTADO"] = df["estado_nome"]
        df["CIDADE"] = ""  # Sem cidade no nível estado
        df["MUNICIPIO"] = ""  # Sem município no nível estado
        df["POPULAÇÃO"] = df["populacao"]
        
        # Selecionar colunas
        colunas = [
            "REGIÃO",
            "ESTADO",
            "CIDADE",
            "MUNICIPIO",
            "POPULAÇÃO",
            "% TOTAL GERAL POPULAÇÃO",
            "% TOTAL POPULAÇÃO POR REGIÃO",
            "% TOTAL POPULAÇÃO POR ESTADO"
        ]
        
        return df[colunas]
    
    @staticmethod
    def gerar_dados_brasil() -> pd.DataFrame:
        """
        Gera dados do Brasil (todos os estados)
        """
        return ExportadorService.gerar_dados_estados()
    
    @staticmethod
    def exportar_para_csv(df: pd.DataFrame) -> BytesIO:
        """
        Exporta DataFrame para CSV
        """
        output = BytesIO()
        df.to_csv(output, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        output.seek(0)
        return output
    
    @staticmethod
    def exportar_para_excel(df: pd.DataFrame) -> BytesIO:
        """
        Exporta DataFrame para Excel com fallback para CSV se openpyxl não estiver disponível
        """
        try:
            # Tentar exportar para Excel
            from openpyxl.workbook import Workbook
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados')
                
                # Formatar colunas de percentual
                workbook = writer.book
                worksheet = writer.sheets['Dados']
                
                # Formatar colunas de percentual
                for idx, col in enumerate(df.columns):
                    if '%' in col:
                        col_letter = chr(65 + idx)  # A, B, C, ...
                        for row in range(2, len(df) + 2):
                            cell = f"{col_letter}{row}"
                            if worksheet[cell].value is not None:
                                worksheet[cell].number_format = '0.00%'
            
            output.seek(0)
            return output
            
        except ImportError:
            # Fallback: exportar como CSV e avisar o usuário
            st.warning("⚠️ Biblioteca 'openpyxl' não encontrada. Exportando como CSV.")
            return ExportadorService.exportar_para_csv(df)
        except Exception as e:
            # Em caso de erro, exportar como CSV
            st.warning(f"⚠️ Erro ao exportar para Excel: {str(e)}. Exportando como CSV.")
            return ExportadorService.exportar_para_csv(df)


# Instância global
exportador_service = ExportadorService()
