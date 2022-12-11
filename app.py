#########################################################################
# -= PACOTES UTILIZADOS =- #

# Carga, manipulação e operações com matrizes de dados
import pandas as pd

# Layout do Dashboard
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output


#########################################################################
# -= LAYOUT DO DASHBOARD =- #

# Instanciando o Dash
app = Dash(__name__)
server = app.server

# Constração do layout
app.layout = dbc.Container(children=[

    html.H3(children="Olá Mundo!")

], fluid=True, style={"height": "100%"})


#########################################################################
# -= END =- #
if __name__ == '__main__':
    app.run_server(debug=False)