'''
Nom : historical_data.py

Description: 
Code Python qui permet la récupération des données historiques de crypto monnaie

Créateur : OL
Date création :  01/03/2024


Modification :
    0.2 --> 0.3 : 03/03/2023 : SV : modification du script suite à sa recette
        > Création de l'en-tête de description
        > ajout commentaires et exemples
        > ajout import clef API via XML 


Version : 0.3
'''
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
    Binance_Key = Binance.find('api_key').text
    Binance_Secret = Binance.find('api_secret').text
    
# print('Key :',Binance_Key)
# Chargement des modules "Client" et "AscynClient" du package "python-binance"
from binance.client import Client, AsyncClient # dans Conda : pip install python-binance
# chargement du module pandas
import pandas as pd
# Clé et secret pour la connexion à l'API BINANCE
api_key = Binance_Key
api_secret = Binance_Secret 
# fonction de récupération de l'historique de token crypto
def import_historical_data(symbol: str , interval: str , datetime_start: str, datetime_end: str):
    """
        Récupère les données historiques de la paire de trading donnée à partir de l'API de Binance.
        Args:
            - symbol (str): Le bitcoin à récupérer 
            (par exemple, 'BTCUSDT','ETHBTC' ).
            - interval (str): L'intervalle de temps entre deux observations en minutes, heures...etc.
            (par exemple, 15 minutes : '15m', 1 heure : '1h', 1 jour: '1d').
            - datetime_start (str): date de début des extractions en datetime ('dd/MM/aaaa hh:mm:ss').
            (par exemple, '20/02/2024 08:00:00')
            - datetime_end (str): date de fin des extractions en datetime ('dd/MM/aaaa hh:mm:ss').
            (par exemple, '20/02/2024 16:00:00')
            
            - output : fichier csv : historical_data_{symbole}.csv dans le dossier de l'exécution du code
             (par exemple, historical_data_BTCUSDT.csv)
             
        Returns:
            pandas.DataFrame: Un DataFrame contenant les données historiques de la paire de trading.
        
        Exemple : import_historical_data('BTCUSDT','15m', '01/03/2024 08:00:00','01/03/2024 18:00:00')
        
        """
    # récupération des clefs privés de connexion API
    binance_client = Client(api_key, api_secret)
    # récupérations des datas Crypto 
    klines = binance_client.get_historical_klines(symbol, interval, datetime_start, datetime_end)
    
    # intégration dans un dataframe Pandas des datas crypto
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    # conversion en millisecond des données du Champ "timestamp"
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    # conversion en millisecond des données du Champ "Close_time"
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    # mise en index du champ "timestamp"
    df.set_index('timestamp', inplace=True)
    
    # création du nom du fichier CSV pour l'export
    filename = "historical_data_"+ symbol.lower() + ".csv"
    # export dans le fichier CSV
    df.to_csv(filename)
    
    return df, filename

# test de fonction
# test = import_historical_data('BTCUSDT','15m', '02/21/2024 08:00:00','02/23/2024 18:00:00')

