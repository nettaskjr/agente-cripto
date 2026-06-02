# Agente de Criptomoedas com Binance API

Este projeto implementa um agente de criptomoedas que:

- Coleta dados de mercado (preço, volume, variação percentual) de criptomoedas através da API da Binance.
- Realiza scraping de notícias de fontes configuradas e analisa o sentimento (positivo/negativo) baseado em palavras-chave.
- Gera recomendações de negociação (comprar, vender, manter etc.) com base nos dados de mercado e no sentimento das notícias.

## Índice

- [Configuração](#configuração)
  - [Arquivo config.xml](#arquivo-configxml)
- [Execução do Aplicativo](#execução-do-aplicativo)
- [Dependências](#dependências)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Detalhes dos Campos do XML](#detalhes-dos-campos-do-xml)

## Configuração

O comportamento do agente é amplamente configurável através do arquivo `config.xml`, que deve estar localizado na raiz do projeto (/home/nestor/Projetos-github/agente-cripto/config.xml). Esse arquivo define parâmetros para a API da Binance, configurações de criptomoedas, fontes de notícias, limiares para recomendações e ajustes do agente.

### Variáveis de Ambiente

Antes de executar o agente, é necessário definir as variáveis de ambiente para a API da Binance:

- A variável cujo nome é definido pelo campo `<api_key_env_var>` deve conter a chave da API da Binance.
- A variável cujo nome é definido pelo campo `<api_secret_env_var>` deve conter o segredo da API da Binance.

Exemplo (em um ambiente Linux):

```bash
export BINANCE_API_KEY=suachave
export BINANCE_SECRET_KEY=seusegredo
```

## Execução do Aplicativo

Para rodar o agente, recomendamos utilizar um ambiente virtual Python. OBS.: O repositório não inclui o ambiente virtual. Siga os passos abaixo para criá-lo e executar o agente:

**Criação do Ambiente Virtual:**

1. Crie o ambiente virtual utilizando o comando:

   ```bash
   python3 -m venv venv
   ```

2. Ative o ambiente virtual:
   - No Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```
   - No Windows:
     ```bash
     venv\\Scripts\\activate
     ```

3. Instale as dependências necessárias:

   ```bash
   pip install -r requirements.txt
   ``` Siga os passos abaixo:

4. Execute o agente:

   ```bash
   venv/bin/python3 crypto_agent.py
   ```

O agente iniciará a coleta de dados, análise das notícias e fará a recomendação de operações, exibindo os resultados em uma tabela formatada no terminal.

## Dependências

- Python 3.13 ou superior
- Módulos: `python-binance`, `requests`, `beautifulsoup4`, `tabulate`, `xml.etree.ElementTree` (padrão no Python)

## Estrutura do Projeto

```
agente-cripto/
├── venv/               # Ambiente virtual Python
├── .gitignore           # Arquivo para ignorar arquivos e pastas indesejadas no controle de versão
├── config.xml           # Arquivo de configuração com parâmetros do agente
├── crypto_agent.py      # Aplicativo principal do agente
├── README.md            # Documentação e instruções do projeto
└── requirements.txt     # Arquivo de dependências do projeto
```

## Detalhes dos Campos do XML

O arquivo `config.xml` é dividido em diversas seções, cada uma com campos específicos:

### `<binance_api>`

- **<api_key_env_var>**: Nome da variável de ambiente que contém a chave da API da Binance. Exemplo: `BINANCE_API_KEY`.
- **<api_secret_env_var>**: Nome da variável de ambiente que contém o segredo da API da Binance. Exemplo: `BINANCE_SECRET_KEY`.

### `<crypto_settings>`

- **<symbols>**: Lista de elementos `<symbol>`, onde cada um representa um par de negociação na Binance, como `BTCUSDT`, `ETHUSDT`, etc.
- **<fiat_currency>**: Define a moeda fiduciária utilizada para expressar valores, como `USD` ou `BRL`.

### `<news_settings>`

- **<sources>**: Contém elementos `<source>`. Cada elemento tem um atributo `name` que identifica a fonte (por exemplo, `coindesk`), e o conteúdo do elemento é a URL utilizada para fazer scraping das notícias.
- **<positive_keywords>**: Lista de palavras-chave, separadas por vírgulas, que indicam um sentimento positivo nas manchetes das notícias.
- **<negative_keywords>**: Lista de palavras-chave, separadas por vírgulas, que indicam um sentimento negativo nas notícias.
- **<sentiment_strong_positive_threshold>**: Valor numérico que define o limite a partir do qual o sentimento positivo é considerado "fortemente positivo".
- **<sentiment_strong_negative_threshold>**: Valor numérico que define o limite a partir do qual o sentimento negativo é considerado "fortemente negativo".

### `<recommendation_thresholds>`

- **<high_volume_threshold>**: Volume considerado alto para uma criptomoeda, utilizado como critério para recomendações de compra ou venda.
- **<low_volume_threshold>**: Volume considerado baixo, utilizado para ajustar as recomendações.
- **<strong_buy_change>**: Percentual de variação de preço que, se ultrapassado, indica uma forte oportunidade de compra ("COMPRA FORTE").
- **<buy_change>**: Percentual de variação de preço que serve como critério para recomendar compra.
- **<strong_sell_change>**: Percentual de variação de preço (queda) que, se ultrapassado, indica uma necessidade urgente de venda ("VENDA FORTE").
- **<sell_change>**: Percentual de variação de preço (queda) utilizado para recomendar venda em situações menos críticas.
- **<neutral_price_change_limit>**: Limite de variação de preço que caracteriza um mercado estável ou lateral, influenciando a decisão de manter a posição.

### `<agent_settings>`

- **<update_interval_seconds>**: Intervalo, em segundos, para a atualização e reexecução da análise do mercado. Define com que frequência o agente obtém novos dados e gera recomendações.
- **<max_reason_length>**: Número máximo de caracteres exibidos para o campo "Razões" na tabela de recomendações. Se o texto exceder esse valor, será truncado (embora, conforme solicitado, agora o texto completo é exibido sem resumo).
- **<show_full_json>**: Valor booleano (`true` ou `false`) que indica se todo o JSON com os resultados da análise deve ser exibido. Essa opção é útil para depuração e verificação dos dados completos.

## Conclusão

Este README explica em detalhes como executar o agente de criptomoedas e o significado de cada campo configurável no arquivo XML. Se precisar de mais informações ou tiver dúvidas, sinta-se à vontade para revisar este documento ou entrar em contato.
