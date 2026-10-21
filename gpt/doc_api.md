# Open-Meteo Weather Forecast API — resumo

Resumo da [documentação oficial](https://open-meteo.com/en/docs), consultada em 21/10/2026. A página também reúne links para APIs históricas, marítimas, de qualidade do ar, geocodificação, elevação e outras.

## Visão geral

A API de previsão do tempo combina dados de modelos meteorológicos de serviços nacionais e escolhe automaticamente os modelos adequados à localização. A previsão padrão cobre 7 dias; é possível solicitar até 16. A resposta é JSON e pode incluir condições atuais, séries horárias e agregações diárias.

## Endpoint principal

```text
GET https://api.open-meteo.com/v1/forecast
```

### Exemplo

```text
https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&current=temperature_2m,relative_humidity_2m,precipitation&hourly=temperature_2m,precipitation_probability&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=America%2FSao_Paulo&forecast_days=3
```

Latitude e longitude são coordenadas WGS84. Longitudes a oeste de Greenwich, como as do Brasil, são negativas.

## Parâmetros mais usados

| Parâmetro | Uso |
| --- | --- |
| `latitude`, `longitude` | Coordenadas (obrigatórias). É possível enviar listas de coordenadas separadas por vírgulas. |
| `current` | Variáveis de condições atuais, por exemplo `temperature_2m` e `precipitation`. |
| `hourly` | Variáveis horárias, como temperatura, umidade, chuva, vento e nebulosidade. |
| `daily` | Agregações diárias, como temperaturas mínima/máxima, soma de precipitação, nascer e pôr do sol. Ao usar, informe `timezone`. |
| `forecast_days` | Dias de previsão: padrão 7, máximo 16. |
| `past_days` | Dias anteriores a incluir (0–92). |
| `start_date`, `end_date` | Intervalo por data (`YYYY-MM-DD`). Para históricos extensos, consulte a Historical Weather API. |
| `timezone` | Fuso horário IANA (por exemplo, `America/Sao_Paulo`) ou `auto` para inferir pelas coordenadas. Padrão `GMT`. |
| `temperature_unit` | `celsius` (padrão) ou `fahrenheit`. |
| `wind_speed_unit` | `kmh` (padrão), `ms`, `mph` ou `kn`. |
| `precipitation_unit` | `mm` (padrão) ou `inch`. |
| `timeformat` | `iso8601` (padrão) ou `unixtime`. |
| `models` | Seleciona modelo(s); por padrão usa a seleção automática (`auto`/Best Match). |
| `elevation` | Altitude em metros para ajuste estatístico; normalmente estimada automaticamente. |
| `cell_selection` | Escolha da célula de grade: `land` (padrão), `sea` ou `nearest`. |

Parâmetros como `forecast_hours`, `past_hours`, `forecast_minutely_15` e `past_minutely_15` controlam intervalos de dados horários ou de 15 minutos. A resolução de 15 minutos só é nativa em algumas regiões; em outras, os valores podem ser interpolados a partir de dados horários.

## Variáveis disponíveis

- **Atuais:** temperatura, sensação térmica, umidade, precipitação, código do tempo, pressão, nebulosidade e vento.
- **Horárias:** além das condições básicas, há probabilidade e tipos de precipitação, visibilidade, rajadas, radiação solar, evapotranspiração, variáveis de solo e níveis de pressão.
- **Diárias:** máximas/mínimas, precipitação acumulada, probabilidade de chuva, duração de sol e luz do dia, nascer/pôr do sol, vento máximo e índice UV.
- **15 minutos:** conjunto reduzido de temperatura, precipitação, vento e algumas variáveis adicionais, conforme a região.

Os nomes usados nos parâmetros são identificadores em inglês, como `temperature_2m`, `precipitation_probability`, `wind_speed_10m` e `weather_code`. Consulte a lista completa na documentação para identificar nomes e unidades de cada variável.

## Formato da resposta

A resposta contém metadados da localização e do fuso, além dos blocos solicitados:

```json
{
  "latitude": -23.55,
  "longitude": -46.63,
  "timezone": "America/Sao_Paulo",
  "current": { "time": "...", "temperature_2m": 22.1 },
  "hourly": { "time": ["..."], "temperature_2m": [22.1] },
  "hourly_units": { "temperature_2m": "°C" },
  "daily": { "time": ["..."], "temperature_2m_max": [27.0] },
  "daily_units": { "temperature_2m_max": "°C" }
}
```

Os arrays de valores acompanham um array `time`; os blocos `*_units` informam as unidades efetivamente retornadas. A API informa as coordenadas da célula de grade utilizada, que podem diferir um pouco das coordenadas solicitadas.

## Códigos meteorológicos

`weather_code` usa códigos WMO numéricos. Alguns exemplos: `0` céu limpo, `1–3` variações de nebulosidade, `45/48` nevoeiro, `51–57` garoa, `61–67` chuva, `71–77` neve, `80–86` pancadas e `95–99` tempestades. A aplicação deve converter os códigos em rótulos legíveis; nem todos os modelos informam granizo (`96` e `99`).

## Erros e cuidados de integração

- Parâmetros inválidos retornam HTTP `400` e um JSON com `error` e `reason`.
- Ao solicitar dados diários, sempre informe o fuso horário para que os limites do dia sejam interpretados corretamente.
- No formato ISO 8601, o deslocamento UTC retornado é fixado no momento da requisição; transições de horário de verão dentro do período não são aplicadas. Para horários locais sensíveis a DST, a documentação recomenda `timeformat=unixtime` e conversão no cliente usando o fuso retornado.
- Precipitação e algumas variáveis representam soma ou média do período anterior; nem todo valor é instantâneo.
- O uso comercial de recursos reservados exige chave e endpoint de cliente (`customer-`); consulte a página de preços/licença para os termos aplicáveis.

## Links oficiais

- [Documentação e construtor da Forecast API](https://open-meteo.com/en/docs)
- [Preços](https://open-meteo.com/en/pricing)
- [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Demais APIs Open-Meteo](https://open-meteo.com/en/docs)

## Geografia e consultas por data

- A Forecast API não filtra por país ou estado: recebe coordenadas WGS84 individuais ou em listas. O projeto guarda `country` e `state` opcionais no catálogo e aplica os filtros na interface.
- A [Geocoding API](https://open-meteo.com/en/docs/geocoding-api) pesquisa nomes de cidades/códigos postais e pode restringir por país (`countryCode`) ou qualificador administrativo de primeiro nível; retorna nome, país, admin1 e coordenadas. O dashboard ainda não cadastra cidades automaticamente.
- A Forecast API aceita variáveis horárias/diárias com `start_date`/`end_date` e prevê até 16 dias. O projeto usa `daily=temperature_2m_max` para comparar uma data inteira. A API também aceita dados passados recentes com `past_days` até 92 dias.
- Para datas passadas, a [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) usa reanálises, com cobertura de alguns conjuntos desde 1940. Esses valores são estimativas meteorológicas baseadas em modelos e observações, não necessariamente medições de uma estação local.
- A [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) arquiva previsões emitidas desde aproximadamente 2022. Ela responde à pergunta “o que a previsão indicava então?”, diferente da reanálise do tempo ocorrido.
