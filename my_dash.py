from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash import page_registry, page_container

# Initialisation de l'application
app = Dash(__name__, use_pages=True)

# Layout principal avec navigation
app.layout = html.Div([
    html.Img(src= "/assets/binance1.png"),
    html.H1("Bienvenue sur l'Application du projet OPA - BINANCE"),
    html.H1("Tableau des Cryptomonnaies"),
    html.Nav([
        html.Ul([
            html.Li(dcc.Link('Home', href='/'), style={'margin-right': '20px', 'display': 'inline-block'}),
            html.Li(dcc.Link('Stream Crypto', href='/streamCrypto'), style={'margin-right': '20px', 'display': 'inline-block'}),
            html.Li(dcc.Link('About', href='/about'), style={'margin-right': '20px', 'display': 'inline-block'}),
        ])
    ]),
    dcc.Location(id='url', refresh=False),  # Permet de rediriger selon l'URL
    html.Div(id='page-content'),  # Conteneur pour le contenu de la page




# app.layout = html.Div([
#     html.Img(src= "/assets/binance1.png"),
#     html.H1("Bienvenue sur l'Application du projet OPA - BINANCE"),
#     html.H1("Tableau des Cryptomonnaies"),
#     html.Div([
#         html.Div(dcc.Link(page['name'], href=page['path']), style={'margin-right': '20px', 'display': 'inline-block'})
#         for page in page_registry.values()
#     ], style={'display': 'flex'}),  # Utilisation de flexbox pour aligner horizontalement
    html.Hr(),  # Ligne de séparation
    page_container  # Cet élément affichera la page courante
  
  
    #     dcc.Link(page['name'], href=page['path'])
    #     for page in page_registry.values()
    # ]),
    # page_container  # Cet élément affichera la page courante
])

# Lancer l'application
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)  # Démarrer Dash sur le port 8050
