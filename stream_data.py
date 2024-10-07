
'''
Nom : stream_data.py

Description: 
Code Python qui permet la récupération en live de la crypto monnaie

Créateur : OL,SV
Date création :  16/09/2024


Modification :
    0.1 --> 0.x : 


Version : 0.1
'''

# stream_data.py
import json
import websocket
# from websocket import WebSocketApp 
from IPython.display import Markdown, display
# import os
import xml.etree.ElementTree as ET
import threading

##################################
# Récupération donnée BINANCE - variable XML

## Chemin vers votre fichier XML
chemin_fichier_xml = "Binance_Key.xml"

## Parsez le fichier XML
tree = ET.parse(chemin_fichier_xml)
root = tree.getroot()

for Binance in root.findall('Binance'):
    Binance_Key = Binance.find('api_key').text
    Binance_Secret = Binance.find('api_secret').text
  
##################################
# Connexion BINANCE

# Chargement des modules "Client" et "AscynClient" du package "python-binance"
from binance.client import Client, AsyncClient # dans Conda : pip install python-binance
# chargement du module pandas
import pandas as pd
# Clé et secret pour la connexion à l'API BINANCE
api_key = Binance_Key
api_secret = Binance_Secret
# récupération des clefs privés de connexion API
binance_client = Client(api_key, api_secret)

####################
## Constants BINANCE
# Binance requires specific string constants for Order Types, Order Side, Time in Force, Order response and Kline intervals these are found on binance.client.Client.
SYMBOL_TYPE_SPOT = 'SPOT'

ORDER_STATUS_NEW = 'NEW'
ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_EXPIRED = 'EXPIRED'

KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'

SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'

ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

TIME_IN_FORCE_GTC = 'GTC'
TIME_IN_FORCE_IOC = 'IOC'
TIME_IN_FORCE_FOK = 'FOK'

ORDER_RESP_TYPE_ACK = 'ACK'
ORDER_RESP_TYPE_RESULT = 'RESULT'
ORDER_RESP_TYPE_FULL = 'FULL'

# For accessing the data returned by Client.aggregate_trades().
AGG_ID             = 'a'
AGG_PRICE          = 'p'
AGG_QUANTITY       = 'q'
AGG_FIRST_TRADE_ID = 'f'
AGG_LAST_TRADE_ID  = 'l'
AGG_TIME           = 'T'
AGG_BUYER_MAKES    = 'm'
AGG_BEST_MATCH     = 'M'


 # Dictionnaire pour stocker les données en direct pour chaque symbole
live_trades = {
    'btcusdt': [],
    'ethusdt': [],
    'bnbusdt': [],
    'solusdt': []
}

def on_message(ws, message):
    json_message = json.loads(message)
    symbol = json_message['s'].lower()  # Récupère le symbole du message
    if symbol in live_trades:
        live_trades[symbol].append(json_message)  # Ajoute les données du trade dans la liste correspondante
        if len(live_trades[symbol]) > 10:  # Limite à 10 derniers trades
            live_trades[symbol].pop(0)

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

def ws_trades(symbols):
    socket = f'wss://stream.binance.com:9443/ws/{"/".join([f"{symbol}@trade" for symbol in symbols])}'  # Jointure des symboles
    wsapp = websocket.WebSocketApp(socket,
                                   on_message=on_message,
                                   on_error=on_error,
                                   on_close=on_close)
    wsapp.on_open = on_open
    thread = threading.Thread(target=wsapp.run_forever)
    thread.daemon = True
    thread.start()

# Appelle cette fonction pour démarrer la connexion avec les quatre symboles
ws_trades(['btcusdt', 'ethusdt', 'bnbusdt', 'solusdt'])  # Exemple avec BTC/USDT, ETH/USDT, BNB/USDT et SOL/USDT
