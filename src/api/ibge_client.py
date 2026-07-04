"""
Cliente base para APIs do IBGE
"""
import requests
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import streamlit as st

from src.config.settings import API_TIMEOUT, API_MAX_RETRIES
from src.api.endpoints import SIDRA_INVALID_SYMBOLS


class IBGEClient:
    """Cliente HTTP para as APIs do IBGE com retry e cache"""
    
    def __init__(self):
        self.timeout = API_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "IBGE-Dashboard/1.0",
            "Accept": "application/json"
        })
    
    @retry(
        stop=stop_after_attempt(API_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _get_json(self, url: str, params: Optional[Dict] = None) -> Any:
        """
        Faz requisição GET e retorna JSON.
        Com retry automático em caso de falha.
        """
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao acessar API do IBGE: {str(e)}")
            raise
    
    @st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
    def get_json_cached(self, url: str, params: Optional[Dict] = None, ttl: int = 86400) -> Any:
        """
        Versão com cache do Streamlit para requisições GET.
        """
        return self._get_json(url, params)
    
    def parse_sidra_value(self, value: Any) -> Optional[float]:
        """
        Converte valor do SIDRA para float, tratando símbolos especiais.
        """
        if value is None or str(value) in SIDRA_INVALID_SYMBOLS:
            return None
        
        try:
            # Substitui vírgula por ponto para conversão
            clean_value = str(value).replace(",", ".")
            return float(clean_value)
        except (ValueError, TypeError):
            return None


# Instância global do cliente
ibge_client = IBGEClient()
