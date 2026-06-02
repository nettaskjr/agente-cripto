
import os
import requests
import json
from datetime import datetime
import time
from bs4 import BeautifulSoup
from binance.client import Client
from tabulate import tabulate
import xml.etree.ElementTree as ET

CONFIG_FILE = "/home/nestor/Projetos-github/agente-cripto/config.xml"

def load_config(config_file):
    config = {}
    tree = ET.parse(config_file)
    root = tree.getroot()

    # Binance API
    binance_api = root.find('binance_api')
    config['API_KEY_ENV_VAR'] = binance_api.find('api_key_env_var').text
    config['API_SECRET_ENV_VAR'] = binance_api.find('api_secret_env_var').text

    # Crypto Settings
    crypto_settings = root.find('crypto_settings')
    config['CRYPTO_SYMBOLS_BINANCE'] = [s.text for s in crypto_settings.find('symbols').findall('symbol')]
    config['FIAT_CURRENCY'] = crypto_settings.find('fiat_currency').text

    # News Settings
    news_settings = root.find('news_settings')
    config['NEWS_SOURCES'] = {s.get('name'): s.text for s in news_settings.find('sources').findall('source')}
    config['POSITIVE_KEYWORDS'] = news_settings.find('positive_keywords').text.split(', ')
    config['NEGATIVE_KEYWORDS'] = news_settings.find('negative_keywords').text.split(', ')
    config['SENTIMENT_STRONG_POSITIVE_THRESHOLD'] = int(news_settings.find('sentiment_strong_positive_threshold').text)
    config['SENTIMENT_STRONG_NEGATIVE_THRESHOLD'] = int(news_settings.find('sentiment_strong_negative_threshold').text)

    # Recommendation Thresholds
    rec_thresholds = root.find('recommendation_thresholds')
    config['HIGH_VOLUME_THRESHOLD'] = int(rec_thresholds.find('high_volume_threshold').text)
    config['LOW_VOLUME_THRESHOLD'] = int(rec_thresholds.find('low_volume_threshold').text)
    config['STRONG_BUY_CHANGE'] = float(rec_thresholds.find('strong_buy_change').text)
    config['BUY_CHANGE'] = float(rec_thresholds.find('buy_change').text)
    config['STRONG_SELL_CHANGE'] = float(rec_thresholds.find('strong_sell_change').text)
    config['SELL_CHANGE'] = float(rec_thresholds.find('sell_change').text)
    config['NEUTRAL_PRICE_CHANGE_LIMIT'] = float(rec_thresholds.find('neutral_price_change_limit').text)

    # Agent Settings
    agent_settings = root.find('agent_settings')
    config['UPDATE_INTERVAL_SECONDS'] = int(agent_settings.find('update_interval_seconds').text)
    config['MAX_REASON_LENGTH'] = int(agent_settings.find('max_reason_length').text)
    config['SHOW_FULL_JSON'] = agent_settings.find('show_full_json').text.lower() == 'true'
    
    return config

# Carregar configurações globais
GLOBAL_CONFIG = load_config(CONFIG_FILE)

def get_crypto_data(symbol):
    """Obtém preço e volume de uma criptomoeda da Binance API."""
    try:
        # Obter ticker para preço, volume de 24h e variação percentual de 24h
        ticker = client.get_ticker(symbol=symbol)
        price = float(ticker['lastPrice'])
        volume = float(ticker['quoteVolume']) # Volume em USDT
        price_change_percent = float(ticker['priceChangePercent']) # Variação percentual de 24h
        return {"price": price, "volume": volume, "price_change_percent": price_change_percent}
    except Exception as e:
        print(f"Erro ao buscar dados de {symbol} da Binance: {e}")
        return None

def get_crypto_news(source_url):
    """Faz web scraping de títulos de notícias de uma fonte."""
    headlines = []
    try:
        response = requests.get(source_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Seletor atual para CoinDesk (pode precisar de ajustes futuros)
        # Tentei encontrar um seletor mais robusto, mas ainda é um ponto de falha potencial
        for article in soup.find_all('a', class_='card-title d-block'): # Seletor atualizado (tentativa)
            headline = article.text.strip()
            if headline:
                headlines.append(headline)
        return headlines
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer scraping de notícias de {source_url}: {e}")
        return []
    except Exception as e:
        print(f"Erro ao processar notícias de {source_url}: {e}")
        return []

def analyze_sentiment(headlines):
    """Análise de sentimento básica baseada em palavras-chave."""
    positive_keywords = GLOBAL_CONFIG['POSITIVE_KEYWORDS']
    negative_keywords = GLOBAL_CONFIG['NEGATIVE_KEYWORDS']

    sentiment_score = 0
    for headline in headlines:
        for keyword in positive_keywords:
            if keyword in headline.lower():
                sentiment_score += 1
        for keyword in negative_keywords:
            if keyword in headline.lower():
                sentiment_score -= 1
    
    if sentiment_score > GLOBAL_CONFIG['SENTIMENT_STRONG_POSITIVE_THRESHOLD']:
        return "fortemente positivo"
    elif sentiment_score > 0:
        return "positivo"
    elif sentiment_score < GLOBAL_CONFIG['SENTIMENT_STRONG_NEGATIVE_THRESHOLD']:
        return "fortemente negativo"
    elif sentiment_score < 0:
        return "negativo"
    else:
        return "neutro"

def generate_recommendation(crypto_data, news_sentiment):
    """Gera uma recomendação direta com base nos dados e sentimento das notícias."""
    recommendation = "Manter"
    reason = []

    if crypto_data and crypto_data["price"] and crypto_data["volume"] is not None and crypto_data["price_change_percent"] is not None:
        price = crypto_data["price"]
        volume = crypto_data["volume"]
        price_change_percent = crypto_data["price_change_percent"]

        # Limiares de volume (ajuste conforme a liquidez da criptomoeda e sua tolerância a risco)
        HIGH_VOLUME_THRESHOLD = GLOBAL_CONFIG['HIGH_VOLUME_THRESHOLD']
        LOW_VOLUME_THRESHOLD = GLOBAL_CONFIG['LOW_VOLUME_THRESHOLD']

        # Limiares de variação de preço (ajuste conforme sua estratégia)
        STRONG_BUY_CHANGE = GLOBAL_CONFIG['STRONG_BUY_CHANGE']
        BUY_CHANGE = GLOBAL_CONFIG['BUY_CHANGE']
        STRONG_SELL_CHANGE = GLOBAL_CONFIG['STRONG_SELL_CHANGE']
        SELL_CHANGE = GLOBAL_CONFIG['SELL_CHANGE']
        NEUTRAL_PRICE_CHANGE_LIMIT = GLOBAL_CONFIG['NEUTRAL_PRICE_CHANGE_LIMIT']

        reason.append(f"Variação de 24h: {price_change_percent:.2f}%")
        reason.append(f"Volume de 24h: {volume:,.2f} {GLOBAL_CONFIG['FIAT_CURRENCY']}")
        reason.append(f"Sentimento de Notícias: {news_sentiment.capitalize()}")

        # Lógica de recomendação mais direta
        if news_sentiment == "fortemente positivo" and price_change_percent > BUY_CHANGE and volume > HIGH_VOLUME_THRESHOLD:
            recommendation = "COMPRA FORTE"
            reason.append("Forte alinhamento de notícias positivas, alta valorização e volume expressivo. Indicativo de momento de alta.")
        elif news_sentiment == "positivo" and price_change_percent > BUY_CHANGE and volume > LOW_VOLUME_THRESHOLD:
            recommendation = "Comprar"
            reason.append("Notícias positivas, valorização e volume saudável. Bom ponto de entrada.")
        elif news_sentiment == "fortemente negativo" and price_change_percent < SELL_CHANGE and volume > HIGH_VOLUME_THRESHOLD:
            recommendation = "VENDA FORTE"
            reason.append("Forte alinhamento de notícias negativas, queda acentuada e alto volume. Risco de desvalorização contínua.")
        elif news_sentiment == "negativo" and price_change_percent < SELL_CHANGE and volume > LOW_VOLUME_THRESHOLD:
            recommendation = "Vender"
            reason.append("Notícias negativas, desvalorização e volume relevante. Possível saída para evitar perdas.")
        elif price_change_percent > STRONG_BUY_CHANGE and volume > HIGH_VOLUME_THRESHOLD:
            recommendation = "COMPRA OPORTUNA"
            reason.append("Aumento significativo de preço com alto volume, mesmo com sentimento neutro/positivo moderado. O mercado está agindo.")
        elif price_change_percent < STRONG_SELL_CHANGE and volume > HIGH_VOLUME_THRESHOLD:
            recommendation = "VENDA URGENTE"
            reason.append("Queda abrupta de preço com alto volume. O mercado está em pânico ou realizando lucros agressivamente.")
        elif news_sentiment == "neutro" and abs(price_change_percent) < NEUTRAL_PRICE_CHANGE_LIMIT and volume < LOW_VOLUME_THRESHOLD:
            recommendation = "Manter (Mercado Estável/Lateral)"
            reason.append("Mercado lateralizado, sem grandes movimentos de preço ou volume, e notícias neutras. Aguardar um catalisador.")
        else:
            recommendation = "Manter"
            reason.append("Condições de mercado mistas ou sem um gatilho claro de compra/venda. Observar.")
    else:
        reason.append("Dados de mercado insuficientes para uma recomendação clara.")
        recommendation = "Manter (dados insuficientes)"

    return {"recommendation": recommendation, "reasons": reason}

def run_analysis():
    """Executa a análise completa e gera o output JSON e em tabela."""
    print(f"\n--- Iniciando Análise de Mercado de Criptomoedas ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    results = {}
    
    all_news_headlines = []
    for source_name, url in GLOBAL_CONFIG['NEWS_SOURCES'].items():
        print(f"Coletando notícias de {source_name}...")
        headlines = get_crypto_news(url)
        all_news_headlines.extend(headlines)
        print(f"Notícias de {source_name}: {len(headlines)} manchetes encontradas.")
    
    overall_sentiment = analyze_sentiment(all_news_headlines)
    print(f"Sentimento geral das notícias: {overall_sentiment}")

    table_data = []
    for symbol in GLOBAL_CONFIG['CRYPTO_SYMBOLS_BINANCE']:
        print(f"Analisando {symbol.upper()}...")
        crypto_data = get_crypto_data(symbol)
        if crypto_data:
            recommendation_data = generate_recommendation(crypto_data, overall_sentiment)
            results[symbol] = {
                "current_data": crypto_data,
                "news_sentiment": overall_sentiment,
                "recommendation": recommendation_data
            }
            # Preparar dados para a tabela
            reason_str = "\n".join([r.strip() for r in recommendation_data['reasons'] if r.strip()])
            table_data.append([
                symbol,
                f"{crypto_data['price']:.2f}",
                f"{crypto_data['price_change_percent']:.2f}%",
                recommendation_data['recommendation'],
                reason_str
            ])
        else:
            results[symbol] = {
                "current_data": None,
                "news_sentiment": overall_sentiment,
                "recommendation": {"recommendation": "Manter (dados não disponíveis)", "reasons": ["Não foi possível obter dados de mercado."]}
            }
            table_data.append([
                symbol,
                "N/A", "N/A",
                "Manter (dados não disponíveis)",
                "Não foi possível obter dados de mercado."
            ])
        print(f"Análise para {symbol.upper()} concluída.")
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "analysis_results": results,
        "raw_news_headlines": all_news_headlines # Incluir para depuração/verificação
    }
    
    print("\n--- Sumário das Recomendações ---")
    headers = ["Cripto", "Preço", "Var. 24h", "Recomendação", "Razões"]
    print(tabulate(table_data, headers=headers, tablefmt="grid", floatfmt=".2f"))

    if GLOBAL_CONFIG['SHOW_FULL_JSON']:
        print("\n--- Análise Completa (JSON) ---")
        print(json.dumps(output, indent=4, ensure_ascii=False))

    # Para gráficos, você precisaria de um ambiente de visualização e bibliotecas como matplotlib.
    # Exemplo de como você poderia usar os dados para gerar um gráfico (apenas demonstração):
    # import matplotlib.pyplot as plt
    # prices = [results[s]["current_data"]["price"] for s in GLOBAL_CONFIG['CRYPTO_SYMBOLS_BINANCE'] if results[s]["current_data"]]
    # labels = [s.replace('USDT', '') for s in GLOBAL_CONFIG['CRYPTO_SYMBOLS_BINANCE'] if results[s]["current_data"]]
    # plt.figure(figsize=(10, 6))
    # plt.bar(labels, prices)
    # plt.title("Preços Atuais das Criptomoedas")
    # plt.ylabel("Preço (USD)")
    # plt.show() # Isso abriria uma janela gráfica, se executado em um ambiente com interface gráfica.

def main():
    global client # Declarar client como global dentro de main para atribuir a ele

    # Lógica de inicialização do cliente Binance
    API_KEY_ENV_VAR = GLOBAL_CONFIG['API_KEY_ENV_VAR']
    API_SECRET_ENV_VAR = GLOBAL_CONFIG['API_SECRET_ENV_VAR']

    API_KEY = os.getenv(API_KEY_ENV_VAR)
    API_SECRET = os.getenv(API_SECRET_ENV_VAR)

    print(f"DEBUG: {API_KEY_ENV_VAR} carregada: {'Sim' if API_KEY else 'Não'}")
    print(f"DEBUG: {API_SECRET_ENV_VAR} carregada: {'Sim' if API_SECRET else 'Não'}")

    if not API_KEY or not API_SECRET:
        print(f"ERRO: As variáveis de ambiente {API_KEY_ENV_VAR} e {API_SECRET_ENV_VAR} devem ser definidas e não podem ser vazias.")
        print("O agente não pode ser inicializado sem as chaves da API da Binance.")
        sys.exit(1) # Sai do programa

    try:
        client = Client(API_KEY, API_SECRET)
        print("DEBUG: Cliente Binance inicializado com sucesso.")
    except Exception as e:
        print(f"ERRO: Erro ao inicializar o cliente Binance. Verifique suas chaves de API. Erro: {e}")
        print("O agente não pode ser inicializado.")
        sys.exit(1) # Sai do programa

    UPDATE_INTERVAL_SECONDS = GLOBAL_CONFIG['UPDATE_INTERVAL_SECONDS']
    while True:
        try:
            run_analysis()
        except Exception as e:
            print(f"Ocorreu um erro durante a execução: {e}")
        print(f"\nAguardando {UPDATE_INTERVAL_SECONDS / 60} minutos para a próxima análise...")
        time.sleep(UPDATE_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
