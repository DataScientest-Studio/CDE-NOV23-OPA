'''
Nom : streaming_data.py

Description: 
Code Python qui permet la récupération des données live de crypto monnaie

Créateur : OL
Date création :  01/03/2024


Modification :
    0.2 --> 0.3 : 03/03/2023 : SV : modification du script suite à sa recette
        > Création de l'en-tête de description

Version : 0.3
'''
# requis
# pip install websocket-client

import websocket
import json
from binance.client import Client
import xml.etree.ElementTree as ET

# A MODIFIER si necessaire
# Chemin complet vers votre fichier XML
chemin_fichier_xml = "./Binance_Key.xml"

# Parsez le fichier XML
tree = ET.parse(chemin_fichier_xml)
root = tree.getroot()

# récupération des clefs API
# méthode 1
# Binance_Key = root[0][0].text  
# Binance_Secret = root[0][1].text
# print(Binance_Key)
# print(Binance_Secret)

# méthode 2
for Binance in root.findall('Binance'):
    Binance_Key_testnet = Binance.find('api_key_testnet').text
    Binance_Secret_testnet = Binance.find('api_secret_testnet').text
    
api_key = Binance_Key_testnet
api_secret = Binance_Secret_testnet

client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'
client.get_account()

def import_streaming_data(symbol, interval) :
    """
        Récupère les données streaming du bitcoin demandé
        - symbol (str) : Le bitcoin à récupérer (par exemple, 'BTC').
        - interval (str) : L'intervalle de temps entre deux observations en minutes, heures...etc.
       
        Exemple : import_streaming_data('ETHUSDT', '1m')
    """
    closes, highs, lows, volumes, trades = [], [], [], [], []
    candles = {}
   
    def on_message(ws, message):
        nonlocal candles, closes, highs, lows, volumes, trades
       
        json_message = json.loads(message)
        candle = json_message["k"]
        is_candle_closed = candle["x"]
        close =candle["c"]
        high = candle["h"]
        low = candle["l"]
        volume = candle["v"]
        trade = candle["n"]
        symbol = candle["s"]

        if is_candle_closed :
            closes.append(close)
            highs.append(high)
            lows.append(low)
            volumes.append(volume)
            trades.append(trade)
            candles[symbol]=[closes,highs,lows,volumes,trades]
            print(candles)
            with open("./streaming_data_" + symbol.lower() +".json", "w") as f:
                json.dump(candles, f)

    def on_close(ws):
        print("Connection closed")

    socket = f'wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}'
    ws = websocket.WebSocketApp(socket, on_message=on_message,on_close=on_close)
    ws.run_forever()
   
    return candles

# import_streaming_data('ETHUSDT', '1m')

