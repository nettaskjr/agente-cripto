#!/usr/bin/env python3

import os
import time
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import KLINE_INTERVAL_1MINUTE
import plotext as plt

# Limite para exibir os últimos N candles
MAX_CANDLES = 30

# Listas globais para armazenar os dados dos candles
times = []
opens = []
highs = []
lows = []
closes = []


def process_message(msg):
    """Callback para processar mensagens do WebSocket.
    Quando um candle é fechado, os dados são armazenados nas listas globais."""
    global times, opens, highs, lows, closes
    if msg and 'k' in msg:
        kline = msg['k']
        is_candle_closed = kline.get('x', False)
        if is_candle_closed:
            # Registra o timestamp do início do candle (em segundos)
            ts = int(kline['t'] / 1000)
            open_price = float(kline['o'])
            high = float(kline['h'])
            low = float(kline['l'])
            close_price = float(kline['c'])
            # Atualiza as listas com os valores do novo candle
            times.append(ts)
            opens.append(open_price)
            highs.append(high)
            lows.append(low)
            closes.append(close_price)
            # Mantém somente os últimos MAX_CANDLES candles
            if len(times) > MAX_CANDLES:
                times.pop(0)
                opens.pop(0)
                highs.pop(0)
                lows.pop(0)
                closes.pop(0)


def update_plot():
    """Atualiza o gráfico de candlesticks no terminal utilizando plotext."""
    plt.clear_figure()
    if len(times) > 0:
        data = {"Open": opens, "High": highs, "Low": lows, "Close": closes}
        plt.candlestick(times, data)
        plt.title("Candlestick Chart para BTCUSDT")
        plt.xlabel("Timestamp")
        plt.ylabel("Preço")
        plt.show()
    else:
        print("Aguardando dados...")


def main():
    # Recupera as chaves da API a partir das variáveis de ambiente
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_SECRET_KEY')

    if not api_key or not api_secret:
        print("Erro: Variáveis de ambiente BINANCE_API_KEY e BINANCE_SECRET_KEY não definidas.")
        return

    # Inicializa o ThreadedWebsocketManager
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    # Carrega a configuração para obter o símbolo a ser analisado
    import xml.etree.ElementTree as ET
    CONFIG_FILE = "/home/nestor/Projetos-github/agente-cripto/config.xml"

    def load_realtime_symbol(config_file):
        try:
            tree = ET.parse(config_file)
            root = tree.getroot()
            crypto_settings = root.find('crypto_settings')
            # Tenta obter o símbolo específico para análise em tempo real
            symbol_node = crypto_settings.find('real_time_symbol')
            if symbol_node is not None and symbol_node.text.strip():
                return symbol_node.text.strip()
            else:
                return 'BTCUSDT'
        except Exception as e:
            print(f"Erro ao carregar o símbolo do config.xml: {e}")
            return 'BTCUSDT'

    realtime_symbol = load_realtime_symbol(CONFIG_FILE)
    print(f"Símbolo a ser analisado em tempo real: {realtime_symbol}")
    
    # Inicia o socket para receber dados de candles do símbolo configurado com intervalo de 1 minuto
    twm.start_kline_socket(symbol=realtime_symbol, callback=process_message, interval=KLINE_INTERVAL_1MINUTE)
    print(f"Socket iniciado para {realtime_symbol} com candles de 1 minuto. Aguardando dados...")

    try:
        # Enquanto o script estiver rodando, atualiza o gráfico periodicamente.
        # Aqui, atualizamos a cada 60 segundos (pode ser ajustado conforme necessário).
        while True:
            update_plot()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Encerrando...")
        twm.stop()


if __name__ == '__main__':
    main()
