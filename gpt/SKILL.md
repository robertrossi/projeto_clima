---
name: projeto-clima-python-data-engineering
description: Regras permanentes para desenvolver, modificar, validar e documentar este projeto Python de engenharia de dados, incluindo uso de uv, arquitetura src, Ruff, pytest e MkDocs.
---

# Instruções do projeto Clima

Aplique estas instruções ao trabalhar neste repositório. O projeto é um aplicativo Python de engenharia de dados relacionado a clima, com nome de distribuição `projeto-clima`. Adapte as recomendações ao tamanho real do código; não crie estrutura ou ferramentas sem necessidade concreta.

## Sumário

- [Antes de alterar o projeto](#antes-de-alterar-o-projeto)
- [Python e dependências](#python-e-dependencias)
  - [Comandos uv](#comandos-uv)
- [Arquitetura e organização](#arquitetura-e-organizacao)
- [Qualidade com Ruff](#qualidade-com-ruff)
- [Testes com pytest](#testes-com-pytest)
- [Boas práticas de engenharia de dados](#boas-praticas-de-engenharia-de-dados)
- [Documentação](#documentacao)
- [Fluxo de trabalho e validação](#fluxo-de-trabalho-e-validacao)
  - [Critérios para concluir uma tarefa](#criterios-para-concluir-uma-tarefa)
- [Princípios](#principios)

## Antes de alterar o projeto

- Inspecione os arquivos e configurações existentes e entenda o objetivo da mudança.
- Preserve comportamento existente e faça alterações incrementais. Não reinicialize nem substitua arquivos de configuração sem necessidade.
- Antes de criar `src/`, `tests/`, `docs/`, `mkdocs.yml` ou outros componentes, verifique o que já existe e se a tarefa justifica sua introdução.
- Prefira a biblioteca padrão e dependências já declaradas. Explique escolhas técnicas relevantes e não invente resultados de comandos ou validações.

## Python e dependências

- Use **uv** para instalar e fixar versões do Python, gerenciar ambientes e dependências. Nunca gerencie pacotes usando `pip` diretamente e não introduza Poetry, Pipenv ou ferramentas concorrentes.
- Use `pyproject.toml` como configuração e declaração de dependências, e mantenha `uv.lock` reprodutível. Altere o lockfile por meio do uv, nunca manualmente, salvo exceção justificada.
- Execute Python e ferramentas do projeto preferencialmente com `uv run`.
- Fixe uma versão estável do Python compatível com `requires-python` e as dependências atuais. Não mude a faixa de compatibilidade sem motivo.

### Comandos uv

Execute os comandos pertinentes à etapa atual, a partir da raiz do repositório.

**Inicialização, somente para um projeto ainda não inicializado:**

```bash
uv init
uv python install 3.11
uv python pin 3.11
uv sync
uv run python --version
```

O repositório atual já possui `pyproject.toml`, `.python-version` e `hello.py`. Portanto, inspecione a configuração atual antes de considerar qualquer comando de inicialização ou pinagem. Não execute `uv init` sobre a estrutura existente.

**Dependências:**

```bash
uv add <pacote>          # dependência de produção
uv add --dev <pacote>    # ferramenta ou dependência de desenvolvimento
uv remove <pacote>       # remover dependência
uv sync                  # sincronizar o ambiente com o projeto
uv tree                  # visualizar a árvore de dependências
```

**Execução:**

```bash
uv run python -m <modulo_de_entrada>  # quando existir um módulo de entrada apropriado
uv run python <arquivo.py>            # quando o projeto adotar execução por script
uv run <ferramenta>                   # executar ferramenta declarada nas dependências
```

Use o módulo ou arquivo de entrada que realmente exista; não presuma que o nome de distribuição `projeto-clima` seja também um nome de módulo Python.

## Arquitetura e organização

- A estrutura atual é pequena: `hello.py`, `doc_api.md`, `README.md` e `pyproject.toml` ficam na raiz. Não presuma que diretórios de aplicação, testes ou documentação já existam.
- Conforme o código evoluir para uma aplicação, use a estrutura de referência abaixo. Crie somente os diretórios necessários à tarefa; não mova arquivos existentes nem crie módulos vazios para preencher a árvore.

```text
projeto_clima/
├── src/
│   └── projeto_clima/           # pacote Python (nome de importação)
│       ├── __init__.py
│       ├── __main__.py          # entrada via python -m, se adotada
│       ├── config.py            # configuração não secreta e leitura do ambiente
│       ├── clients/
│       │   └── open_meteo.py    # chamadas HTTP à API externa
│       ├── pipelines/           # coordenação de etapas de ingestão
│       ├── transformations/     # limpeza e transformação dos dados
│       └── storage/             # persistência, se necessária
├── tests/
│   ├── unit/                    # testes isolados e com serviços externos simulados
│   └── integration/             # testes que dependem de serviços/recursos externos
├── docs/                        # documentação detalhada do projeto
├── data/                        # dados locais gerados; não versionar dados volumosos
│   ├── raw/
│   ├── processed/
│   └── .gitkeep                 # opcional, se for preciso versionar diretórios vazios
├── pyproject.toml
├── uv.lock
├── mkdocs.yml                   # somente se MkDocs for configurado
├── README.md
├── .env.example                 # somente se houver configuração por variáveis de ambiente
└── .gitignore
```

- O nome de distribuição `projeto-clima` e o nome Python `projeto_clima` têm convenções diferentes. Confirme o nome de importação e configure o empacotamento em `pyproject.toml` ao introduzir `src/`.
- Mantenha `doc_api.md` onde está enquanto a estrutura atual não for reorganizada. Se a documentação passar a usar MkDocs, mova/adapte o conteúdo para `docs/` e atualize `mkdocs.yml` e a navegação na mesma mudança.
- Dados baixados, arquivos temporários, ambientes virtuais e segredos não devem ser adicionados ao controle de versão. Atualize `.gitignore` conforme os artefatos que o projeto realmente gerar.
- Separe aquisição externa, validação, transformação, regras de negócio e persistência quando isso melhorar a clareza e a testabilidade.
- Prefira funções pequenas e coesas, nomes claros e type hints nas interfaces relevantes. Evite duplicação, arquivos excessivamente grandes, abstrações prematuras e camadas sem benefício demonstrável.
- Mantenha claros os papéis de `src/` (código), `tests/` (testes), `docs/` (documentação), `data/` (artefatos locais), `pyproject.toml` (metadados, dependências e ferramentas), `uv.lock` (resolução reproduzível) e `mkdocs.yml` (configuração do site, se usado).

## Qualidade com Ruff

Configure Ruff em `pyproject.toml` se ele fizer parte da configuração acordada do projeto. Use-o para lint, formatação e imports. Não desabilite regras indiscriminadamente nem confunda formatar com verificar lint.

```bash
uv run ruff check .
uv run ruff check --fix .       # apenas quando as correções automáticas forem seguras
uv run ruff format .
uv run ruff format --check .
```

## Testes com pytest

- Coloque testes unitários em `tests/unit/` e testes de integração em `tests/integration/`, espelhando, quando útil, os módulos de `src/`. Use nomes `test_*.py` e funções `test_*` descobríveis pelo pytest.
- Toda mudança que introduza ou altere comportamento deve trazer ou atualizar testes unitários para esse comportamento. Cubra pelo menos o caminho de sucesso, validações/erros esperados e casos de borda relevantes para a mudança; não adicione casos irrelevantes só para aumentar a contagem.
- Testes unitários devem ser determinísticos, rápidos e independentes de rede, credenciais, relógio real ou estado compartilhado. Isole APIs e serviços externos com mocks/fakes; não faça chamadas reais à Open-Meteo nos testes unitários.
- Para o cliente da API, quando aplicável, cubra parâmetros e parsing da resposta, status HTTP de erro, timeout e resposta inválida. Para transformações, cubra dados válidos, ausências, duplicidades, tipos incorretos e limites relevantes. Teste apenas cenários pertinentes às funções existentes.
- Testes de integração verificam a interação entre componentes ou serviços reais. Separe-os dos unitários e documente pré-requisitos, variáveis de ambiente e como executá-los; não os torne dependentes de segredo ou serviço indisponível para a execução unitária padrão.
- A cobertura mínima é **50% do código de produção relevante**, calculada pelo `pytest-cov` sobre o pacote da aplicação. Considere o total da aplicação coberta, não apenas os módulos fáceis; não omita módulos importantes da medição nem reduza a qualidade dos testes para alcançar o percentual. Configure `fail_under = 50` no `pyproject.toml` quando a configuração de cobertura estiver estabelecida.
- Não escreva testes que apenas reproduzam a implementação. Verifique resultados, efeitos e erros observáveis. Corrija testes que falhem por regressões; não altere expectativas sem confirmar o comportamento desejado.

```bash
uv run pytest
uv run pytest --cov=<nome_do_pacote> --cov-report=term-missing
```

Substitua `<nome_do_pacote>` pelo nome de importação real. Para tornar o mínimo de cobertura um bloqueio da execução, use `--cov-fail-under=50` ou configure `fail_under = 50` em `[tool.coverage.report]` no `pyproject.toml`. Se pytest ou pytest-cov ainda não estiverem declarados e a tarefa incluir código/testes, adicione-os como dependências de desenvolvimento com `uv add --dev pytest pytest-cov` e sincronize com `uv sync`.

## Boas práticas de engenharia de dados

- Valide dados na entrada e trate explicitamente valores ausentes, duplicidades, tipos incorretos e inconsistências.
- Mantenha aquisição, transformação, validação e persistência separadas quando necessário para facilitar manutenção e testes.
- Para chamadas externas, defina timeouts e trate erros; implemente retentativas limitadas com backoff apenas quando fizer sentido.
- Não inclua credenciais, tokens ou senhas no código. Use variáveis de ambiente e forneça `.env.example` quando a configuração exigir segredos.
- Prefira processamento incremental para volumes grandes quando adequado. Registre eventos úteis com logging, sem usar `print()` como mecanismo principal de log da aplicação.
- Torne as transformações previsíveis, reproduzíveis e testáveis.

## Documentação

- Se o projeto usar MkDocs, mantenha a documentação em `docs/` e configure navegação e tema em `mkdocs.yml`; use MkDocs Material conforme a convenção solicitada para este projeto.
- Documente objetivo, instalação, configuração, execução, arquitetura, dependências externas e exemplos. Mantenha `README.md` com visão geral e instruções rápidas, sem duplicar toda a documentação detalhada.
- Mantenha comandos documentados alinhados à configuração real do repositório.

```bash
uv run mkdocs serve  # visualizar localmente durante a edição
uv run mkdocs build  # validar e gerar a documentação
```

## Fluxo de trabalho e validação

1. Entenda o pedido e inspecione a estrutura atual antes de editar.
2. Faça a menor mudança completa e coerente; atualize configuração, lockfile e documentação afetados.
3. Execute `uv sync` se o ambiente precisar ser sincronizado.
4. Antes de concluir uma mudança de código, execute as verificações pertinentes abaixo; não inicialize ferramentas ou componentes que ainda não estejam configurados sem avaliar e documentar essa decisão.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pytest --cov=<nome_do_pacote> --cov-report=term-missing
uv run mkdocs build
```

Execute verificações conforme o escopo: mudanças de código exigem testes unitários e lint/formatação configurados; mudanças em documentação exigem revisão dos links/comandos e build MkDocs se configurado; mudanças de dependências exigem sincronização; alterações amplas exigem a suíte completa. Verificações indisponíveis por falta de ferramenta não contam como aprovadas. Se uma ferramenta necessária à mudança não estiver configurada, configure-a como parte do trabalho quando isso for proporcional, ou informe claramente o bloqueio e a razão. Investigue falhas relacionadas à mudança e não repita a configuração inicial do projeto a cada tarefa.

Ao concluir, informe os arquivos alterados, os comandos executados e o resultado real das verificações. Declare limitações relevantes com clareza.

### Critérios para concluir uma tarefa

Considere a tarefa validada somente quando os critérios aplicáveis abaixo forem atendidos:

1. **Requisito:** a mudança atende ao pedido e preserva o comportamento não relacionado; entradas inválidas e casos de borda relevantes são tratados.
2. **Código:** `uv run ruff check .` e `uv run ruff format --check .` passam quando Ruff estiver configurado. Corrija problemas introduzidos pela mudança; não use formatação como substituto de lint.
3. **Testes unitários e cobertura:** mudanças que adicionem ou alterem comportamento da aplicação incluem testes unitários determinísticos para sucesso, validação/erros e casos de borda pertinentes. Testes unitários não acessam serviços externos; use mocks/fakes. Execute `uv run pytest`. Para código da aplicação, execute a medição com `pytest-cov` sobre o pacote real e confirme pelo menos 50% de cobertura do código de produção relevante. Não exclua módulos importantes da medição. Se pytest/pytest-cov não estiverem configurados, adicione-os como dependências de desenvolvimento quando a tarefa envolver código e valide a configuração. Testes de integração são adicionais quando necessários para validar uma interação real e devem documentar seus pré-requisitos.
4. **Documentação:** atualize a documentação afetada e execute `uv run mkdocs build` quando MkDocs estiver configurado. Comandos e exemplos documentados devem corresponder ao projeto.
5. **Dependências e ambiente:** se dependências ou metadados mudarem, mantenha `pyproject.toml` e `uv.lock` sincronizados via uv; `uv sync` deve concluir sem erro.
6. **Relato:** informe o que foi alterado, os comandos realmente executados e seus resultados. Identifique verificações não aplicáveis ou bloqueadas e explique o motivo; não declare aprovação sem execução.

Não crie testes, dependências ou ferramentas só para marcar itens como concluídos. Se um critério obrigatório para a mudança falhar, investigue e corrija antes de finalizar; se não for possível, descreva claramente a falha e o que falta.

## Princípios

Priorize legibilidade, simplicidade, modularidade proporcional, reprodutibilidade, testabilidade e manutenção. Siga PEP 8 e convenções modernas de Python, preserve funcionalidades existentes e explique limitações de soluções necessárias. A rapidez de geração não substitui entendimento e validação.
