import pandas as pd
import numpy as np
import streamlit as st
import uuid
import mysql.connector
from mysql.connector import connect, Error
from datetime import datetime
import os

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
            # user="walid",
            # password="walid",
            # database="crypto_db"
        )

        if connection.is_connected():
            print("Connexion réussie à MySQL")
            return connection

    except Error as e:
        print(f"Erreur de connexion à MySQL : {e}")
        return None


# Initialisation des clés dans st.session_state si elles n'existent pas déjà
if 'date_start' not in st.session_state:
    st.session_state['date_start'] = ''

if 'date_end' not in st.session_state:
    st.session_state['date_end'] = ''

if 'symbol_crypto' not in st.session_state:
    st.session_state['symbol_crypto'] = ''


# Fonction pour réinitialiser les valeurs dans st.session_state
def reset_form():
    for key in ['date_start', 'date_end', 'symbol_crypto']:
        st.session_state[key] = ''  # Réinitialise les champs du formulaire


# Page pour extraire les données historiques
def extract_histo_page():
    st.markdown("#### Choisir la période des transactions:")


    # Utiliser st.text_input avec les valeurs stockées dans st.session_state
    #st.markdown("**Date début**")
    st.markdown("""
                <div style='display: inline-block; font-weight: bold;'>Date début</div>
                """, unsafe_allow_html=True)
    date_start = st.text_input("Date début", value=st.session_state['date_start'], label_visibility="collapsed")
    st.caption("Exemple : 27/09/2024 00:00:00")

    st.markdown("""<br>
                <div style='display: inline-block; font-weight: bold;'>Date fin</div>
                """, unsafe_allow_html=True)
    date_end = st.text_input("Date fin", value=st.session_state['date_end'], label_visibility="collapsed")
    st.caption("Exemple : 29/09/2024 23:59:59")

    crypto_symbols = ['', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT']
    st.markdown("""<br>""", unsafe_allow_html=True)
    st.markdown("#### Choisir le symbole du crypto :")
    
    st.markdown("""<br>
                <div style='display: inline-block; font-weight: bold;'>Symbole du crypto</div>
                """, unsafe_allow_html=True)
    symbol_crypto = st.selectbox("Symbole du crypto", options=crypto_symbols, \
                                 index=crypto_symbols.index(st.session_state['symbol_crypto']) \
                                 , label_visibility="collapsed"
                                    )

    st.caption("Exemple : BTCUSDT")

    # Bouton pour soumettre le formulaire
    if st.button("Appliquer"):
        try:
            # Sauvegarder les nouvelles valeurs dans le session_state
            st.session_state['date_start'] = date_start
            st.session_state['date_end'] = date_end
            st.session_state['symbol_crypto'] = symbol_crypto

            # Convertir les entrées en flottants
            date_start_dt = datetime.strptime(date_start, "%d/%m/%Y %H:%M:%S")
            date_end_dt = datetime.strptime(date_end, "%d/%m/%Y %H:%M:%S")
            print("date_start_dt :", date_start_dt)
            print("date_end_dt :", date_end_dt)

            #requete dans une base de données
            #récupération des données
            conn = connect_to_db()
            mycursor = conn.cursor(dictionary=True)
            query = """
            SELECT *
            FROM T_CRYPTO_HIST
            WHERE 
            (closetime BETWEEN %s AND %s )
            AND (symbol = %s)
            LIMIT 100
            """
            mycursor.execute(query, (date_start_dt, date_end_dt, symbol_crypto))

            # Afficher la vue de la table sql
            # Stocker les résultats dans un DataFrame
            results = mycursor.fetchall()
            df = pd.DataFrame(results)

            mycursor.close()
            conn.close()

            if df.empty:
                st.warning("Aucune donnée trouvée pour cette période et ce symbole. Réessayer une autre période !")
            else:
                # Afficher les données sous forme de tableau
                st.dataframe(df)


        except ValueError:
            st.error("Veuillez entrer des dates et un symbole de crypto valides.")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")


    # Bouton pour réinitialiser le formulaire
    if st.button("Reset"):
        reset_form()  # Réinitialise toutes les variables dans le session state
        st.rerun()  # Recharge la page avec les nouvelles valeurs réinitialisées



def extract_stream_page():
    st.markdown("""
                En cours de construction ...
                """, unsafe_allow_html=True)

# Page d'accueil (Home)
def home_page():
    #st.title("Bienvenue sur l'application Crypto Transactions")
    st.markdown("<h1 style='font-family: Arial; font-size: 25px; color: #2C3E50;'>Bienvenue sur l'application Crypto Transactions</h1>", unsafe_allow_html=True)

    st.markdown("""
                <div>
                Ce projet a pour objectif de créer un bot de trading pour investir sur le marché des cryptomonnaies.
                A l’aide des méthodes de machine learning, nous avons développé des stratégies d’achat/vente.
                Cette application permet d'extraire et d'analyser les données de transactions historiques des cryptomonnaies.
                Utilisez le menu de navigation pour explorer les différentes fonctionnalités.
                </div>
                <div>
                <h1 style='font-family: Arial; font-size: 25px; color: #2C3E50;'>Bases de données</h1>
                Nous avons recolé les données (transactions) à l’aide de l’API Binance.
                Deux types de données nous ont intéressées : Les données historiques et les données en temps réel, connues sous le nom données streaming.
                </div>

                <div>
                <h1 style='font-family: Arial; font-size: 25px; color: #2C3E50;'>Machine Learning</h1>
                <ul>
                    <li>Le but de cette étape était d'appliquer des algorithmes de machine learning afin de prédire les tendences du marché en se basant sur les données historiques. </li>
                    <li>Cette étape de modélisation intevient aprés l'étape de collecte de données via l'API binance. </li>
                    <li>Pour récupérer ces données collectés on va établir une liaison avec la base de données préalablement dockerisée. </li>
                <ul>
                Nous avons testé deux approches de modélisation :
                <ul>
                    <li>une régression avec comme variable target le prix de clôture **'close_price'**. </li>
                    <li>une classification avec comme variable target **'is_profit'** qui représente l'équivalent de ('close_price' - 'open_price' ) / 'open_price' >= 0.01) qui prend True si l'action a atteint l'objectif de profit de 1% , False dans le cas contraire.  </li>
                </ul>
                </div>

                <div>
                <div>

                <div>
                <h1 style='font-family: Arial; font-size: 25px; color: #2C3E50;'>Documentation et liens utiles</h1>
                <ul>
                    <li>https://www.binance.com/fr/binance-api </li>
                    <li>https://developers.binance.com/docs/binance-open-api/apis </li>
                    <li>https://binance-docs.github.io/apidocs/spot/en/#change-log </li>
                </ul>
                </div>


                """
                , unsafe_allow_html=True)

# Fonction principale pour démarrer l'application
def run():
    st.title("CryptoBot avec Binance")

    # Barre de navigation latérale
    with st.sidebar:
        st.title("OPA")
        page = st.sidebar.radio("Choisissez une page", ["Accueil", "Données historiques","Données streaming"])

    if page == "Accueil":
        home_page()
    elif page == "Données historiques":
        extract_histo_page()
    elif page == "Données streaming":
        extract_stream_page()

# Exécuter l'application
if __name__ == '__main__':
    run()
