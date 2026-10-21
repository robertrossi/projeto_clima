# Projeto Clima

Dashboard em Streamlit que compara temperaturas do ar a 2 m em localidades de um catálogo CSV.
O ranking mostra até cinco localidades mais quentes entre as que passaram pelos filtros.

## Iniciar o dashboard

Na raiz do projeto, instale/sincronize as dependências e execute:

```bash
uv sync
uv run streamlit run src/projeto_clima/app.py
```

O catálogo de exemplo é `config/locations.example.csv`. Ele contém seis localidades brasileiras;
você pode apontar o painel para outro CSV pela barra lateral. Consulte [como usar o painel](uso.md)
para preparar o catálogo e interpretar os filtros e resultados.

## Como funciona o ranking

- **Agora:** compara `temperature_2m` atual.
- **Data:** compara `temperature_2m_max` para o dia selecionado. Datas passadas usam reanálise
  histórica; hoje e datas futuras usam previsão diária.
- O ranking só inclui valores numéricos válidos. Empates são ordenados pelo nome.
- Cada máxima diária usa o dia local da cidade; localidades em fusos diferentes podem cobrir
  períodos UTC diferentes.

O serviço meteorológico trabalha globalmente por coordenadas, mas o dashboard consulta apenas os
locais cadastrados no CSV. País e estado/região são filtros do catálogo, não filtros enviados à API.

Veja a [arquitetura](arquitetura.md), os detalhes das [consultas meteorológicas](api.md) ou as
instruções para [desenvolver e validar](desenvolvimento.md) o projeto.

## Catálogo CSV

O arquivo deve ser UTF-8 e conter `name`, `latitude` e `longitude`. As colunas `country` e `state`
são opcionais. Coordenadas devem seguir os limites WGS84. Localidades com o mesmo nome podem
coexistir se país/estado as distinguirem.

## Desenvolver e testar

```bash
uv run task test
uv run task lint
uv run task docs-build
```

Para editar a documentação com atualização automática no navegador:

```bash
uv run task docs
```
