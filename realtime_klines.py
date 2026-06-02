#!/usr/bin/env python3

import os
from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.enums import KLINE_INTERVAL_1MINUTE


def process_message(msg):
    """Processa as mensagens recebidas do websocket e exibe os dados da vela."""
    if msg and 'k' in msg:
        kline = msg['k']
        symbol = kline['s']
        interval = kline['i']
        open_price = kline['o']
        close_price = kline['c']
        high = kline['h']
        low = kline['l']
        volume = kline['v']
        is_candle_closed = kline['x']

        print(f"\n=== Atualização de Candle ===")
        print(f"Símbolo: {symbol}")
        print(f"Intervalo: {interval}")
        print(f"Abertura: {open_price}")
        print(f"Fechamento: {close_price}")
        print(f"Máxima: {high}")
        print(f"Mínima: {low}")
        print(f"Volume: {volume}")
        print(f"Candle fechado: {is_candle_closed}")


def main():
    # Recupera as chaves da API a partir das variáveis de ambiente
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_SECRET_KEY')

    if not api_key or not api_secret:
        print("Erro: Variáveis de ambiente BINANCE_API_KEY e BINANCE_SECRET_KEY não definidas.")
        return

    # Cria e inicia o ThreadedWebsocketManager
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    # Inicia o socket para dados de candles de BTCUSDT com intervalo de 1 minuto
    twm.start_kline_socket(symbol='BTCUSDT', callback=process_message, interval=KLINE_INTERVAL_1MINUTE)
    print("Socket iniciado para BTCUSDT com candles de 1 minuto. Aguardando dados...")

    # Mantém o script rodando
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Encerrando...")
        twm.stop()


if __name__ == '__main__':
    main()
