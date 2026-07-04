# Painel Demográfico do Brasil (IBGE)

Dashboard em Streamlit com indicadores de população por Região, Estado e
Município, usando exclusivamente APIs públicas e gratuitas do IBGE (sem
necessidade de chave de acesso):

- **Localidades** — regiões, estados e municípios
- **Agregados (SIDRA)** — estimativas de população (tabela 6579) e
  área/densidade do Censo 2022 (tabela 4714)
- **Malhas Geográficas** — contorno dos estados para o mapa

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`. Nenhuma variável de ambiente ou
chave de API é necessária.

## Estrutura

```
app.py             # tudo em um único arquivo: API, layout, CSS e lógica
requirements.txt
```

Optei por um arquivo único (em vez de um pacote `services/`) porque plataformas
de deploy como o Streamlit Community Cloud às vezes não versionam corretamente
subpastas/`__init__.py` vazios, o que gera `ModuleNotFoundError`. Um único
`app.py` elimina esse tipo de problema de import.

## Como funciona o filtro

O menu lateral funciona em cascata:

1. **Região** → filtra os estados disponíveis
2. **Estado** → filtra os municípios disponíveis
3. **Cidade / Município** → nível mais granular

Ao deixar um filtro em "todos", o painel mostra o indicador agregado daquele
nível (ex.: sem estado selecionado, mostra o total da região ou do Brasil).

## Observações

- As primeiras consultas podem demorar alguns segundos: os resultados ficam
  em cache (`st.cache_data`) por até 24h, então as próximas trocas de filtro
  são quase instantâneas.
- Os IDs de variável do agregado 4714 (área/densidade) são descobertos
  dinamicamente pelo nome, em vez de fixados no código — mais robusto a
  mudanças na numeração do SIDRA.
- Caso a API do IBGE esteja temporariamente instável, os cartões mostram
  "—" em vez de quebrar a página.
