# Usar o dashboard

## Iniciar

Na raiz do repositório, instale as dependências e inicie o Streamlit:

```powershell
uv sync
uv run streamlit run src/projeto_clima/app.py
```

O painel abre no navegador. A barra lateral controla o arquivo CSV, os filtros geográficos, o
período consultado e a atualização dos dados.

## Preparar o catálogo

O caminho padrão é `config/locations.example.csv`. Para usar sua própria lista, crie um CSV em
UTF-8 com cabeçalho e informe seu caminho no campo **Arquivo CSV**.

| Coluna | Obrigatória | Descrição |
| --- | --- | --- |
| `name` | Sim | Nome exibido. Não pode ficar vazio. |
| `latitude` | Sim | Latitude decimal WGS84, entre -90 e 90. |
| `longitude` | Sim | Longitude decimal WGS84, entre -180 e 180. |
| `country` | Não | País usado pelo filtro. |
| `state` | Não | Estado ou região administrativa usado pelo filtro. |

Exemplo:

```csv
name,latitude,longitude,country,state
São Paulo,-23.5505,-46.6333,Brasil,São Paulo
Lisboa,38.7223,-9.1393,Portugal,Lisboa
```

Nomes repetidos são aceitos quando país ou estado/região diferem. A identidade duplicada é a
combinação de nome, país e estado, comparada sem diferenciar maiúsculas de minúsculas. O arquivo
deve conter ao menos uma localidade válida; campos obrigatórios ausentes, coordenadas inválidas ou
duplicatas fazem o painel apresentar erro de catálogo.

## Aplicar filtros

Os filtros **País** e **Estado / região** são montados a partir dos valores presentes no CSV.
Estado/região é filtrado dentro do país selecionado. **Todos** inclui também localidades sem o
metadado correspondente. Se nenhum local corresponder, o painel informa e encerra a consulta.

Esses filtros são locais: a Open-Meteo recebe as coordenadas das localidades filtradas. O serviço
aceita coordenadas globalmente, mas o dashboard não pesquisa nem enumera automaticamente cidades.

## Escolher período e interpretar resultados

- **Agora** compara a temperatura atual do ar a 2 m.
- **Data** compara a máxima diária do ar a 2 m no dia local de cada cidade.
- Datas anteriores a hoje usam a reanálise histórica. Hoje e datas futuras usam previsão diária.
- O seletor aceita datas desde 1940 até 15 dias depois de hoje (16 datas contando hoje). A
  disponibilidade histórica ou prevista pode variar por localidade e conjunto de dados.
- Valores ausentes, inválidos ou com unidade inesperada não entram no ranking e aparecem com seu
  estado na tabela.
- A tabela inclui todas as localidades selecionadas, não apenas o top 5, com coordenadas pedidas
  e coordenadas da célula de grade quando retornadas.

Cada máxima pertence ao calendário local da cidade. Portanto, uma data igual em cidades de fusos
diferentes não representa necessariamente o mesmo intervalo UTC. A reanálise é estimativa de
modelo, não necessariamente leitura direta de uma estação.

Os dados são armazenados em cache por 5 minutos. Use **Atualizar agora** para limpar o cache da
consulta e buscar respostas novas. A aplicação não persiste as respostas em disco.
