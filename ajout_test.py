import numpy as np
import pickle
import pandas as pd
import os
import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI

app = FastAPI()


# Charger le modèle de regression
with open("binaries/rfr.sav","rb") as pickle_reg:
    model_reg = pickle.load(pickle_reg)


# Charger le modèle de regression
with open("binaries/rfc.sav","rb") as pickle_class:
    model_class = pickle.load(pickle_class)
# Les features à importer de la table T_CRYPTO_HIST
#['open_price' 'high_price' 'low_price' 'volume' 'quote_asset_volume'
# 'number_of_trades' 'taker_buy_base_asset_volume'
# 'taker_buy_quote_asset_volume' 'close_price_lag1' 'close_price_lag2'
# 'close_price_lag3' 'close_price_lag4']


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
    
@app.post('/predict_regression')
def prediction_test_reg():

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

    #créer 4 nouveaux champs :'close_price_lag1', 'close_price_lag2', 'close_price_lag3', 'close_price_lag4'
    df_prev['close_price_lag1'] = df_prev['close_price'].shift(1)
    df_prev['close_price_lag2'] = df_prev['close_price'].shift(2)
    df_prev['close_price_lag3'] = df_prev['close_price'].shift(3)
    df_prev['close_price_lag4'] = df_prev['close_price'].shift(4)

    df_prev.drop(columns=['close_price'], replace=True) # drop(['close_price'], axis=1, replace=True)

    prediction=model_reg.predict(df_prev.dropna())
    
    return {"Regression prediction": list(prediction)}


@app.post('/predict_classification')
def prediction_test_class():

    #requete dans une base de données
    #récupération des données
    conn = connect_to_db()
    mycursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT open, high, low, close, volume    
    FROM T_CRYPTO_HIST
    ORDER BY RAND()
    LIMIT 10
    """
    mycursor.execute(query)

    # Création du DataFrame
    df_prev = pd.DataFrame(mycursor.fetchall())

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

    prediction=model_class.predict(df_prev.dropna())
    
    return {"Classification prediction": list(prediction)}


if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')