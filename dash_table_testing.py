from dash import Dash, html, Input, Output, callback, dash_table, dcc
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

import pandas as pd

import dash_ag_grid as dag

data = pd.read_csv("./aceh_production_data_daily_ed.csv")
a = {'type': 'dataframe', 'value': data.describe()}
result = a['value']

def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table

def create_aggrid(df):
    df_ag = df.to_dict('records')
    df_ag_columns = [
        {'field':i} for i in df.columns
    ]

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "Aceh Block Information (Dummy)"
app.layout = html.Section([
    html.Button('hit me', id='hitme-button'),
    html.Div(id='table-div')
])

@app.callback(
    Output('table-div', 'children'),
    Input('hitme-button', 'n_clicks')
)
def update_table(n):
    if n is None:
        raise PreventUpdate

    div_table = create_aggrid(result)
    return div_table

if __name__ == "__main__":
    app.run_server(debug=True, port=1234)
