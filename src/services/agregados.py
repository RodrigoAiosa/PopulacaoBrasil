@staticmethod
def get_renda_per_capita(nivel: str, codigo: int, periodo: str = "-1") -> Optional[float]:
    """
    Obtém o PIB per capita (renda) para uma localidade.
    Agregado: 5964 - PIB per capita
    Variável: 38 - PIB per capita (R$)
    """
    try:
        # Buscar PIB per capita
        localidade = f"{nivel}[{codigo}]"
        data = _fetch_valor_agregado(
            Agregados.RENDA_PER_CAPITA,
            Variaveis.PIB_PER_CAPITA,
            localidade,
            periodo
        )
        
        if not data:
            return None
        
        series = data[0]["resultados"][0]["series"]
        if not series:
            return None
        
        serie = series[0]["serie"]
        if not serie:
            return None
        
        ultimo_periodo = sorted(serie.keys())[-1]
        valor_bruto = serie[ultimo_periodo]
        
        if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
            return None
        
        try:
            # Remove pontos de milhar e substitui vírgula por ponto
            clean_value = str(valor_bruto).replace(".", "").replace(",", ".")
            return float(clean_value)
        except (ValueError, TypeError):
            return None
            
    except Exception as e:
        st.warning(f"⚠️ Erro ao obter PIB per capita: {str(e)}")
        return None

@staticmethod
def get_pib_total(nivel: str, codigo: int, periodo: str = "-1") -> Optional[float]:
    """
    Obtém o PIB total (em R$ 1.000) para uma localidade.
    Agregado: 5938 - PIB dos Municípios
    Variável: 37 - PIB total (R$ 1.000)
    """
    try:
        localidade = f"{nivel}[{codigo}]"
        data = _fetch_valor_agregado(
            Agregados.PIB_MUNICIPIOS,
            Variaveis.PIB_TOTAL,
            localidade,
            periodo
        )
        
        if not data:
            return None
        
        series = data[0]["resultados"][0]["series"]
        if not series:
            return None
        
        serie = series[0]["serie"]
        if not serie:
            return None
        
        ultimo_periodo = sorted(serie.keys())[-1]
        valor_bruto = serie[ultimo_periodo]
        
        if valor_bruto is None or str(valor_bruto) in SIDRA_INVALID_SYMBOLS:
            return None
        
        try:
            # Remove pontos de milhar e substitui vírgula por ponto
            clean_value = str(valor_bruto).replace(".", "").replace(",", ".")
            # Valor está em R$ 1.000
            return float(clean_value) * 1000
        except (ValueError, TypeError):
            return None
            
    except Exception as e:
        st.warning(f"⚠️ Erro ao obter PIB total: {str(e)}")
        return None
