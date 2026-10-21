# Arquitetura

O código de produção está em `src/projeto_clima`. A interface Streamlit coordena o carregamento do
catálogo, os filtros, a consulta e a apresentação; leitura CSV, HTTP e ranking ficam em módulos
separados para poderem ser testados sem executar a interface ou acessar a rede.

## Fluxo de uma consulta

```text
CSV -> validação -> filtros -> cache/cliente HTTP -> normalização diária (se aplicável)
    -> associação por ordem -> validação e ranking -> métricas e tabela Streamlit
```

O catálogo é carregado antes da consulta. Após os filtros, as coordenadas são enviadas em listas
na mesma ordem das localidades. O cliente normaliza uma resposta JSON única ou uma lista para uma
lista de registros; o ranking associa cada registro à localidade correspondente por essa ordem.
Uma quantidade incompatível de respostas interrompe o processamento com erro.

## Módulos

| Módulo | Responsabilidade |
| --- | --- |
| `app.py` | Interface, filtros, seletor de período, cache de cinco minutos, mensagens, métricas e tabela. |
| `storage/locations.py` | Modelo `Location`, carregamento, validação e filtros do CSV. |
| `clients/open_meteo.py` | Parâmetros HTTP, escolha do endpoint e tratamento de falhas da Open-Meteo. |
| `services/ranking.py` | Extração da máxima diária, validação, metadados, avisos e ordenação do top 5. |

## Tratamento de dados e falhas

O ranking não converte ausência em zero; ignora temperaturas não numéricas, infinitas, ausentes ou
com unidades não suportadas e registra o estado na tabela. Os valores válidos são ordenados por
temperatura decrescente e nome crescente. A saída inclui até cinco itens, todos os resultados,
coordenadas da consulta/grade, hora ou data local, fuso e avisos.

O cliente tem timeout padrão de 15 segundos e converte HTTP, rede, timeout, JSON inválido ou
estrutura divergente em `OpenMeteoError`. A interface exibe a mensagem e para aquela execução,
sem encerrar o processo Streamlit. O cache de `st.cache_data` dura 300 segundos e o botão de
atualização limpa os dois caches.

## Dependências e arquivos de dados

Streamlit e a biblioteca padrão cobrem a aplicação. Testes, Ruff, MkDocs Material e Taskipy são
dependências de desenvolvimento no grupo `dev`. Não há banco de dados nem persistência das
respostas. O arquivo `config/locations.example.csv` é apenas uma lista inicial pequena.
