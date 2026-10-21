# Desenvolvimento e validação

## Ambiente

Requisitos: Python `>=3.11.5,<3.13` e uv. Na raiz do repositório:

```powershell
uv sync
```

As dependências de desenvolvimento do grupo `dev` são sincronizadas por padrão. O projeto usa
`src/` layout e o pacote é `projeto_clima`.

## Tarefas Taskipy

| Comando | Ação |
| --- | --- |
| `uv run task docs` | Serve a documentação local em `http://127.0.0.1:8001` com recarga automática. |
| `uv run task docs-build` | Compila o site estático para `site/`. |
| `uv run task test` | Executa a suíte pytest em `tests/`. |
| `uv run task lint` | Executa `ruff check .`. |
| `uv run task format` | Formata arquivos com Ruff. |

Verificações diretas equivalentes:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pytest --cov=projeto_clima --cov-report=term-missing --cov-fail-under=50
uv run mkdocs build
```

## Organização dos testes

| Arquivo | Escopo |
| --- | --- |
| `tests/unit/test_locations.py` | CSV válido/inválido, metadados opcionais, duplicatas e filtros. |
| `tests/unit/test_open_meteo.py` | Parâmetros e endpoints, erros de rede/HTTP/timeout, JSON e quantidade de respostas. |
| `tests/unit/test_ranking.py` | Ordenação, desempate, dados inválidos, timestamps e máxima diária. |

Os testes unitários substituem `urlopen` por respostas simuladas; não precisam chamar a API real.
O limite de cobertura definido no `pyproject.toml` é 50% do pacote de produção.

## Integração contínua no GitHub

O workflow `.github/workflows/ci.yml` roda em `ubuntu-latest` quando há push para `main` ou
`feat/**`, em pull requests direcionados a `main` e quando iniciado manualmente pela aba **Actions**.
Ele instala Python 3.12 e uv 0.13.4, sincroniza o `uv.lock` sem alterá-lo e executa lint, checagem
de formatação, testes com cobertura mínima de 50% e build do MkDocs. Não usa segredos nem depende
de chamadas reais à API meteorológica.

## Documentação

`mkdocs.yml` define Material, idioma, extensões e navegação. As páginas publicadas ficam em `docs/`;
`gpt/PLAN.md`, `gpt/SKILL.md` e `gpt/doc_api.md` são arquivos de planejamento/notas mantidos fora
do site publicado.
