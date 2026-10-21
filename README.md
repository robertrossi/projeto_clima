# Projeto Clima

[![CI](https://github.com/robertrossi/projeto_clima/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/robertrossi/projeto_clima/actions/workflows/ci.yml)

Dashboard Streamlit que compara temperaturas do ar a 2 m para localidades de um catálogo configurável, com filtros por país/estado e consultas atuais, futuras e históricas.

## Acessar sem instalar

Abra o [dashboard Projeto Clima](https://projetoclima-lj2xvqbpqynq2whnvojjuk.streamlit.app/) no navegador, sem instalar Python ou dependências localmente. O app está hospedado no [Streamlit Community Cloud](https://streamlit.io/cloud).

Para publicar, entre no Community Cloud com GitHub, escolha **Create app** e informe:

- Repositório: `robertrossi/projeto_clima`
- Branch: `main`
- Arquivo principal: `src/projeto_clima/app.py`
- Versão do Python: `3.12`

Envie o código para o GitHub antes de publicar. O repositório inclui `uv.lock` para declarar as dependências. Consulte o [guia oficial de implantação](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). O app só fica acessível pelo navegador depois que a implantação for concluída.

## Clonar o projeto

Com Git instalado, clone o repositório e entre na pasta:

```powershell
git clone https://github.com/robertrossi/projeto_clima.git
cd projeto_clima
```

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

## Estrutura do projeto

```text
projeto_clima/
├── config/
│   └── locations.example.csv   # catálogo de exemplo
├── docs/                       # documentação do MkDocs
│   ├── api.md
│   ├── arquitetura.md
│   ├── desenvolvimento.md
│   ├── index.md
│   └── uso.md
├── gpt/                        # plano e notas de desenvolvimento
│   ├── PLAN.md
│   ├── SKILL.md
│   └── doc_api.md
├── src/projeto_clima/
│   ├── __init__.py
│   ├── app.py                  # interface Streamlit
│   ├── clients/
│   │   ├── __init__.py
│   │   └── open_meteo.py       # cliente da API Open-Meteo
│   ├── services/
│   │   ├── __init__.py
│   │   └── ranking.py          # transformação e ranking
│   └── storage/
│       ├── __init__.py
│       └── locations.py        # leitura e validação do CSV
├── tests/unit/
│   ├── test_locations.py
│   ├── test_open_meteo.py
│   └── test_ranking.py
├── .gitignore
├── .python-version
├── mkdocs.yml                  # configuração da documentação
├── pyproject.toml              # dependências e ferramentas
├── uv.lock                     # versões resolvidas pelo uv
└── README.md
```

## Desenvolvimento

O GitHub Actions executa lint, verificação de formatação, testes com cobertura mínima de 50% e build do MkDocs em pushes à `main`/`feat/**`, pull requests para `main` e execuções manuais na aba **Actions**.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pytest --cov=projeto_clima --cov-report=term-missing --cov-fail-under=50
uv run task docs
uv run task docs-build
```

## Documentação do site

Depois da primeira publicação, a documentação também estará disponível em [robertrossi.github.io/projeto_clima](https://robertrossi.github.io/projeto_clima/). O workflow `deploy-docs.yml` publica automaticamente a documentação quando há alterações na branch `main`.

Com MkDocs Material e Taskipy instalados no grupo de desenvolvimento:

```bash
uv run task docs
```

O comando inicia a pré-visualização local em [http://127.0.0.1:8001](http://127.0.0.1:8001). Deixe o terminal aberto enquanto usa o site. Para validar ou gerar o site estático em `site/`:

```bash
uv run task docs-build
```

A página inicial está em `docs/index.md`; consulte também `docs/api.md`.
