import pandas as pd
import dash
from dash import Dash, Input, Output, dcc, html, dash_table, State, page_registry, page_container, register_page,callback
import os
import requests
import time

# from dash.dependencies import Input, Output


# Connexion DB
import sqlite3, sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, create_engine, text, inspect
from IPython.display import Markdown, display
import mysql.connector
from mysql.connector import Error
import json



# Fonction pour récupérer les symboles depuis l'API /getcrypto
def get_crypto_data(username : str, password : str):
    try:
        response = requests.get("http://web:8000/getcrypto",auth=(username, password))
        data = response.json()
        # Vérifie si les données sont sous la clé 'data', sinon retourne une liste vide
        return data.get('data', []) if isinstance(data, dict) else []
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API : {e}")
        return []



# Fonction pour récupérer les symboles depuis l'API /getsymbol
def get_symbol_data(username : str, password : str):
    max_retries = 5
    retries = 0
    url = "http://web:8000/getsymbol"
    while retries < max_retries:
        try:
            response = requests.get(url, auth=(username, password))
            if response.status_code == 200:
                data = response.json()
                return data.get('data', []) if isinstance(data, dict) else []
            else :
                print(f"Erreur de réponse, code: {response.status_code}")  
        except requests.exceptions.ConnectionError:
            print(f"Connexion refusée, réessai dans 5 secondes... ({retries+1}/{max_retries})")
            retries += 1
            time.sleep(5)
    return []
    
# Fonction pour appeler l'API /majcrypto
def update_crypto(username : str, password : str):
    try:
        response = requests.get("http://web:8000/majcrypto",auth=(username, password))
        return response.json()  # Supposons que l'API renvoie un JSON
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API majcrypto : {e}")
        return {"message": "Erreur lors de la mise à jour"}

# Fonction pour récupérer le résultat de l'API /getmajcrypto
def get_update_result(username : str, password : str):
    try:
        response = requests.get("http://web:8000/getmajcrypto",auth=(username, password))
        # print(response)
        data = response.json()  # Supposons que l'API renvoie un JSON
        # print(f"Résultat1 brut de l'API: {data}")
        return data
        # return data.get('data', []) if isinstance(data, dict) else []
        
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API getmajcrypto : {e}")
        return {"message": "Erreur lors de la récupération des résultats"}
# def get_symbol_data():
#     max_retries = 5
#     retries = 0
#     url = "http://web:8000/getsymbol"
    
#     while retries < max_retries:
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 return response.json()
#             else:
#                 print(f"Erreur de réponse, code: {response.status_code}")
#         except requests.exceptions.ConnectionError:
#             print(f"Connexion refusée, réessai dans 5 secondes... ({retries+1}/{max_retries})")
#             retries += 1
#             time.sleep(5)
    
#     return []  # Retourner une liste vide après les échecs


# Enregistre la page avec le chemin '/'
register_page(__name__, path='/')

# Créer l'application Dash
# app = dash.Dash(__name__)

# Authentification
username = "sam"
password = "sam"
# Récupérer les données des cryptos
# crypto_data = get_crypto_data()

# Récupérer les symboles pour le filtre
symbol_data = get_symbol_data(username, password)
symbol_options = [{'label': crypto['symbol'], 'value': crypto['symbol']} for crypto in symbol_data]



# Créer le layout de l'application Dash
layout = html.Div([    
    # html.Img(src= "/assets/binance1.png"),
    # html.H1("Bienvenue sur l'Application du projet OPA - BINANCE"),
    # html.H1("Tableau des Cryptomonnaies"),

    # Menu déroulant pour filtrer les symboles
    dcc.Dropdown(
        id='symbol-filter',
        options=symbol_options,
        placeholder="Sélectionnez un symbole",
        multi=False  # Un seul symbole à la fois
    ),

    # Tableau contenant les données des cryptos
    dash_table.DataTable(
        id='crypto-table',
        columns=[
            {'name': 'Symbol', 'id': 'symbol'},
            {'name': 'Time', 'id': 'time'},
            {'name': 'Open', 'id': 'open'},
            {'name': 'High', 'id': 'high'},
            {'name': 'Low', 'id': 'low'},
            {'name': 'Close', 'id': 'close'},
            {'name': 'Volume', 'id': 'volume'},
            {'name': 'Close Time', 'id': 'closetime'},
            {'name': 'Quote Asset Volume', 'id': 'quote_asset_volume'},
            {'name': 'Number of Trades', 'id': 'number_of_trades'},
            {'name': 'Base Asset Volume', 'id': 'base_asset_volume'},
            {'name': 'Base Quote Volume', 'id': 'base_quote_volume'}
        ],
        data=get_crypto_data(username, password),  # Initialisation avec les données non filtrées
        page_size=20,  # Limite à 20 lignes par page
        style_table={'overflowX': 'auto'}
    ),
    # Boutons pour mettre à jour et afficher les résultats
    html.Div([
        html.Button('MajCrypto', id='update-button', n_clicks=0),
        html.Button('Afficher Résultat', id='result-button', n_clicks=0),
    ]),

  # Nouveau tableau pour afficher le résultat de getmajcrypto
    dash_table.DataTable(
        id='update-result-table2',
        columns=[
            {'name': 'Message', 'id': 'message'},
            # Ajoute d'autres colonnes si nécessaire
        ],
        data=[],  # Initialiser vide, sera mis à jour par le callback
        page_size=1,  # Limite à 10 lignes par page
        style_table={'overflowX': 'auto'}
    ),
  # Nouveau tableau pour afficher le résultat de getmajcrypto
    dash_table.DataTable(
        id='update-result-table',
        columns=[
            {'name': 'Symbol', 'id': 'symbol'},
            {'name': 'Time', 'id': 'time'},
            {'name': 'Open', 'id': 'open'},
            {'name': 'High', 'id': 'high'},
            {'name': 'Low', 'id': 'low'},
            {'name': 'Close', 'id': 'close'},
            {'name': 'Volume', 'id': 'volume'},
            {'name': 'Close Time', 'id': 'closetime'},
            {'name': 'Quote Asset Volume', 'id': 'quote_asset_volume'},
            {'name': 'Number of Trades', 'id': 'number_of_trades'},
            {'name': 'Base Asset Volume', 'id': 'base_asset_volume'},
            {'name': 'Base Quote Volume', 'id': 'base_quote_volume'}
            # Ajoute d'autres colonnes si nécessaire
        ],
        data=[],  # Initialiser vide, sera mis à jour par le callback
        # data = get_crypto_data(),
        page_size=10,  # Limite à 10 lignes par page
        style_table={'overflowX': 'auto'}
    )
])

# Callback pour mettre à jour le tableau en fonction du filtre sélectionné
@callback(
    Output('crypto-table', 'data'),
    [Input('symbol-filter', 'value')]
)

def update_table(selected_symbol):
    # Filtrer les données selon le symbole sélectionné
    all_data = get_crypto_data(username, password)
    filtered_data = [row for row in all_data if row['symbol'] == selected_symbol] if selected_symbol else all_data
    return filtered_data

# Callback pour mettre à jour les données du tableau
@callback(
    Output('update-result-table2', 'data'),
    Input('update-button', 'n_clicks')
)


def update_table(n_clicks):
    # Mettre à jour les données de crypto
    if n_clicks > 0:
        update_crypto(username, password)  # Appel de l'API pour mettre à jour les cryptos
    # return get_crypto_data()  # Récupérer les données actualisées
    return dash.no_update  # Ne pas mettre à jour le tableau

# Callback pour afficher le résultat de getmajcrypto dans le nouveau tableau
@callback(
    Output('update-result-table', 'data'),
    Input('result-button', 'n_clicks')
)
def display_update_result(n_clicks):
    if n_clicks > 0:
        result = get_update_result(username, password)  # Appel de l'API pour obtenir les résultats
        
        # Vérification si result est None ou vide
        if result is None:
            return [{"message": "Aucune donnée disponible. La réponse est vide."}]
        
        if not result:  # Si result est vide ([], {}, '')
            return [{"message": "Aucune donnée reçue de l'API."}]
        
        # Si result contient des données valides
        return [ {
                'symbol': item.get('symbol'),
                'time': item.get('time'),
                'open': item.get('open'),
                'high': item.get('high'),
                'low': item.get('low'),
                'close': item.get('close'),
                'volume': item.get('volume'),
                'closetime': item.get('closetime'),
                'quote_asset_volume': item.get('quote_asset_volume'),
                'number_of_trades': item.get('number_of_trades'),
                'base_asset_volume': item.get('base_asset_volume'),
                'base_quote_volume': item.get('base_quote_volume'),
            # } for item in result  # On itère directement sur la liste result
            } for item in result[0].get('data', [])  # Adapte en fonction de la structure de l'API
        ]
    return []

# # Lancer l'application
# if __name__ == '__main__':
#     app.run_server(host='0.0.0.0', port=8050, debug=True)  # Démarrer Dash sur le port 8050
