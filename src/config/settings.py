"""
Configurações globais do projeto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configurações da API
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 15))
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", 3))

# Cache TTL (em segundos)
CACHE_TTL_LOCALIDADES = 60 * 60 * 24  # 24 horas
CACHE_TTL_AGREGADOS = 60 * 60 * 6     # 6 horas
CACHE_TTL_MALHAS = 60 * 60 * 24       # 24 horas

# Configurações do mapa
MAP_CENTER_LAT = float(os.getenv("MAP_CENTER_LAT", -15.0))
MAP_CENTER_LON = float(os.getenv("MAP_CENTER_LON", -55.0))
MAP_ZOOM_START = int(os.getenv("MAP_ZOOM_START", 4))
MAP_HEIGHT = int(os.getenv("MAP_HEIGHT", 520))

# Configurações de UI
UI_MAX_ITEMS_RANKING = int(os.getenv("UI_MAX_ITEMS_RANKING", 10))

# Caminho do CSV local (opcional) com IDHM por município.
# Formato esperado: colunas codigo_ibge,idhm,ano
# Veja src/services/idhm.py para detalhes de como obter/gerar esse arquivo.
DATA_IDHM_MUNICIPIOS_PATH = os.getenv(
    "DATA_IDHM_MUNICIPIOS_PATH",
    str(BASE_DIR / "data" / "idhm_municipios.csv")
)
