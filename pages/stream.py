# pages/streamCrypto.py
from dash import html, dcc, callback, Output, Input, register_page
from stream_data import live_trades  # Importer la liste globale avec les données

# Enregistrer la page avec le chemin '/streamCrypto'
register_page(__name__, path='/streamCrypto')
# Layout de la page
layout = html.Div([
    html.H2('Stream Crypto'),
    dcc.Interval(id='interval-component', interval=3*1000, n_intervals=0),  # Met à jour toutes les 10 secondes
    html.Div(id='live-data-btc'),  # Conteneur pour afficher les données BTC
    html.Div(id='live-data-eth'),  # Conteneur pour afficher les données ETH
    html.Div(id='live-data-bnb'),  # Conteneur pour afficher les données BNB
    html.Div(id='live-data-sol'),  # Conteneur pour afficher les données SOL
])

# Callback pour mettre à jour les données toutes les 10 secondes
@callback(
    Output('live-data-btc', 'children'),
    Output('live-data-eth', 'children'),
    Output('live-data-bnb', 'children'),
    Output('live-data-sol', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    btc_data = live_trades['btcusdt']  # Récupère les données pour BTC
    eth_data = live_trades['ethusdt']  # Récupère les données pour ETH
    bnb_data = live_trades['bnbusdt']  # Récupère les données pour BNB
    sol_data = live_trades['solusdt']  # Récupère les données pour SOL

    btc_output = 'Aucune donnée BTC disponible.'
    eth_output = 'Aucune donnée ETH disponible.'
    bnb_output = 'Aucune donnée BNB disponible.'
    sol_output = 'Aucune donnée SOL disponible.'

    if btc_data:
        latest_btc_trade = btc_data[-1]  # On affiche le dernier trade reçu pour BTC
        btc_output = html.Div([
            html.P(f"BTC Symbol: {latest_btc_trade['s']}"),
            html.P(f"BTC Price: {latest_btc_trade['p']}"),
            html.P(f"BTC Quantity: {latest_btc_trade['q']}")
        ])

    if eth_data:
        latest_eth_trade = eth_data[-1]  # On affiche le dernier trade reçu pour ETH
        eth_output = html.Div([
            html.P(f"ETH Symbol: {latest_eth_trade['s']}"),
            html.P(f"ETH Price: {latest_eth_trade['p']}"),
            html.P(f"ETH Quantity: {latest_eth_trade['q']}")
        ])

    if bnb_data:
        latest_bnb_trade = bnb_data[-1]  # On affiche le dernier trade reçu pour BNB
        bnb_output = html.Div([
            html.P(f"BNB Symbol: {latest_bnb_trade['s']}"),
            html.P(f"BNB Price: {latest_bnb_trade['p']}"),
            html.P(f"BNB Quantity: {latest_bnb_trade['q']}")
        ])

    if sol_data:
        latest_sol_trade = sol_data[-1]  # On affiche le dernier trade reçu pour SOL
        sol_output = html.Div([
            html.P(f"SOL Symbol: {latest_sol_trade['s']}"),
            html.P(f"SOL Price: {latest_sol_trade['p']}"),
            html.P(f"SOL Quantity: {latest_sol_trade['q']}")
        ])

    return btc_output, eth_output, bnb_output, sol_output