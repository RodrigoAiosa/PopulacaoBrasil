from src.utils.formatters import (
    fmt_int,
    fmt_dec,
    fmt_porcentagem,
    fmt_habitantes,
    fmt_posicao,
    formatar_texto_plural,
)


def test_fmt_int_none_retorna_travessao():
    assert fmt_int(None) == "—"


def test_fmt_int_usa_ponto_como_separador_de_milhar():
    assert fmt_int(1_234_567) == "1.234.567"


def test_fmt_dec_usa_virgula_decimal():
    assert fmt_dec(1234.5, casas=1) == "1.234,5"


def test_fmt_dec_none_retorna_travessao():
    assert fmt_dec(None) == "—"


def test_fmt_porcentagem():
    assert fmt_porcentagem(12.3) == "12,3%"


def test_fmt_habitantes_milhoes():
    assert fmt_habitantes(2_500_000) == "2.5 mi"


def test_fmt_habitantes_mil():
    assert fmt_habitantes(1_500) == "1.5 mil"


def test_fmt_habitantes_abaixo_de_mil_usa_fmt_int():
    assert fmt_habitantes(950) == "950"


def test_fmt_posicao_com_total():
    assert fmt_posicao(1, 27) == "1º de 27"


def test_fmt_posicao_none():
    assert fmt_posicao(None) == "—"


def test_formatar_texto_plural_singular():
    assert formatar_texto_plural(1, "município") == "município"


def test_formatar_texto_plural_plural_automatico():
    assert formatar_texto_plural(3, "município") == "municípios"


def test_formatar_texto_plural_irregular():
    assert formatar_texto_plural(2, "capital", "capitais") == "capitais"
