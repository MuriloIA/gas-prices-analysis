#######################################################################################
# -= PACOTES UTILIZADOS =-

# Manipulação e operações com matrizes de dados
import numpy as np
import pandas as pd

# Construção de gráficos
import plotly.express as px
import plotly.graph_objects as go

# Ferramentas para a construção do Dashboard
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO


#######################################################################################
# -= CARGA E PRÉ-PROCESSAMENTO DOS DADOS =-

def load_data():

    """
        Carga e pré-processamento dos dados. 
            - Função não paramética.
    """

    # Carregando os dados em um DataFrame do Pandas
    url   = "https://raw.githubusercontent.com/asimov-academy/Dashboards/main/gas-prices-dash/data_gas.csv"
    dados = pd.read_csv(url)

    # Erro no nome da coluna
    dados.rename(columns={' DATA INICIAL': 'DATA INICIAL'}, inplace=True)

    # Estabelecendo datas, simplificando-as estabelecendo a ordem do DF por elas
    dados['DATA INICIAL'] = pd.to_datetime(dados['DATA INICIAL'])
    dados['DATA FINAL']   = pd.to_datetime(dados['DATA FINAL'])
    dados['DATA MEDIA']   = ((dados['DATA FINAL'] - dados['DATA INICIAL'])/2) + dados['DATA INICIAL']
    dados                 = dados.sort_values(by='DATA MEDIA',ascending=True)
    dados.rename(columns = {'DATA MEDIA':'DATA'}, inplace = True)
    dados.rename(columns = {'PREÇO MÉDIO REVENDA': 'VALOR REVENDA (R$/L)'}, inplace=True)

    # Criando uma coluna de Ano
    dados["ANO"] = dados["DATA"].apply(lambda x: str(x.year))

    # Resetando o index por uma questão organizacional
    dados = dados.reset_index()

    # Filtrando pois só falaremos da gasolina comum
    dados = dados[dados.PRODUTO == 'GASOLINA COMUM'] # ou podemos deixar todos os produtos e depois utilizar como um filtro geral !!!!

    # Excluindo colunas que não usaremos
    dados.drop(['UNIDADE DE MEDIDA', 'COEF DE VARIAÇÃO REVENDA', 'COEF DE VARIAÇÃO DISTRIBUIÇÃO', 
        'NÚMERO DE POSTOS PESQUISADOS', 'DATA INICIAL', 'DATA FINAL', 'PREÇO MÁXIMO DISTRIBUIÇÃO', 'PREÇO MÍNIMO DISTRIBUIÇÃO', 
        'DESVIO PADRÃO DISTRIBUIÇÃO', 'MARGEM MÉDIA REVENDA', 'PREÇO MÍNIMO REVENDA', 'PREÇO MÁXIMO REVENDA', 'DESVIO PADRÃO REVENDA', 
        'PRODUTO', 'PREÇO MÉDIO DISTRIBUIÇÃO'], inplace=True, axis=1)

    # Retornando os dados já organizados
    return dados

# Chamando a função load_data()
dados = load_data()

# Transformando o DataFrame em um dicionário
df_store = dados.to_dict()


#######################################################################################
# -= CONSTRUÇÃO DO LAYOUT DO DASHBOARD =-

# Definindo os parâmetros gerais para todos os gráficos com plotly
main_config = {
    "hovermode": "x unified",
    "legend": {
        "yanchor": "top",
        "y": 0.9,
        "xanchor": "left",
        "x": 0.1,
        "title": {"text": None},
        "font": {"color": "white"},
        "bgcolor": "rgba(0, 0, 0, 0.5)"},
    "margin": {"l": 0, "r": 0, "t": 10, "b": 0}
}

# Definindo um estilo para todos os cards
tab_card = {"height": "100%"}

# Definindo os temas opcionais para este projeto
template_theme1 = "flatly"
template_theme2 = "vapor"
theme1 = dbc.themes.FLATLY
theme2 = dbc.themes.VAPOR

# Importando Estilo css para os objetos do dash_bootstrap_components
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")

# Instanciando o Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, dbc_css])
server = app.server

# Constração do layout
app.layout = dbc.Container(children=[

    # Armazenando os Datasets do projeto
    dcc.Store(id="dataset", data=df_store),
    dcc.Store(id="dataset_fixed", data=df_store),

    # -= LINHA 1 =-
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Legend(children="Análise de Preços de Gás")
                        ], sm=8),
                        dbc.Col([
                            html.I(className="fa fa-gas-pump", style={"font-size": "300%"})
                        ], sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[theme1, theme2]),
                            html.Legend(children="Asimov Academy")
                        ])
                    ], style={"magin-top": "10px"}),
                    dbc.Row([
                        dbc.Button(children="Visite o Site", href="https://asimov.academy/", target="_blank")
                    ], style={"margin-top": "10px"}),
                    html.P(children="© Murilo Rocha", style={"text-align": "center"})
                ])
            ], style=tab_card)
        ], sm=4, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3(children="Máximos e Mínimos"),
                            dcc.Graph(id="static_maxmin", config={"displayModeBar": False, "showTips": False})
                        ])
                    ])
                ])
            ], style=tab_card)
        ], sm=8, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6(children="Ano de análise:"),
                            dcc.Dropdown(
                                id="select_ano",
                                value=dados.at[dados.index[3], 'ANO'],
                                clearable=False,
                                className="dbc",
                                options=[
                                    {"label": x, "value": x} for x in dados['ANO'].unique()
                                ]
                            )
                        ], sm=6),
                        dbc.Col([
                            html.H6(children="Região de análise"),
                            dcc.Dropdown(
                                id="select_regiao",
                                value=dados.at[dados.index[1], 'REGIÃO'],
                                clearable=False,
                                className="dbc",
                                options=[
                                    {"label": x, "value": x} for x in dados["REGIÃO"].unique()
                                ]
                            )
                        ], sm=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="regiaobar_graph", config={"displayModeBar": False, "showTips": False})
                        ], sm=12, md=6),
                        dbc.Col([
                            dcc.Graph(id="estadobar_graph", config={"displayModeBar": False, "showTips": False})
                        ], sm=12, md=6)
                    ], style={"column-gap": "0px"})
                ])
            ], style=tab_card)
        ], sm=12, lg=7)
    ], class_name="g-2 my-auto")
], fluid=True, style={"height": "100%"})


#########################################################################
# -= END =- #
if __name__ == '__main__':
    app.run_server(debug=False)