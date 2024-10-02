from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from random import sample
import pandas as pd
import json, csv
from datetime import date
import pickle
import os
import logging
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler

# Connexion DB
import sqlite3, sqlalchemy
import mysql.connector
from mysql.connector import Error
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, create_engine, text, inspect
from IPython.display import Markdown, display
from binance_histo_symbol import get_data_from_db_symbol
from binance_histo_crypto import get_data_from_db_crypto
from binance_maj_histo_crypto import get_data_from_db2, maj_data_from_db
from binance.client import Client, AsyncClient

logger = logging.getLogger(__name__)

app = FastAPI()

security = HTTPBasic()


# User data
users = {
    "walid": "walid",
    "sam": "sam",
    "clementine": "mandarine"
    }

# Configuration des informations d'authentification admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "4dm1N"



# Class
class ClCrypto(BaseModel):
    Symbol: str
    Time: date
    number_of_questions: int


# Fonctions d'authetification
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if users.get(credentials.username) == credentials.password:
        return credentials.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

# Endpoints : Bienvenue
@app.get('/')
def get_index():
    return {
        'data': 'Bienvenue dans l\'API : Investir dans les cryptos'
        }

# Endpoints : Vérification
@app.get('/verify')
def get_verify():
    """
    Description: Vérifie que l'API est fonctionnelle.

    """
    return {
        "message": "L'API est fonctionnelle."
        }

# Endpoints : Authentification
@app.get("/user")
def current_user(username: str = Depends(authenticate)):
    """
    Description:
    Vérifier l'authentification de l'utilisateur
    
    """
    return "Hello {}".format(username)

# Endpoints : Appel du module Binance pour récupérer les transactions
@app.get("/getcrypto")
def getcrypto():
    # Appeler la fonction du script pour obtenir les données
    data = get_data_from_db_crypto()
    return {"data": data}

# Endpoints : Appel du module Binance pour récupérer les symboles
@app.get("/getsymbol")
def getcrypto():
    # Appeler la fonction du script pour obtenir les données
    data = get_data_from_db_symbol()
    return {"data": data}

# Endpoints : Appel du module Binance pour la MAJ de la data
@app.get("/majcrypto")
def getcrypto():
    # Appeler la fonction du script pour obtenir les données
    try:
        maj_data_from_db()
        return {
        "message": "Mise à jour de l'historique a été effectué avec succés !"
        }
    except Error as e:
        return print(f"Erreur lors de la mise à jour ou de la récupération des données : {e}")
    

# Endpoints : Appel du module Binance pour la MAJ de la data 2
@app.get("/getmajcrypto")
def getcrypto():
    try:
        data = get_data_from_db2()  # Assuming this function retrieves your data
        return {
            "data": data
        }, 200
    except Error as e:
        print(f"Erreur lors de la mise à jour ou de la récupération des données : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {e}")
   

# Endpoints : Affichage des tables sql de la database
@app.get("/db")
def read_db():
    connection = mysql.connector.connect(
        host="mysql_db", # DB_HOST
        user="sam", # DB_USER, MYSQL_USER
        password="samword", # DB_PASSWORD, MYSQL_PASSWORD
        database="crypto_db" # DB_NAME, MYSQL_DATABASE
    )
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    return {"tables": tables}



# Charger le modèle de regression
with open("binaries/rfr.sav","rb") as pickle_reg:
    model_reg = pickle.load(pickle_reg)


# Charger le modèle de regression
with open("binaries/rfc.sav","rb") as pickle_class:
    model_class = pickle.load(pickle_class)


def connect_to_db():
    try:
        
        # Récupérer les variables d'environnement
        db_host = os.getenv("DB_HOST", "localhost")  # Par défaut, localhost
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
    
@app.get('/predict_regression')
def prediction_test_reg():
    try:

        #requete dans une base de données
        #récupération des données
        conn = connect_to_db()
        mycursor = conn.cursor(dictionary=True)
        query = """
        SELECT open as open_price, high as high_price,
            close as close_price, low as low_price,
            volume, quote_asset_volume, number_of_trades,
            base_asset_volume as taker_buy_base_asset_volume,
            base_quote_volume as taker_buy_quote_asset_volume
        FROM T_CRYPTO_HIST
        ORDER BY RAND()
        LIMIT 10
        """

        mycursor.execute(query)

        # Création du DataFrame
        df_prev = pd.DataFrame(mycursor.fetchall())
        mycursor.close()
        conn.close()

        #créer 4 nouveaux champs :'close_price_lag1', 'close_price_lag2', 'close_price_lag3', 'close_price_lag4'
        df_prev['close_price_lag1'] = df_prev['close_price'].shift(1)
        df_prev['close_price_lag2'] = df_prev['close_price'].shift(2)
        df_prev['close_price_lag3'] = df_prev['close_price'].shift(3)
        df_prev['close_price_lag4'] = df_prev['close_price'].shift(4)

        df_prev.drop(columns=['close_price'], inplace=True)

        #prediction=[round(float(pred), 4) for pred in predictions]
        prediction=model_reg.predict(df_prev.dropna())

    except Error as e:
        print(f"Erreur lors de l/'application de la prévision du modèle de régression : {e}")
    
    return {"Regression prediction": list(prediction)}


@app.get('/predict_classification')
def prediction_test_class():
    try:
        #requete dans une base de données
        #récupération des données
        conn = connect_to_db()
        mycursor = conn.cursor(dictionary=True)
        query = """
        SELECT open, high, low, close, volume
        FROM T_CRYPTO_HIST
        ORDER BY RAND()
        LIMIT 1000
        """
        mycursor.execute(query)

        # Création du DataFrame
        df_prev = pd.DataFrame(mycursor.fetchall())
        #print("Shape of dataframe before dropna:", df_prev.shape)
        mycursor.close()
        conn.close()
        
        if df_prev.empty:
            return {"error": "No data available for prediction"}, 400
        
        #créer 4 nouveaux champs :'close_price_lag1', 'close_price_lag2', 'close_price_lag3', 'close_price_lag4'

        def get_rsi(df, rsi_period):
            chg = df['close'].diff(1)
            gain = chg.mask(chg<0,0)
            loss = chg.mask(chg>0,0)
            avg_gain = gain.ewm(com=rsi_period-1, min_periods=rsi_period).mean()
            avg_loss = loss.ewm(com=rsi_period-1, min_periods=rsi_period).mean()
            rs = abs(avg_gain/avg_loss)
            rsi = 100 - (100/(1+rs))
            return rsi

        # relative strength index
        df_prev['rsi14'] = get_rsi(df_prev, 14)

        # Création des moving averages (moyennes mobiles)
        df_prev['sma9'] = df_prev['close'].rolling(9).mean()
        df_prev['sma180'] = df_prev['close'].rolling(180).mean()
        df_prev['sma9_var'] = (df_prev['close']/df_prev['sma9'])-1
        df_prev['sma180_var'] = (df_prev['close']/df_prev['sma180'])-1

        # Création des spreads
        df_prev['spread']=((df_prev['close']/df_prev['open'])-1).abs()
        df_prev['spread14_e']=df_prev['spread'].ewm(span=14).mean()

        # volume-based indicator
        df_prev['volume14'] = df_prev['volume'].rolling(14).mean()
        df_prev['volume34'] = df_prev['volume'].rolling(34).mean()
        df_prev['volume14_34_var'] = (df_prev['volume14']/df_prev['volume34'])-1

        #prediction=round(float(model_class.predict(df_prev.dropna()),4))
        
        df_clean = df_prev.dropna()
        print("Shape of dataframe after dropna:", df_clean.shape)

        if df_clean.empty:
            return {"error": "No valid data after cleaning for prediction"}, 400

        expected_columns = ['open', 'high', 'low', 'close', 'volume', 'rsi14', 'sma9', 'sma180', 'sma9_var', 'sma180_var', 'spread', 'spread14_e', 'volume14', 'volume34', 'volume14_34_var']

        X = df_clean[expected_columns]

        float_cols = X.select_dtypes(include='float64').columns
        tf = ColumnTransformer(
            [('RobustScaler', RobustScaler(), float_cols)],
            remainder='passthrough'
        )

        # Fit and transform X
        tf.fit(X)
        X_transformed = tf.transform(X)

        prediction = model_class.predict(X_transformed)
        #prediction=model_class.predict(X)

    except Error as e:
        print(f"Erreur lors de la prévision du modèle de classification : {e}")

    #return {"Classification prediction": prediction.tolist()}
    return {"Classification prediction": ["gain" if x else "perte" for x in prediction.tolist()]}




    