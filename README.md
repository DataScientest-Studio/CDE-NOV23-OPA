# CDE-NOV23-OPA  - CryptoBot avec Binance

## Présentation du projet

Ce projet a pour objectif de créer un bot de trading pour investir sur le marché des cryptomonnaies. A l’aide des méthodes de machine learning, nous allons développer des stratégies d’achat/vente et industrialiser leur déploiement.

## Auteur

- Oualid Lemtine
- Samuel Vicat

## Schéma dossier

    binaries/
    ├── rfc.sav
    ├── rfr.sav
    dash/
    ├── dockerfile
    ├── requirements.txt
    flask/
    ├── dockerfile
    ├── requirements.txt
    ├
    ├── Readme.md
    └── 

## Démarrer le projet

1. mettre à jour le fichier Binance_Key.xml avec vos clés API Binance

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

2. lancer dans un shell
 `docker compose up -d`
