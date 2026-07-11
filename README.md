# 🗺️ Painel Demográfico do Brasil

Painel interativo construído com **Streamlit** para explorar dados demográficos do Brasil — população, área, densidade demográfica e IDHM — em diferentes níveis territoriais (Brasil, Região, Estado e Município), usando dados públicos do **IBGE**.

## ✨ Funcionalidades

- **Navegação em cascata** por Região → Estado → Município através da barra lateral.
- **Cards de indicadores** com população, área, densidade demográfica e um quarto indicador contextual (posição no ranking, número de municípios/estados, etc.).
- **Ranking** de municípios/estados por população, exibido como tabela (nível município/estado) ou gráfico de barras (nível região/Brasil), com destaque para o local selecionado.
- **Mapa interativo** (Folium) da população por estado, com destaque para a seleção atual.
- **Exportação de dados** em Excel/CSV, inclusive para todos os municípios do Brasil em uma única consulta otimizada.
- **IDHM** por município a partir de uma base local (CSV opcional).
- **Modo offline** com aviso ao usuário quando os dados completos da API não estão disponíveis.
- Cache de requisições e *retries* para tornar o consumo da API do IBGE mais resiliente.

## 🧱 Estrutura do projeto

```
PopulacaoBrasil/
├── app.py                     # Ponto de entrada da aplicação Streamlit
├── requirements.txt           # Dependências do projeto
├── .env                       # Variáveis de ambiente (configuráveis)
└── src/
    ├── api/                   # Cliente HTTP e endpoints da API do IBGE
    │   ├── endpoints.py
    │   └── ibge_client.py
    ├── config/
    │   └── settings.py        # Configurações globais (timeouts, cache, mapa, UI)
    ├── models/
    │   └── schemas.py         # Modelos de dados (Pydantic)
    ├── services/
    │   ├── agregados.py       # Indicadores demográficos e rankings (SIDRA)
    │   ├── localidades.py     # Regiões, estados e municípios
    │   ├── mapas.py           # Preparação de dados para o mapa
    │   ├── idhm.py            # Leitura do IDHM por município
    │   └── exportador.py      # Exportação de dados em Excel/CSV
    ├── ui/
    │   ├── sidebar.py         # Filtros (região/estado/município)
    │   ├── hero.py            # Cabeçalho com o local selecionado
    │   ├── cards.py           # Cards de indicadores
    │   ├── charts.py          # Gráfico e tabela de ranking
    │   ├── map_view.py        # Renderização do mapa
    │   ├── ranking_table.py
    │   ├── export_button.py
    │   ├── components.py
    │   └── css.py             # Estilos customizados
    └── utils/
        ├── constants.py       # Textos, cores e configs de UI
        └── formatters.py      # Formatação de números
```

## 🚀 Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/RodrigoAiosa/PopulacaoBrasil.git
cd PopulacaoBrasil
```

### 2. Criar um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente (opcional)

O arquivo `.env` já vem com valores padrão. Ajuste conforme necessário:

```env
# Configurações da API
API_TIMEOUT=15
API_MAX_RETRIES=3

# Configurações do mapa
MAP_CENTER_LAT=-15.0
MAP_CENTER_LON=-55.0
MAP_ZOOM_START=4
MAP_HEIGHT=520

# Configurações de UI
UI_MAX_ITEMS_RANKING=10
```

Para habilitar o IDHM por município, adicione a variável `DATA_IDHM_MUNICIPIOS_PATH` apontando para um CSV com as colunas `codigo_ibge,idhm,ano` (veja `src/services/idhm.py` para detalhes).

### 5. Rodar a aplicação

```bash
streamlit run app.py
```

O painel abrirá automaticamente no navegador, normalmente em `http://localhost:8501`.

## 🗃️ Fontes de dados

Os dados são obtidos das APIs públicas do IBGE:

- **API de Localidades** — regiões, estados e municípios.
- **API de Agregados (SIDRA)** — estimativas de população (tabela 6579) e área/densidade do Censo Demográfico 2022 (tabela 4714).
- **API de Malhas Geográficas** — geometrias para o mapa interativo.

## 🛠️ Tecnologias utilizadas

- [Streamlit](https://streamlit.io/) — interface web
- [Plotly](https://plotly.com/python/) — gráficos
- [Folium](https://python-visualization.github.io/folium/) / [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) — mapas interativos
- [Pandas](https://pandas.pydata.org/) — manipulação de dados
- [Pydantic](https://docs.pydantic.dev/) — validação de dados/modelos
- [Requests](https://requests.readthedocs.io/) + [Tenacity](https://tenacity.readthedocs.io/) — chamadas HTTP resilientes
- [OpenPyXL](https://openpyxl.readthedocs.io/) — exportação em Excel

## 📄 Licença

Este projeto utiliza dados públicos disponibilizados pelo IBGE. Consulte o repositório para informações sobre a licença de uso do código.
