'''
Nom : binance_histo.py

Description: 
Code Python qui permet la récupération des données historiques de crypto monnaie

Créateur : OL
Date création :  16/09/2024


Modification :
    0.1 --> 0.x : 


Version : 0.1
'''

##################################
# import des modules et des librairies

import os
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import xml.etree.ElementTree as ET
import sqlite3, sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, create_engine, text, inspect
from IPython.display import Markdown, display
import mysql.connector
from mysql.connector import Error
from binance.client import Client, AsyncClient # dans Conda : pip install python-binance


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




##################################
# Connexion Base
# Récupération data Cryptos



def connect_to_db():
    try:
        
        # Récupérer les variables d'environnement
        db_host = os.getenv("DB_HOST")  # Par défaut, localhost
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        # Connexion à la base de données MySQL
        connection = mysql.connector.connect(
            host=db_host,  
            user=db_user,       # Remplace par l'utilisateur que tu as défini
            password=db_password,  # Mot de passe que tu as défini
            database=db_name  # La base de données créée dans Docker
            # host="mysql_db",
            # user="sam",
            # password="samword",
            # database="crypto_db"
        )

        if connection.is_connected():
            print("Connexion réussie à MySQL")
            return connection

    except Error as e:
        print(f"Erreur de connexion à MySQL : {e}")
        return None

def insert_dataframe_to_mysql(connection, df, table_name):
    cursor = connection.cursor()

    # Créer une requête SQL INSERT dynamique en fonction des colonnes du DataFrame
    cols = ", ".join([str(i) for i in df.columns.tolist()])
    insert_stmt = f"INSERT IGNORE INTO {table_name} ({cols}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # Convertir le DataFrame en une liste de tuples
    data = [tuple(row) for row in df.to_numpy()]

    try:
        # Exécuter l'insertion des lignes
        cursor.executemany(insert_stmt, data)
        connection.commit()
        print(f"{cursor.rowcount} lignes insérées avec succès dans la table {table_name}.")

    except mysql.connector.Error as err:
        print(f"Erreur : {err}")
        connection.rollback()

    finally:
        cursor.close()


def maj_data_from_db():

    conn = connect_to_db()
    
    cursor = conn.cursor()
    
    # Exécuter la requête SQL pour récupérer la valeur max de 'champdate'
    cursor.execute("SELECT MAX(time) FROM T_CRYPTO_HIST")

    # Récupérer le résultat
    maxtime = cursor.fetchone()[0]
    
    if maxtime is not None :
        maxtime = maxtime + timedelta(seconds=1)
        
    # on récupére la date et l'heure du jour
    current_datetime = datetime.now()
        
    List_Symbol = ['SOLUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT']

    # DateDebut = maxtime.strftime("%Y-%m-%d %H:%M:%S") if maxtime else (current_datetime - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
    DateDebut = maxtime.strftime("%Y-%m-%d %H:%M:%S") if maxtime else (current_datetime - relativedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S')
    # DateDebut = '21/09/2024 08:00:00'
    Datefin = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # Datefin = '21/09/2024 18:00:00'

    arr_Symbol = []
    arr_Time = []
    arr_Open = []
    arr_High = []
    arr_Low = []
    arr_Close = []
    arr_Volume = []
    arr_CloseTime = []
    arr_QuoteAv =[]
    arr_trades = []
    arr_TbBaseAv = []
    arr_TbQuoteAv =[]

    # info = binance_client.get_symbol_info('BNBBTC')
    # df = pd.DataFrame()
    for symbol in List_Symbol:
        SymbInfos = binance_client.get_historical_klines(symbol, interval=KLINE_INTERVAL_5MINUTE, start_str=DateDebut, end_str=Datefin)
        for SymbInfo in SymbInfos:
            arr_Symbol.append(symbol)
            arr_Time.append(SymbInfo[0] / 1000)
            arr_Open.append(SymbInfo[1])
            arr_High.append(SymbInfo[2])
            arr_Low.append(SymbInfo[3])
            arr_Close.append(SymbInfo[4])
            arr_Volume.append(SymbInfo[5])
            arr_CloseTime.append(SymbInfo[6] / 1000)
            arr_QuoteAv.append(SymbInfo[7])
            arr_trades.append(SymbInfo[8])
            arr_TbBaseAv.append(SymbInfo[9])
            arr_TbQuoteAv.append(SymbInfo[10])
                        
        
    timestamps = [datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S') for i in arr_Time]
    timestampclose_cleaned = [datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S') for i in arr_CloseTime]

    data_arr = list(zip(arr_Symbol, timestamps, arr_Open, arr_High, arr_Low, arr_Close, arr_Volume, timestampclose_cleaned, arr_QuoteAv, arr_trades, arr_TbBaseAv, arr_TbQuoteAv))
    df = pd.DataFrame(data_arr, columns=['Symbol', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'quote_asset_volume', 'number_of_trades', 'base_asset_volume', 'base_quote_volume'])

    insert_dataframe_to_mysql(conn, df, "T_CRYPTO_HIST")
    conn.close()
    

def get_data_from_db2():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    # Exécuter la requête
    cursor.execute("SELECT * FROM T_CRYPTO_HIST ORDER BY TIME DESC LIMIT 10")
    data = cursor.fetchall()  

    cursor.close()
    conn.close()

    return data
 