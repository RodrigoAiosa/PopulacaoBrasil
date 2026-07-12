from src.models.schemas import Regiao, Estado, Municipio, IndicadorDemografico, RankingItem


def test_regiao_from_api():
    regiao = Regiao.from_api({"id": 3, "nome": "Sudeste", "sigla": "SE"})
    assert regiao == Regiao(id=3, nome="Sudeste", sigla="SE")


def test_estado_from_api_com_regiao_aninhada():
    data = {
        "id": 35,
        "nome": "São Paulo",
        "sigla": "SP",
        "regiao": {"id": 3, "nome": "Sudeste", "sigla": "SE"},
    }
    estado = Estado.from_api(data)
    assert estado.sigla == "SP"
    assert estado.regiao.nome == "Sudeste"


def test_estado_from_api_sem_regiao():
    data = {"id": 35, "nome": "São Paulo", "sigla": "SP"}
    estado = Estado.from_api(data)
    assert estado.regiao is None


def test_municipio_from_api():
    municipio = Municipio.from_api({"id": 3550308, "nome": "São Paulo"})
    assert municipio.id == 3550308
    assert municipio.microrregiao is None


def test_indicador_populacao_formatada_com_valor():
    ind = IndicadorDemografico(populacao=1_234_567)
    assert ind.populacao_formatada == "1.234.567"


def test_indicador_populacao_formatada_sem_valor():
    ind = IndicadorDemografico()
    assert ind.populacao_formatada == "—"


def test_indicador_pib_total_formatado_bilhoes():
    ind = IndicadorDemografico(pib_total=2_500_000_000)
    assert ind.pib_total_formatado == "R$ 2.50 bi"


def test_indicador_idhm_faixa_muito_alto():
    ind = IndicadorDemografico(idhm=0.850)
    assert ind.idhm_faixa == "Muito alto"


def test_indicador_idhm_faixa_baixo():
    ind = IndicadorDemografico(idhm=0.550)
    assert ind.idhm_faixa == "Baixo"


def test_indicador_idhm_faixa_sem_valor():
    ind = IndicadorDemografico()
    assert ind.idhm_faixa == ""


def test_ranking_item_populacao_formatada():
    item = RankingItem(nome="São Paulo", populacao=12_396_372)
    assert item.populacao_formatada == "12.396.372"


def test_ranking_item_renda_per_capita_sem_valor():
    item = RankingItem(nome="São Paulo", populacao=12_396_372)
    assert item.renda_per_capita_formatada == "—"
