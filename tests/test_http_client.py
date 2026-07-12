import requests

from src.api import http_client


def test_parse_sidra_value_none():
    assert http_client.parse_sidra_value(None, {"-", ".."}) is None


def test_parse_sidra_value_simbolo_invalido():
    assert http_client.parse_sidra_value("-", {"-", ".."}) is None


def test_parse_sidra_value_com_virgula():
    assert http_client.parse_sidra_value("1234,56", {"-"}) == 1234.56


def test_get_json_retorna_none_em_erro_http_sem_tentar_de_novo(mocker):
    resposta = mocker.Mock()
    resposta.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mocker.Mock(status_code=404)
    )
    mock_get = mocker.patch.object(http_client._session, "get", return_value=resposta)

    resultado = http_client.get_json("https://exemplo.invalido/recurso")

    assert resultado is None
    # Erro HTTP (404) não é transitório: não deve haver retry.
    assert mock_get.call_count == 1


def test_get_json_faz_retry_em_timeout_e_depois_funciona(mocker):
    resposta_ok = mocker.Mock()
    resposta_ok.raise_for_status.return_value = None
    resposta_ok.json.return_value = {"ok": True}

    mock_get = mocker.patch.object(
        http_client._session,
        "get",
        side_effect=[requests.exceptions.Timeout(), resposta_ok],
    )
    mocker.patch("time.sleep", return_value=None)

    resultado = http_client.get_json("https://exemplo.invalido/recurso")

    assert resultado == {"ok": True}
    assert mock_get.call_count == 2
