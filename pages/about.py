from dash import html, register_page

# Enregistre la page avec le chemin '/about'
register_page(__name__, path='/about')

# Layout de la page
layout = html.Div([
    html.H2('À propos'),
    html.P('Voici la page À propos.')
])
