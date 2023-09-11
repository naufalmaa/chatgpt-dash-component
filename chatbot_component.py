from dash import Dash, html, dcc, Input, Output, dash_table, callback, State, ctx
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pandas as pd
import time

#for key
import openai_api_key

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

import chartgpt as cg

from io import StringIO

openai_api_key = openai_api_key.KEY
llm = OpenAI(api_token=openai_api_key)

df = pd.read_csv("./aceh_production_data_daily_ed.csv")

conv_hist = []

def contains_word(text, word_list):
    for word in word_list:
        if text.find(word) != -1:
            return True
    return False

word_list = ['table', 'summary', 'summerize']
plot_list = ['plot']

def create_table(df):
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return table

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
                                            "Zara IntelliSmart Assistant",
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
                                            "An assistant for you to build a quick data analysis without querying your data",
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
                                                className='ag-theme-alpine',
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
                                    placeholder="Write your question here...",
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
                        # dmc.LoadingOverlay
                        html.Div(className="full-chatbot-layout-zara", children=[
                            dmc.LoadingOverlay(
                            html.Div(id='response-chatbot'),
                                loaderProps={'variant':'dots', 'color':'dark','size':'xl'},
                                overlayBlur=2,
                                overlayColor='#F5F4F4'
                            )
                        ]
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
    Output('response-chatbot', 'children'),
    Input('send-chat-zara', 'n_clicks'),
    State('chat-text-input-data-zara', 'value'),
    Input('memory-output','data')
)

def update_convo(n, human_prompt, data_chosen):
    
    button_click = ctx.triggered_id
    global conv_hist
    
    if button_click == 'send-chat-zara':
        time.sleep(1)
        
        if contains_word(human_prompt.lower(), word_list):
            call_API = SmartDataframe(data_chosen, config={'llm':llm})
            chatbot_resp = call_API.chat(human_prompt)
            
            bot_table_output = f"{chatbot_resp}"
            df_ = pd.read_csv(StringIO(bot_table_output), delim_whitespace=True, header=0, index_col=0)
            df_ = df_.transpose()
            df_.reset_index(inplace=True)
            
            # final_table = dag.AgGrid(className='ag-theme-alpine',
            #                          rowData=df_.to_dict('records'), 
            #                          columnDefs=[{'field': i} for i in df_.columns],
            #                         defaultColDef={"resizeable": True, "sortable": True, "filter": True})
            final_table = dmc.Table(create_table(df_))

            whole_div = html.Div(children=[
                dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=40), color='gray', radius='xl', size='40px', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className='grid-profile'),
                                                dmc.Col(html.Div(html.H4(human_prompt,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div'),
                dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:face-agent", width=40), color='blue', radius='xl', size='40px', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className='grid-profile'),
                                                dmc.Col(html.Div([final_table]), className='grid-chat-for-table')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div')
                ])
            
            conv_hist.append(whole_div)
            
            return conv_hist
        
        elif contains_word(human_prompt.lower(), plot_list):
            dfchart = pd.DataFrame(data_chosen)
            chart = cg.Chart(dfchart, api_key=openai_api_key)
            fig = chart.plot(human_prompt, return_fig=True)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            graph_bot = dcc.Graph(figure=fig)

            whole_div = html.Div(children=[
                dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=40), color='gray', radius='xl', size='40px', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className='grid-profile'),
                                                dmc.Col(html.Div(html.H4(human_prompt,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div'),
                dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:face-agent", width=40), color='blue', radius='xl', size='40px', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className='grid-profile'),
                                                dmc.Col(html.Div(graph_bot), className='grid-chat-for-table')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div')
                ])
            
            conv_hist.append(whole_div)
            
            return conv_hist
        
        else:
            call_API = SmartDataframe(data_chosen, config={'llm':llm})
            chatbot_resp = call_API.chat(human_prompt)
            
            whole_div = html.Div(children=[
                dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:user-outline", width=40), color='gray', radius='xl', size='40px', style={'border': '2px solid #868E96', 'border-radius':'50%'})), span='content',className='grid-profile'),
                                                dmc.Col(html.Div(html.H4(human_prompt,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div'),
                dmc.Grid(gutter='xs', children=[dmc.Col(html.Div(dmc.Avatar(DashIconify(icon="mdi:face-agent", width=40), color='blue', radius='xl', size='40px', style={'border': '2px solid #53A5EC', 'border-radius':'50%'})), span='content', className='grid-profile'),
                                                dmc.Col(html.Div(html.H4(chatbot_resp,style={'text-align':'left'})), className='grid-chat')], style={'padding':'5px 0px 5px 0px'}, className='chat-full-div')
            ])
            
            conv_hist.append(whole_div)
            
            return conv_hist
    
    else:
        return None

if __name__ == "__main__":
    app.run_server(debug=True, port=1234)
