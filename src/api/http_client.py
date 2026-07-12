"""
Cliente HTTP compartilhado para as APIs do IBGE.

Antes deste módulo, `localidades.py` e `agregados.py` reimplementavam,
cada um, o mesmo padrão de `requests.get(...) + try/except` em várias
funções `_fetch_*` — e o README já prometia "retries" para tornar o
consumo da API mais resiliente, mas nenhuma requisição de fato tentava
de novo em caso de timeout/erro de conexão.

Este módulo centraliza:
- uma única `requests.Session` reutilizada (evita reabrir conexão TCP/TLS
  a cada chamada);
- retentativa automática com backoff exponencial (via tenacity) apenas
  para falhas transitórias (timeout, erro de conexão) — erros HTTP como
  404 não são repetidos, pois repetir não muda o resultado;
- logging estruturado do que falhou, em vez de estourar o erro completo
  (com URL) diretamente na tela para o usuário final via `st.warning`.

Quem chama continua responsável por decidir o que fazer quando `get_json`
retorna `None` (usar dado de fallback, mostrar aviso resumido etc.) —
este módulo não sabe nada sobre Streamlit.
"""
import logging
from typing import Any, Dict, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config.settings import API_TIMEOUT, API_MAX_RETRIES

logger = logging.getLogger("populacao_brasil")

_session = requests.Session()
_session.headers.update({
    "User-Agent": "PainelDemograficoBrasil/1.0 (+https://github.com/RodrigoAiosa/PopulacaoBrasil)",
    "Accept": "application/json",
})

# Só faz sentido tentar de novo em falhas transitórias de rede/timeout.
# Um 404 ou um JSON malformado não vira diferente na segunda tentativa.
_ERROS_TRANSITORIOS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
)


@retry(
    retry=retry_if_exception_type(_ERROS_TRANSITORIOS),
    stop=stop_after_attempt(max(1, API_MAX_RETRIES)),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    reraise=True,
)
def _get_com_retry(url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    resp = _session.get(url, params=params, timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp


def get_json(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """
    Faz uma requisição GET com retentativa automática para falhas
    transitórias e retorna o corpo já decodificado como JSON.

    Em caso de falha definitiva (após esgotar as tentativas, ou erro HTTP
    não-transitório), loga o problema e retorna `None` — nunca lança
    exceção para quem chama, para manter o comportamento de fallback
    silencioso que o resto do app espera.
    """
    try:
        return _get_com_retry(url, params=params).json()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "desconhecido"
        logger.warning("Erro HTTP %s ao acessar %s", status, url)
        return None
    except requests.exceptions.RequestException as e:
        logger.warning("Falha ao acessar %s após retentativas: %s", url, e)
        return None
    except ValueError:
        # resp.json() falhou (corpo não é JSON válido)
        logger.warning("Resposta não é JSON válido: %s", url)
        return None


def parse_sidra_value(value: Any, invalid_symbols) -> Optional[float]:
    """
    Converte um valor bruto retornado pelo SIDRA para float, tratando os
    símbolos que representam dado ausente/indisponível (ex.: "-", "..", "X").
    """
    if value is None or str(value) in invalid_symbols:
        return None
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None
