@staticmethod
def get_indicadores_demograficos(nivel: str, codigo: int) -> IndicadorDemografico:
    """
    Obtém todos os indicadores demográficos para uma localidade
    """
    # População
    populacao = AgregadosService.get_valor_agregado(
        Agregados.POPULACAO_ESTIMADA,
        Variaveis.POPULACAO_ESTIMADA,
        nivel,
        codigo
    )
    
    # Área
    area_info = AgregadosService.find_variavel_id(
        Agregados.CENSO_AREA_DENSIDADE,
        Variaveis.AREA
    )
    area = None
    if area_info:
        area = AgregadosService.get_valor_agregado(
            Agregados.CENSO_AREA_DENSIDADE,
            area_info[0],
            nivel,
            codigo
        )
    
    # Densidade
    densidade_info = AgregadosService.find_variavel_id(
        Agregados.CENSO_AREA_DENSIDADE,
        Variaveis.DENSIDADE
    )
    densidade = None
    if densidade_info:
        densidade = AgregadosService.get_valor_agregado(
            Agregados.CENSO_AREA_DENSIDADE,
            densidade_info[0],
            nivel,
            codigo
        )
    
    # Renda per capita (PIB per capita) - apenas para municípios e estados
    pib_per_capita = None
    if nivel in [NiveisTerritoriais.MUNICIPIO, NiveisTerritoriais.ESTADO]:
        pib_per_capita = AgregadosService.get_renda_per_capita(nivel, codigo)
    
    # PIB total - apenas para municípios e estados
    pib_total = None
    if nivel in [NiveisTerritoriais.MUNICIPIO, NiveisTerritoriais.ESTADO]:
        pib_total = AgregadosService.get_pib_total(nivel, codigo)
    
    return IndicadorDemografico(
        populacao=populacao,
        area=area,
        densidade=densidade,
        pib_per_capita=pib_per_capita,
        pib_total=pib_total
    )
