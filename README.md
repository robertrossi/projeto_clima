# Projeto Clima

Dashboard Streamlit que compara temperaturas do ar a 2 m para localidades de um catálogo configurável, com filtros por país/estado e consultas atuais, futuras e históricas.

## Requisitos e execução

Requer Python 3.11.5–3.12 e [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run streamlit run src/projeto_clima/app.py
```

O painel usa `config/locations.example.csv` por padrão. Copie-o para outro CSV se quiser adaptar sua lista e informe o caminho na barra lateral. O CSV deve ser UTF-8, separado por vírgulas, com colunas `name`, `latitude` e `longitude`; `country` e `state` são opcionais e alimentam os filtros geográficos. Coordenadas devem estar nos limites WGS84. O mesmo nome pode aparecer em regiões distintas; a combinação nome/país/estado não pode se repetir.

## Como funciona

O modo **Agora** envia as coordenadas em lote para `https://api.open-meteo.com/v1/forecast`, solicitando `current=temperature_2m`, Celsius e `timezone=auto`. Em **Data**, escolha o dia a comparar: o ranking usa `daily=temperature_2m_max`, a máxima diária do ar a 2 m. Hoje e datas futuras usam a previsão (até 16 dias); datas passadas usam `https://archive-api.open-meteo.com/v1/archive`, com reanálise histórica desde 1940 conforme a disponibilidade do conjunto de dados. A reanálise é baseada em modelos, não representa necessariamente uma observação direta de estação.

Cada máxima diária corresponde ao dia local da cidade. Por isso, cidades em fusos diferentes podem representar períodos UTC diferentes, mesmo quando a data no painel é a mesma. Só valores numéricos válidos participam do ranking; empates são resolvidos pelo nome em ordem alfabética. A tabela mostra data local, fuso, coordenadas solicitadas e da célula de grade, além de dados ignorados.

Os dados ficam em cache por 5 minutos; use **Atualizar agora** para forçar uma consulta. A aplicação não persiste respostas localmente. O catálogo de exemplo é pequeno e não representa cobertura geográfica completa. Consulte o [site de documentação](docs/index.md) e a referência de [uso da API](docs/api.md).

## Desenvolvimento

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pytest --cov=projeto_clima --cov-report=term-missing --cov-fail-under=50
uv run task docs
uv run task docs-build
```

## Documentação do site

Com MkDocs Material e Taskipy instalados no grupo de desenvolvimento:

```bash
uv run task docs
```

O comando inicia a pré-visualização local. Para validar ou gerar o site estático em `site/`:

```bash
uv run task docs-build
```

A página inicial está em `docs/index.md`; consulte também `docs/api.md`.
