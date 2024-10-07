# CDE-NOV23-OPA  - CryptoBot avec Binance

## Présentation du projet

Ce projet a pour objectif de créer un bot de trading pour investir sur le marché des cryptomonnaies. A l’aide des méthodes de machine learning, nous allons développer des stratégies d’achat/vente et industrialiser leur déploiement.

## Auteur

- Oualid L.
- Samuel V.

## Schéma dossier

    .dockerignore
    │   ajout_test.py                                       <- Scripts pour tester le code
    │   binance_histo_crypto.py                             <- Scripts pour gérer l'historisation des mouvements de crypto monnaie
    │   binance_histo_symbol.py                             <- Scripts pour gérer l'ajout de nouvelle crypto
    │   Binance_Key.xml                                     <- xml pour mettre la clé APII Binance
    │   binance_maj_histo_crypto.py                         <- Scripts pour mettre à jour les données d'historisation
    │   docker-compose.yml                                  <- docker compose : fichier de configuration pour démarrer l'applicatif
    │   init.sql                                            <- script d'initialisation des bases mySQL
    │   main.py                                             <- Script main pour les points API (FAST API)
    │   my_dash.py                                          <- Script principal Dash
    │   README.md
    │
    ├───assets                                              <- éléments Dash pour la mise en page (css, images, etc..)
    │
    ├───binaries                                            <- Modèles entraînés et sérialisés, prédictions de modèles ou résumés de modèles
    │       rfc.sav
    │       rfr.sav
    │
    ├───dash                                                <- Docker Dash
    │       dockerfile
    │       requirements.txt                                <- Le fichier d'exigences
    │
    ├───docs                                                <- documentations
    │   │
    │   ├───archive
    │   │
    │   └───logo
    │
    ├───flask                                               <- Docker Flask
    │       dockerfile
    │       flask_api.py
    │       requirements.txt
    │
    ├───initdb
    │       init.sql
    │
    ├───streamlit                                           <- Docker Streamlit
    │       app.py
    │       dockerfile
    │       requirements.txt
    │
    ├───web                                                <- Docker Fastapi
    │       dockerfile
    │       requirements.txt
    │

## Démarrer le projet

1. mettre à jour le fichier `Binance_Key.xml` avec **vos clés API Binance**

``` python
    <Binance>
        <!-- Renseigner l'API Key -->
        <api_key>XXX</api_key>
        <!-- Renseigner l'API Secret> -->
        <api_secret>YYY</api_secret>
        <!-- Renseigner l'API Key testnet-->
        <api_key_testnet>ZZZ</api_key_testnet>
        <!-- Renseigner l'API Secret testnet> -->
        <api_secret_testnet>AAA</api_secret_testnet>
    </Binance> 
```

2. A la racine du projet, lancer dans un shell


 `docker compose up -d`
