from dash import Dash, html, dcc, Input, Output, dash_table, callback, State, ctx
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

openai_api_key = OPEN_AI_API_KEY
llm = OpenAI(api_token=openai_api_key)

df = pd.read_csv("./aceh_production_data_daily_ed.csv")

conv_hist = []

# -------------------------------- OpenAI --------------------------------

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "Aceh Block Information (Dummy)"
app.layout = html.Section(
    [
        dcc.Store(id='memory-output'),
        dmc.Card(
            className="Chatbot-card",
            withBorder=True,
            shadow="md",
            radius="lg",
            children=[
                html.Div(
                    className="div-zara",
                    children=[
                        dmc.Card(
                            className="left-card-zara",
                            withBorder=True,
                            shadow="sm",
                            radius="lg",
                            children=[
                                html.Div(
                                    className="container-inside-left-card-zara",
                                    children=[
                                        html.H1(
                                            "Zara IntelliSmart ChatBot",
                                            className="title-zara",
                                        ),
                                        html.Div(
                                            className="chip-container-zara1",
                                            children=[
                                                dmc.ChipGroup(
                                                    [
                                                        dmc.Chip(
                                                            x,
                                                            value=x,
                                                            color="grape",
                                                            variant="filled",
                                                            radius="lg",
                                                        )
                                                        for x in [
                                                            "Data Q&A",
                                                            "Document Q&A",
                                                            "Report AI",
                                                        ]
                                                    ],
                                                    id="chip-data-zara1",
                                                    value="Data Q&A",
                                                    multiple=False,
                                                )
                                            ],
                                        ),
                                        html.P(
                                            "A chatbot for you to build a quick data analysis without querying your data",
                                            className="desc-zara-1",
                                        ),
                                        html.P(
                                            "Choose and preview the data!",
                                            className="desc-zara-2",
                                        ),
                                        html.Div(
                                            className="chip-container-zara2",
                                            children=[
                                                dmc.SegmentedControl(
                                                    id="segmented",
                                                    radius="lg",
                                                    size="sm",
                                                    value="RAW Data",
                                                    data=[
                                                        "RAW Data",
                                                        "Oil Production Rate",
                                                        "Well Status",
                                                        "Daily Water Injection",
                                                        "Water Cut Daily Gas Ratio",
                                                        "Oil and Water Rate by Time",
                                                        "Choke Size and Avg Downhole Pressure",
                                                        "Well Log",
                                                    ],
                                                )
                                            ],
                                        ),
                                        html.Div(
                                            className="table-shown-data-qa",
                                            children=[
                                                dag.AgGrid(
                                                id="table-data-qa",
                                                defaultColDef={"resizeable": True, "sortable": True, "filter": True},
                                                dashGridOptions={"pagination": True},
)
                                                ],
                                        ),
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            className="chat-input-zara",
                            children=[
                                dmc.Textarea(
                                    className="chat-text-input-data-qa",
                                    id='chat-text-input-data-zara',
                                    placeholder="Write your question here",
                                    autosize=False,
                                    minRows=2,
                                    maxRows=2,
                                    variant="default",
                                    radius='lg',
                                    
                                ),
                                html.Div(className='div-action-button-stack-zara',
                                         children=[
                                             dmc.ActionIcon(
                                                 DashIconify(icon='formkit:submit', width=25),
                                                 id='send-chat-zara',
                                                 radius='md',
                                                 size=50,
                                                 variant='subtle',
                                                 color='gray',
                                                 n_clicks=0
                                                 )
                                         ]
                                         ),
                            ],
                        ),
                        html.Div(className="full-chatbot-layout-zara", children=[
                            dmc.Text(id='OutputHuman', children=''),
                            dmc.Text(id='OutputChatbot', children='')
                        ]
                            #      children=[
                            # dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=20), color='gray', radius='xl', size='sm', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className='grid-profile'),
                            #                    dmc.Col(html.Div(html.H4('Testing',style={'text-align':'left', 'width':'200px'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}),
                            # dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="lucide:bot", width=15), color='blue', radius='xl', size='sm', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className='grid-profile'),
                            #                    dmc.Col(html.Div(html.H4('response zara',style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'})
                            # ]
                                 ),
                    ],
                )
            ],
        )
    ],
)

#callback yang dipakai buat tampilin data perhitungan
@app.callback(
    Output('memory-output', 'data'),
    Output('table-data-qa', 'columnDefs'),
    Input('segmented','value')
)

def filter_table(calculation_chosen):
    if calculation_chosen == 'Water Cut Daily Gas Ratio':
        df['WATER_CUT_DAILY'] =(df['BORE_WAT_VOL'] / (df['BORE_OIL_VOL'] + df['BORE_GAS_VOL'] + df['BORE_WAT_VOL'])*100)
        df['GAS_OIL_RATIO'] = df['BORE_GAS_VOL'] / df['BORE_OIL_VOL']
        
        pivot_GOR = df.pivot_table(
            values=['WATER_CUT_DAILY', 'GAS_OIL_RATIO'],
            index=df['DATEPRD'],
            aggfunc='mean',
            dropna=True
        )
        
        data_GOR = pivot_GOR.reset_index().to_dict("records")
        
        column_GOR = [
            {"field": "DATEPRD"},
            {"field": "WATER_CUT_DAILY"},
            {"field": "GAS_OIL_RATIO"},
        ]
        
        return data_GOR, column_GOR
    
    df_original = df.to_dict('records')
    original_columns = [
        {"field": i} for i in df.columns if i not in ["WATER_CUT_DAILY", "GAS_OIL_RATIO"]
    ]
    return df_original, original_columns


# callback buat dataset yang dipakai sama aggrid
@app.callback(
    Output('table-data-qa', 'rowData'),
    Input('memory-output', 'data')
)

def table_dataset(dataset):
    if dataset is None:
        raise PreventUpdate
    
    return dataset

@app.callback(
    Output('OutputHuman', 'children'),
    Output('OutputChatbot', 'children'),
    Input('send-chat-zara', 'n_clicks'),
    State('chat-text-input-data-zara', 'value'),
    Input('memory-output','data')
)

def update_convo(n, human_prompt, data_chosen):
    if n is None and data_chosen is not None:
        return None, None
    
    else:
        call_API = SmartDataframe(data_chosen, config={'llm':llm, 'conversation':True})
        chatbot_resp = call_API.chat(human_prompt)
        
        return human_output, chatbot_output

if __name__ == "__main__":
    app.run_server(debug=True, port=1234)
