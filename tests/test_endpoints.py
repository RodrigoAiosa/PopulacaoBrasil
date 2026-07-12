from src.api.endpoints import APIEndpoints, NiveisTerritoriais


def test_get_regioes_url():
    assert APIEndpoints.get_regioes_url() == (
        "https://servicodados.ibge.gov.br/api/v1/localidades/regioes"
    )


def test_get_estados_url_sem_regiao():
    assert APIEndpoints.get_estados_url() == (
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    )


def test_get_estados_url_com_regiao():
    url = APIEndpoints.get_estados_url(regiao_id=3)
    assert url == (
        "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/3/estados"
    )


def test_get_municipios_url():
    url = APIEndpoints.get_municipios_url(uf_id=35)
    assert url == (
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios"
    )


def test_get_agregado_valor_url():
    url = APIEndpoints.get_agregado_valor_url(6579, 9324, periodo="2022")
    assert url == (
        "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2022/variaveis/9324"
    )


def test_niveis_territoriais_display():
    assert NiveisTerritoriais.DISPLAY[NiveisTerritoriais.MUNICIPIO] == "Município"
