# Plano de criação do Projeto Clima

Este plano organiza um dashboard Streamlit que compara temperaturas em localidades configuráveis, com filtros geográficos e consulta por data. As instruções de desenvolvimento estão em [SKILL.md](SKILL.md); os parâmetros e particularidades das APIs estão resumidos em [doc_api.md](doc_api.md).

## Sumário

- [Objetivo](#objetivo)
- [Escopo da primeira versão](#escopo-da-primeira-versao)
- [Regras para o ranking](#regras-para-o-ranking)
- [Arquitetura proposta](#arquitetura-proposta)
- [Estrutura de diretórios](#estrutura-de-diretorios)
- [Fases de implementação](#fases-de-implementacao)
- [Estratégia de testes e qualidade](#estrategia-de-testes-e-qualidade)
- [Critérios de aceite](#criterios-de-aceite)
- [Fora do escopo inicial](#fora-do-escopo-inicial)
- [Referências](#referencias)

## Objetivo

Criar um dashboard Streamlit executável localmente que compare as cinco maiores temperaturas entre localidades do catálogo, filtradas por país e estado/região. Permitir consultar condições atuais ou a máxima diária de uma data selecionada, usando previsão para hoje e datas futuras e reanálise para datas passadas.

## Escopo da primeira versão

### Incluído

- Criar uma interface Streamlit com ação explícita para consultar/atualizar os dados.
- Ler a lista de localizações de um CSV configurável, contendo ao menos nome, latitude e longitude. Não fixar nomes nem coordenadas no código. Incluir um pequeno arquivo de exemplo documentado, sem alegar cobertura geográfica completa.
- Aceitar `country` e `state` como colunas opcionais do catálogo e oferecer filtros por esses campos; localidades sem metadados continuam disponíveis quando o filtro correspondente está em “Todos”.
- Consultar `GET https://api.open-meteo.com/v1/forecast` usando `current=temperature_2m`, `temperature_unit=celsius` e `timezone=auto` para resolver o fuso de cada localidade; permitir configurar essas opções se necessário.
- Permitir selecionar uma data. Para hoje e datas futuras, consultar `daily=temperature_2m_max` na Forecast API (horizonte de até 16 dias); para datas passadas, consultar a mesma variável no endpoint de arquivo histórico, baseado em reanálise e com disponibilidade dependente da variável/modelo.
- Comparar a máxima do dia local de cada localidade e informar que dias locais em fusos diferentes não correspondem necessariamente ao mesmo período UTC.
- Enviar coordenadas em lote quando apropriado e suportado pela API, mantendo a associação correta entre cada resposta e sua localidade. Tratar respostas como objeto único ou lista, conforme o número de coordenadas.
- Validar catálogo e estrutura da resposta antes de calcular o ranking.
- Apresentar as cinco localidades de maior temperatura, com nome, coordenadas, temperatura, unidade e horário/fuso do dado; permitir inspecionar outras localidades consultadas.
- Exibir estado de carregamento, horário da consulta e mensagens claras para arquivo inválido, falha de rede, timeout, erro HTTP ou ausência de dados.
- Usar cache do Streamlit somente com validade curta e ação visível para atualizar, evitando resultados antigos sem indicação.
- Preservar a resposta JSON original em `data/raw/` e os resultados em `data/processed/` se a auditoria/reprodutibilidade justificar. A consulta do dashboard não deve depender de persistência, salvo decisão posterior explícita.
- Registrar eventos operacionais com logging, sem expor segredos nem despejar respostas completas desnecessariamente.

### Regras dos dados exibidos

- Solicitar e identificar explicitamente a unidade. Usar Celsius por padrão e comparar apenas valores na mesma unidade.
- Respeitar datas locais e fusos retornados; não reconstruir horários ignorando `utc_offset_seconds`.
- Não substituir valores ausentes por zero. Indicar quantos registros foram ignorados e por quê.
- Guardar, quando disponíveis, tanto as coordenadas solicitadas quanto as coordenadas da célula de grade retornadas pela API.
- Se os timestamps entre localidades divergirem significativamente, sinalizar isso para que o ranking não sugira medições simultâneas exatas.
- Em consultas por data, identificar se o resultado é previsão ou reanálise histórica; não apresentar reanálise como observação direta de estação.

## Regras para o ranking

- Considerar temperatura do ar a 2 m: `current.temperature_2m` no modo atual ou `daily.temperature_2m_max` na data selecionada. Não misturar máxima diária com temperatura horária ou sensação térmica.
- Ordenar da maior temperatura para a menor e exibir até cinco localidades. Se houver menos de cinco registros válidos, exibir todos e informar a quantidade.
- Resolver empates de forma determinística: temperatura decrescente e, em seguida, nome da localidade em ordem alfabética. Exibir exatamente cinco resultados quando existirem pelo menos cinco localidades válidas.
- Excluir temperaturas ausentes, inválidas ou não numéricas do ranking e indicar a exclusão; nunca converter tais valores em zero.
- Exibir a data local associada à máxima diária e o fuso de cada localidade; explicar que dias locais em fusos diferentes podem cobrir períodos UTC distintos. Mostrar também o horário de atualização da consulta.

## Arquitetura proposta

Usar o pacote Python `projeto_clima` dentro de `src/`, confirmando e configurando o empacotamento em `pyproject.toml`. Manter a lógica de consulta e ranking independente do Streamlit.

- **Interface Streamlit:** carregar a lista de localidades, filtrar por país/estado, selecionar período ou data, oferecer atualização e apresentar ranking e metadados.
- **Configuração/entrada:** ler e validar catálogo, caminho, metadados geográficos opcionais, fuso e unidade.
- **Cliente Open-Meteo:** consultar condições atuais, máxima diária prevista ou máxima diária histórica com timeout e tratamento de erros HTTP, de rede e resposta.
- **Validação e ranking:** verificar catálogo e resposta, associar cada retorno à localidade, normalizar unidade/timestamp, ordenar e selecionar top 5.
- **Persistência opcional:** gravar JSON bruto e resultados processados se for necessário auditar; manter essa camada desacoplada para não bloquear o dashboard.
- **Serviço de consulta:** coordenar as etapas sem depender de componentes Streamlit, permitindo testes unitários isolados.

Usar Streamlit para a interface e começar com a biblioteca padrão para HTTP e CSV se atender aos requisitos. Adicionar dependências somente quando houver benefício claro. Credenciais não são necessárias para o uso comum; não armazenar chaves no código. Não introduzir banco de dados, orquestrador ou serviço web próprio na primeira versão.

## Estrutura de diretórios

Criar gradualmente a estrutura abaixo, somente conforme cada fase precisar dos diretórios. Não recriar nem mover arquivos existentes sem necessidade.

```text
projeto_clima/
├── src/
│   └── projeto_clima/
│       ├── __init__.py
│       ├── app.py                 # interface Streamlit
│       ├── config.py
│       ├── clients/
│       │   └── open_meteo.py
│       ├── services/
│       │   └── ranking.py         # consulta, associação e top 5
│       ├── transformations/
│       │   └── forecast.py
│       └── storage/
│           ├── locations.py       # leitura/validação do catálogo
│           └── files.py           # persistência opcional
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── index.md
│   ├── architecture.md
│   └── api.md
├── config/
│   └── locations.example.csv      # catálogo de exemplo
├── data/
│   ├── raw/
│   └── processed/
├── gpt/
│   ├── SKILL.md
│   ├── doc_api.md
│   └── PLAN.md
├── pyproject.toml
├── uv.lock
├── mkdocs.yml
├── README.md
└── .gitignore
```

A estrutura é uma referência, não uma lista de diretórios obrigatórios. Evitar duplicar lógica entre a interface e os serviços. Dados gerados, segredos, ambientes virtuais e arquivos temporários devem ser ignorados pelo Git. Versionar apenas exemplos pequenos e não sensíveis.

## Fases de implementação

### Fase 1 — Preparar a base do projeto

- Inspecionar `pyproject.toml`, `.python-version`, `.gitignore`, `README.md` e scripts atuais.
- Preservar configuração existente e confirmar compatibilidade da versão Python antes de alterá-la.
- Configurar empacotamento `src/` para `projeto_clima` e comandos de execução coerentes.
- Adicionar Streamlit como dependência de produção e Ruff, pytest e pytest-cov como dependências de desenvolvimento, se ainda não configurados.
- Configurar Ruff e cobertura no `pyproject.toml`, com cobertura mínima de 50% do pacote de produção.
- Sincronizar com `uv sync` e manter `uv.lock` gerado pelo uv.

**Conclusão da fase:** pacote instalável, Streamlit e ferramentas de qualidade configurados e comandos básicos registrados no README.

### Fase 2 — Implementar catálogo e cliente da API

- Definir o esquema do catálogo CSV: nome, latitude e longitude obrigatórios; país e estado/região opcionais. Validar campos ausentes, duplicidades e limites válidos das coordenadas.
- Montar a consulta para `current=temperature_2m`, `temperature_unit=celsius` e `timezone=auto`; preservar metadados de fuso/offset de cada localidade.
- Montar consultas diárias com `start_date`, `end_date`, `daily=temperature_2m_max` e `timezone=auto`; usar `/v1/forecast` para hoje/futuro e `/v1/archive` para datas passadas.
- Consultar várias coordenadas em lote quando apropriado e verificar a estrutura JSON de retorno para múltiplas localizações.
- Definir timeout e mensagens úteis para falhas de rede, erros HTTP e respostas malformadas.
- Não implementar repetição ilimitada. Se houver retentativa, limitar tentativas e usar backoff.

**Conclusão da fase:** localidades e respostas são validadas e o cliente pode ser testado sem chamadas reais à API.

### Fase 3 — Calcular o ranking

- Associar cada objeto retornado à localidade correta.
- Validar presença e tipo de `current.temperature_2m` ou `daily.temperature_2m_max`, data, unidade e coordenadas retornadas.
- Excluir temperaturas inválidas com diagnóstico; nunca preencher ausências com zero.
- Ordenar por temperatura decrescente e nome crescente como desempate; selecionar até cinco registros.
- Manter a função/serviço de ranking independente do Streamlit.

**Conclusão da fase:** ranking determinístico com metadados e exclusões explicáveis, coberto por testes com respostas de exemplo.

### Fase 4 — Construir o dashboard

- Criar página Streamlit com título, contexto, seleção/caminho do catálogo, filtros por país/estado, modo atual ou data, botão de atualização e horário da consulta.
- Destacar top 5 com temperatura e mostrar tabela de apoio com demais localidades, unidade, data local/fuso e estado do dado.
- Mostrar localidades inválidas/sem resposta em diagnóstico sem interromper os resultados válidos.
- Exibir estados de carregamento, erro recuperável e ausência de resultados.
- Aplicar cache com validade curta e oferecer atualização explícita.
- Persistir JSON/CSV apenas se habilitado/configurado; se persistência for opcional e falhar, informar sem impedir a consulta válida.

**Conclusão da fase:** dashboard executa localmente, consulta o catálogo, apresenta ranking correto e comunica estados relevantes.

### Fase 5 — Documentar e finalizar

- Atualizar README com instalação via uv, execução do Streamlit, localização/configuração do catálogo, filtros e seleção de data.
- Documentar como informar país/estado no CSV, regras do ranking, unidades, timestamps, diferenças entre previsão e reanálise e limitações temporais/geográficas.
- Manter `docs/api.md` como referência de uso da API e `gpt/doc_api.md` como notas detalhadas de consulta.
- Configurar MkDocs Material e tarefas Taskipy para servir e compilar a documentação.
- Rodar validações finais, corrigir falhas e registrar resultados reais.

**Conclusão da fase:** documentação compila e uma nova pessoa consegue configurar o catálogo e abrir o dashboard seguindo as instruções.

## Estratégia de testes e qualidade

- **Unitários (`tests/unit/`):** testar validação do catálogo e metadados opcionais, parâmetros dos endpoints de previsão/arquivo, parsing, erros HTTP/timeout, extração de máxima diária, ranking e comportamento para resposta incompleta.
- **Ranking:** cobrir ordenação, empate na quinta posição, menos de cinco localidades, valores ausentes/inválidos, unidades e timestamps divergentes entre fusos.
- **Mocks:** simular HTTP nos testes unitários. Nenhuma chamada real à Open-Meteo deve ocorrer na suíte unitária padrão.
- **Interface:** testar funções independentes da interface; testar componentes Streamlit apenas quando isso trouxer valor observável.
- **Integração (`tests/integration/`):** opcional, para interação real com a API. Deve ser explicitamente acionada, tolerar indisponibilidade externa e documentar pré-requisitos.
- **Cobertura:** medir todo o pacote de produção com pytest-cov e manter pelo menos 50%; não excluir módulos relevantes para atingir o limite.
- **Qualidade:** executar `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`, `uv run pytest --cov=projeto_clima --cov-report=term-missing --cov-fail-under=50` e `uv run mkdocs build` quando as respectivas ferramentas estiverem configuradas.
- **Ambiente:** validar `uv sync` quando dependências ou metadados mudarem. Não declarar verificações como aprovadas sem executá-las.

## Critérios de aceite

- [ ] Dashboard Streamlit inicia pelo comando documentado e apresenta estados de carregamento, erro e consulta concluída.
- [ ] Catálogo configurável contém nome, latitude e longitude; país e estado/região são opcionais; problemas são apontados claramente.
- [ ] Requisição usa `/v1/forecast`, `current=temperature_2m`, `temperature_unit=celsius` e `timezone=auto` (ou configuração equivalente documentada).
- [ ] Respostas de múltiplas coordenadas são associadas às localidades corretas.
- [ ] Top 5 considera a temperatura atual no modo Agora e a máxima diária na data selecionada, nunca a sensação térmica, com ordem decrescente e desempate determinístico.
- [ ] Menos de cinco localidades válidas e dados sem temperatura válida são tratados e informados corretamente.
- [ ] Interface exibe localidade, temperatura, unidade, data local/fuso do dado e horário da consulta.
- [ ] Timeout, erro HTTP, falha de rede e JSON inválido resultam em mensagens acionáveis sem derrubar a aplicação.
- [ ] Cache tem validade curta e pode ser atualizado explicitamente.
- [ ] Filtros de país e estado/região funcionam com os metadados presentes no catálogo.
- [ ] A data selecionada usa máxima diária da previsão para hoje/futuro até 16 dias e do arquivo histórico para passado, identificando o tipo de dado e tratando valores ausentes.
- [ ] Persistência, se habilitada, preserva timestamps e metadados e não é requisito para abrir o dashboard.
- [ ] Testes unitários não usam rede, cobrem comportamentos relevantes e passam.
- [ ] Cobertura do código de produção é de pelo menos 50%; Ruff lint/formatação passam; MkDocs compila; dependências estão sincronizadas.
- [ ] README/documentação explicam setup, execução, catálogo, regra do ranking, saídas e limitações.
- [ ] Nenhum segredo ou dado volumoso indevido foi adicionado ao Git.

## Fora do escopo inicial

- Login, perfis, alertas e notificações.
- Histórico persistente, gráficos temporais ou tendências.
- Banco de dados, data warehouse, cloud storage ou infraestrutura em nuvem.
- Agendamento automático, Airflow/Prefect ou execução distribuída.
- Busca geográfica e inclusão automática de novas cidades via Geocoding API; os filtros iniciais operam sobre metadados fornecidos no catálogo.
- Previsão de modelos meteorológicos específicos.
- Garantia de disponibilidade ou precisão além dos dados e limites informados pelo Open-Meteo.

## Referências

- [Instruções de desenvolvimento do projeto](SKILL.md)
- [Resumo da Forecast API](doc_api.md)
- [Documentação oficial Open-Meteo](https://open-meteo.com/en/docs)
- [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Geocoding API](https://open-meteo.com/en/docs/geocoding-api)
