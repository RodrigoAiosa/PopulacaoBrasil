"""
URLs e constantes das APIs do IBGE
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class APIEndpoints:
    """URLs base das APIs do IBGE"""
    BASE_LOC = "https://servicodados.ibge.gov.br/api/v1/localidades"
    BASE_AGG = "https://servicodados.ibge.gov.br/api/v3/agregados"
    BASE_MALHA = "https://servicodados.ibge.gov.br/api/v3/malhas"
    
    # Subrotas
    REGIOES = "/regioes"
    ESTADOS = "/estados"
    MUNICIPIOS = "/municipios"
    METADADOS = "/metadados"
    PERIODOS = "/periodos"
    VARIAVEIS = "/variaveis"
    
    @classmethod
    def get_regioes_url(cls):
        return f"{cls.BASE_LOC}{cls.REGIOES}"
    
    @classmethod
    def get_estados_url(cls, regiao_id: int = None):
        if regiao_id:
            return f"{cls.BASE_LOC}{cls.REGIOES}/{regiao_id}{cls.ESTADOS}"
        return f"{cls.BASE_LOC}{cls.ESTADOS}"
    
    @classmethod
    def get_municipios_url(cls, uf_id: int):
        return f"{cls.BASE_LOC}{cls.ESTADOS}/{uf_id}{cls.MUNICIPIOS}"
    
    @classmethod
    def get_agregado_metadados_url(cls, agregado_id: int):
        return f"{cls.BASE_AGG}/{agregado_id}{cls.METADADOS}"
    
    @classmethod
    def get_agregado_valor_url(cls, agregado_id: int, variavel_id: int, periodo: str = "-1"):
        return f"{cls.BASE_AGG}/{agregado_id}{cls.PERIODOS}/{periodo}{cls.VARIAVEIS}/{variavel_id}"
    
    @classmethod
    def get_malha_url(cls, localidade: str = "BR"):
        return f"{cls.BASE_MALHA}/{localidade}"


@dataclass(frozen=True)
class Agregados:
    """IDs dos agregados do SIDRA"""
    POPULACAO_ESTIMADA = 6579
    CENSO_AREA_DENSIDADE = 4714


@dataclass(frozen=True)
class Variaveis:
    """IDs das variáveis dos agregados"""
    POPULACAO_ESTIMADA = 9324
    
    # Nomes para busca dinâmica
    AREA = "Área"
    DENSIDADE = "Densidade"


@dataclass(frozen=True)
class NiveisTerritoriais:
    """Níveis territoriais da API"""
    BRASIL = "N1"
    REGIAO = "N2"
    ESTADO = "N3"
    MUNICIPIO = "N6"
    
    # Mapeamento para display
    DISPLAY = {
        "N1": "Brasil",
        "N2": "Região",
        "N3": "Estado",
        "N6": "Município"
    }


# Símbolos que representam dados inválidos no SIDRA
SIDRA_INVALID_SYMBOLS = {"-", "..", "...", "X", ""}
