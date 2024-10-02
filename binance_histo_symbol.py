'''
Nom : binance_histo.py

Description: 
Code Python qui permet la récupération des données historiques de crypto monnaie

Créateur : OL, SV
Date création :  16/09/2024


Modification :
    0.1 --> 0.x : 


Version : 0.1
'''

##################################
# import module

import xml.etree.ElementTree as ET
import sqlite3, sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, create_engine, text, inspect
from IPython.display import Markdown, display
import os
import mysql.connector
from mysql.connector import Error
import json
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

def insert_symbol(symbol):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            sql = "INSERT IGNORE INTO T_SYMBOL (symbol) VALUES (%s)"
            cursor.execute(sql, (symbol,))
            connection.commit()
            print(f"Symbol {symbol} inséré avec succès")

        except Error as e:
            print(f"Erreur lors de l'insertion des données : {e}")

        # finally:
        #     close_connection(connection)



def get_data_from_db_symbol():
    # Récupérer la variable d'environnement DATABASE_URL
    # DATABASE_URL = os.getenv('DATABASE_URL')
    # engine = create_engine(DATABASE_URL, echo= True)
    
    
    # engine = create_engine('sqlite:///db/opa_database.db', echo= True)
    # inspector = inspect(engine)
    # inspector.get_table_names()
    # inspector.get_columns(table_name='T_SYMBOL')

    List_Symbol = ['SOLUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT']
    for symbol in List_Symbol :
        # SymbInfos =  binance_client.get_symbol_info(symbol)
        # print(list(SymbInfos.values())[0])
        # arr_Symbol.append(list(SymbInfos.values())[0])
        # insert_symbol(list(SymbInfos.values())[0])
        insert_symbol(symbol)


    # conn = sqlite3.connect("opa_database.db")
    # conn = engine.connect()
    conn = connect_to_db()
    # c = conn.cursor()
    cursor = conn.cursor(dictionary=True)

        
    # Exécuter la requête
    resultsql = cursor.execute("SELECT * FROM T_SYMBOL LIMIT 10")
    # resultsql = conn.execute(text("SELECT * FROM T_SYMBOL LIMIT 10"))
    
    # Récupérer les résultats dans une liste de dictionnaires
    # columns = resultsql.keys()  # Récupère les noms des colonnes
    # data = [dict(zip(columns, row)) for row in resultsql]
    data = cursor.fetchall()
    # data = [row._asdict() for row in resultsql]
    

    # Convertir les résultats en JSON
    json_data = json.dumps(data, default=str)  # default=str pour gérer les objets datetime
    
    cursor.close()
    conn.close()
    
    # return json_data
    return data
    # print(testsql)
    # for row in testsql:
    #     print(row)
    
    
    # testsql2 = conn.execute(text("SELECT * FROM T_CRYPTO_HIST LIMIT 10"))
    # print(testsql2)
    # for row in testsql2:
    #     print(row)    

# datares = get_data_from_db_symbol()
# for row in datares:
#     print(row)