from flask import Flask, jsonify, request, url_for, send_file, render_template_string, make_response
import numpy as np
import pickle
import pandas as pd
import flasgger
from flasgger import Swagger
import mysql.connector
from mysql.connector import connect, Error
import os
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler

app=Flask(__name__)
Swagger(app)

# Charger le modèle de régression
with open("binaries/rfr.sav","rb") as model:
    model_reg = pickle.load(model)

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
    
@app.route('/predict_reg',methods=["Get"])
def predict_reg_class():
    
    """Predict the price of crypto.
    ---
    parameters:  
      - name: Date début
        in: query
        type: string
        required: true
        example: '27/09/2024 00:00:00'
      - name: Date fin
        in: query
        type: string
        required: true
        example: '28/09/2024 23:00:00'
      
    responses:
        500:
            description: Prediction
        
    """
    date_start = request.args.get("Date début")
    date_end = request.args.get("Date fin")
    
    try:
        
        date_start_dt = datetime.strptime(date_start, "%d/%m/%Y %H:%M:%S")
        date_end_dt = datetime.strptime(date_end, "%d/%m/%Y %H:%M:%S")
        print("date_start_dt :", date_start_dt)
        print("date_end_dt :", date_end_dt)
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
        WHERE closetime BETWEEN %s AND %s
        LIMIT 10
        """

        mycursor.execute(query, (date_start_dt, date_end_dt))

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

        df_prediction = pd.DataFrame(prediction, columns=['prediction'])

        # Exporter les prédictions dans un fichier CSV
        df_prediction.to_csv('predictions_reg.csv', index=False)

        # Générer l'URL de téléchargement
        download_link = url_for('download_predictions', _external=True)

        response = {
            "message": "Les prédictions ont été enregistrées dans 'predictions_reg.csv'.",
            "download_link": download_link,
            "Regression prediction": list(prediction)
        }
        return jsonify(response)
        #return {"Regression prediction": list(prediction)}

    #except Error as e:
    #    print(f"Erreur lors de l/'application de la prévision du modèle de régression : {e}")
    
    except ValueError as ve:
        return {"error": f"Erreur de formatage des dates : {ve}"}, 400

    except Error as e:
        return {"error": f"Erreur SQL : {e}"}, 500

    except Exception as e:
        return {"error": f"Erreur générale : {e}"}, 500

@app.route('/predict_reg_file',methods=["POST"])
def prediction_reg_test_file():
    """Prediction on multiple input test file .
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
      
    responses:
        500:
            description: Test file Prediction
        
    """

    df_test=pd.read_csv(request.files.get("file"))
    
    df_test['close_price_lag1'] = df_test['close_price'].shift(1)
    df_test['close_price_lag2'] = df_test['close_price'].shift(2)
    df_test['close_price_lag3'] = df_test['close_price'].shift(3)
    df_test['close_price_lag4'] = df_test['close_price'].shift(4)

    df_test.drop(columns=['close_price'], inplace=True)

    prediction = None

    try:
        prediction=model_reg.predict(df_test.dropna())
        df_prediction = pd.DataFrame(prediction, columns=['prediction'])

        # Exporter les prédictions dans un fichier CSV
        df_prediction.to_csv('predictions.csv', index=False)

        # Générer l'URL de téléchargement
        download_link = url_for('download_predictions', _external=True)
        
        response = {
            "Regression prediction": list(prediction),
            "download_link": download_link   ,
            "message": "Les prédictions ont été enregistrées dans 'predictions.csv'."                     
        }
        return jsonify(response)

        #html_message = f"""
        #<html>
        #    <body>
        #        <p>Les prédictions ont été enregistrées dans 'predictions.csv'.</p>
        #        <a href="{download_link}" download>Cliquez ici pour télécharger le fichier de prédictions</a>
        #    </body>
        #</html>
        #"""

        # Retourner la réponse HTML
        response = make_response(html_message)
        response.headers['Content-Type'] = 'text/html'
        return response

    except Exception as e:
        print(f"Erreur lors de l'application de la prévision du modèle de régression : {e}")
        return {"error": f"Une erreur est survenue : {e}"}, 500  # Retourner un message d'erreur HTTP 500

@app.route('/download_predictions', methods=["GET"])
def download_predictions():
    # Retourner le fichier CSV en pièce jointe
    try:
        return send_file('predictions.csv', as_attachment=True)
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier : {e}")
        return {"error": f"Le fichier n'a pas pu être téléchargé : {e}"}, 500



# Charger le modèle de classification
with open("binaries/rfc.sav","rb") as model:
    model_class = pickle.load(model)

@app.route('/predict_classif',methods=["Get"])
def predict_classif_class():
    
    """Predict if the investor win or not.
    ---
    parameters:
      - name: Date début
        in: query
        type: string
        required: true
        example: '27/09/2024 00:00:00'
      - name: Date fin
        in: query
        type: string
        required: true
        example: '28/09/2024 23:00:00'
      
    responses:
        500:
            description: Prediction
        
    """
    date_start = request.args.get("Date début")
    date_end = request.args.get("Date fin")
    
    try:
        
        date_start_dt = datetime.strptime(date_start, "%d/%m/%Y %H:%M:%S")
        date_end_dt = datetime.strptime(date_end, "%d/%m/%Y %H:%M:%S")
        print("date_start_dt :", date_start_dt)
        print("date_end_dt :", date_end_dt)
        #requete dans une base de données
        #récupération des données
        conn = connect_to_db()
        mycursor = conn.cursor(dictionary=True)
        query = """
        SELECT open, high, low, close, volume
        FROM T_CRYPTO_HIST
        WHERE closetime BETWEEN %s AND %s
        LIMIT 1000
        """

        mycursor.execute(query, (date_start_dt, date_end_dt))

        # Création du DataFrame
        df_prev = pd.DataFrame(mycursor.fetchall())
        mycursor.close()
        conn.close()

        if df_prev.empty:
            return {"error": "No data available for prediction"}, 400

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
        
        df_clean = df_prev.dropna()

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

        prediction_label = ["Gain" if pred else "Perte" for pred in prediction]

        df_prediction = pd.DataFrame(prediction_label, columns=['prediction'])

        # Exporter les prédictions dans un fichier CSV
        df_prediction.to_csv('predictions_classif.csv', index=False)

        # Générer l'URL de téléchargement
        download_link = url_for('download_predictions', _external=True)

        response = {
            "message": "Les prédictions ont été enregistrées dans 'predictions_classif.csv'.",
            "download_link": download_link,
            "Classification prediction": prediction_label
        }
        return jsonify(response)

    #except Error as e:
    #    print(f"Erreur lors de l/'application de la prévision du modèle de régression : {e}")
    
    except ValueError as ve:
        return {"error": f"Erreur de formatage des dates : {ve}"}, 400

    except Error as e:
        return {"error": f"Erreur SQL : {e}"}, 500

    except Exception as e:
        return {"error": f"Erreur générale : {e}"}, 500


if __name__=='__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)