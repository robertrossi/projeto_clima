# API meteorológica

O projeto usa a [Open-Meteo Forecast API](https://open-meteo.com/en/docs) para condições atuais
e previsão, e a [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
para máximas diárias históricas. As consultas são feitas a partir das coordenadas do catálogo.

## Consultas do projeto

| Modo | Endpoint | Dado solicitado |
| --- | --- | --- |
| Agora | `/v1/forecast` | `current=temperature_2m` |
| Data atual ou futura | `/v1/forecast` | `daily=temperature_2m_max` |
| Data passada | `/v1/archive` | `daily=temperature_2m_max` |

As requisições usam Celsius e `timezone=auto`. No modo Data, o intervalo enviado corresponde à
data selecionada. A previsão diária está disponível até o limite suportado pela API (16 dias).
O histórico é baseado em reanálises e não equivale necessariamente à observação de uma estação.

## Limites e geografia

A API não descobre nem enumera todas as cidades para o dashboard. A [Geocoding API](https://open-meteo.com/en/docs/geocoding-api)
permite pesquisar globalmente nomes de cidades e códigos postais e retorna coordenadas e metadados;
o cadastro automático por busca ainda não faz parte desta aplicação.

País e estado/região são metadados opcionais do CSV e filtrados localmente. Assim, a abrangência
geográfica da comparação depende dos locais incluídos no catálogo.

## Referência

Para parâmetros e variáveis atualizados, consulte a [documentação oficial da Forecast API](https://open-meteo.com/en/docs),
a [Geocoding API](https://open-meteo.com/en/docs/geocoding-api) e a [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).
