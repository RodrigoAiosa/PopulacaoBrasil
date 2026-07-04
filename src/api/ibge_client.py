"""
Cliente base para APIs do IBGE com tratamento de erros robusto
"""
import requests
from typing import Dict, Any, Optional
import streamlit as st

from src.config.settings import API_TIMEOUT
from src.api.endpoints import SIDRA_INVALID_SYMBOLS


class IBGEClient:
    """Cliente HTTP para as APIs do IBGE com cache e fallback"""
    
    def __init__(self):
        self.timeout = API_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "IBGE-Dashboard/1.0",
            "Accept": "application/json"
        })
    
    def _get_json(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Faz requisição GET e retorna JSON.
        """
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Tempo limite excedido ao acessar: {url}")
            return None
        except requests.exceptions.ConnectionError:
            st.warning(f"🔌 Erro de conexão ao acessar: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.warning(f"📭 Recurso não encontrado: {url}")
                return None
            st.warning(f"⚠️ Erro HTTP {e.response.status_code}: {url}")
            return None
        except requests.exceptions.RequestException as e:
            st.warning(f"❌ Erro ao acessar API: {str(e)}")
            return None
    
    @st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
    def get_json_cached(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Versão com cache do Streamlit para requisições GET.
        Usa '_self' para evitar hashing do objeto.
        """
        # Criar uma instância temporária para a requisição
        temp_client = IBGEClient()
        return temp_client._get_json(url, params)
    
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
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API do IBGE
        """
        test_url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes"
        try:
            response = self.session.get(test_url, timeout=5)
            return response.status_code == 200
        except:
            return False


# Instância global do cliente
ibge_client = IBGEClient()


# Funções auxiliares para cache (evitam problemas de hashing)
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def get_json_cached_safe(url: str, params: Optional[Dict] = None) -> Optional[Any]:
    """
    Função segura para cache de requisições JSON.
    """
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "IBGE-Dashboard/1.0",
            "Accept": "application/json"
        })
        resp = session.get(url, params=params, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"⚠️ Erro na requisição: {str(e)}")
        return None
