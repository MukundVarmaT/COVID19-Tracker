# all import files!!
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from dash.dependencies import Input, Output
import main
import plotly.graph_objs as go
import flask
import os
import json
import random
import threading
import twitter_stream
from collections import deque
import numpy as np
import base64

# The app part!!
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

# Map box key!
map_box_key = "pk.eyJ1IjoibXVrdW5kdmFybWEiLCJhIjoiY2s5NTNubWUyMGpvdTNmb20wbmh5eHB5MCJ9.P6zlR2twAwpZNW-x_X-l3Q"

# Colors dictionary
colors = {
    'background': '#111111',
    'gray': '#505050',
    'text': '#505050',
    "active": "#FFA500",
    "deaths": "#B22222",
    "recovered": "#008000",
}
tabs_styles = {
    'height': '100%',
    "width" : "100%",
    'backgroundColor': colors["background"]
}
tab_style = {
    'backgroundColor': colors["background"],
    "color": "#FFFFFF",
}

tab_selected_style = {
    'borderTop': '5px solid {}'.format(colors["active"]),
    'backgroundColor': colors["background"],
    'color': colors["active"],
    'fontWeight': 'bold'
}

############################################
COVID = main.covid()
COVID.get_lat_long()
COVID.load_data()
active_now, deaths_now, recovered_now = COVID.get_stats()
stat =go.Sunburst(
    labels=["Deaths", "Recovered", "Active Cases"] + COVID.countries + COVID.countries + COVID.countries,
    parents=["", "", ""] + ["Deaths"]*len(COVID.countries) + ["Recovered"]*len(COVID.countries) + ["Active Cases"]*len(COVID.countries),
    values=[sum(deaths_now), sum(recovered_now), sum(active_now)] + deaths_now + recovered_now + active_now,
    marker=dict(
        colorscale='amp')
)
today = datetime.datetime.now().date()
time_step = 60
COVID.load_states()
cols = []
for i in range(len(COVID.selected_indian_states)):
    cols.append("%06x" % random.randint(0, 0xFFFFFF))
color_states = dict(zip(COVID.selected_indian_states,cols))

st_vis = []
cases = dict(zip(COVID.selected_indian_states,[COVID.selected_indian_data[x]["active"][-1] for x in COVID.selected_indian_states]))
cases = {k: v for k, v in sorted(cases.items(), key=lambda item: item[1])}
sts = list(cases.keys())[-5:-1]
for st in sts:
    time_ref, cases_ref, _, _ = COVID.selected_indian_data[st].values()
    days_real = COVID.convert_dates(time_ref[0], len(time_ref))
    st_vis.append(go.Scatter(
                x=days_real,
                y=cases_ref,
                mode="lines",
                name=st,
                line_color = "#" + color_states[st]
                ))
    

time_ref, cases_ref, _, _ = COVID.country_real["India"].values()
days_real = COVID.convert_dates(time_ref[0], len(time_ref))
st_vis.append(go.Scatter(
                x=days_real,
                y=cases_ref,
                mode="lines",
                name="India",
                line_color = colors["active"]
                ))

t = threading.Thread(target = twitter_stream.stream_tweets )
t.start()
while len(twitter_stream.tweet_csv) < 10:
    if len(twitter_stream.tweet_csv) == 5:
        print("Starting soon")
    pass


i = 0
X = deque(maxlen=20)
X.append(i)
Y = deque(maxlen=20)
Y.append(0)
pos_count = 0
nue_count = 0
neg_count = 0
test_png = 'data/wordcloud.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')
#############################################

# The app layout!
app.layout = html.Div(style={'backgroundColor': colors["background"], 'height':'100%'},
    children=[
    # The main heading
    html.H1('Tracking the COVID-19 Parameter', 
            style={'textAlign': 'center','color': colors['active']}),
    
    # The Tabs!    
    
    dcc.Tabs(id="tabs", children=[
        
        dcc.Tab(label='Worldwide Statistics', style=tab_style, selected_style=tab_selected_style, children=[
            ## Tab 1 content
            
            html.Div(html.H3("Simulate the Pandemic - Country wise"), 
             style={'width':'60%','display': 'inline-block','textAlign': 'center','color': colors['text']}),

            html.Div(
                dcc.Dropdown(
                value=['a'],
                options=[{'label': i, 'value': i} for i in COVID.countries],
                multi=True,
                id='dropdown'
            ),style={'width':'20%','display': 'inline-block',"horizontal-align":"left"}),

        
            dcc.DatePickerSingle(
                id='date-picker-single',
                date=datetime.datetime.now().date(),
                style = {"width":"100%", 'textAlign': 'center'}
            ),
            
            # The simulation graph
            dcc.Graph(id="simulation graph", style = {"width":"70%", 'display': 'inline-block',"textAlign":"left"}),
            
            html.Div([
                dcc.Graph(id='country-stats', animate=False),], style={'width':'30%','display': 'inline-block',"textAlign":"right"}),
            
            html.Div(html.H3("Worldwide Active Cases for next 60 days (Use slider)"), 
                    style={'width':'50%','display': 'inline-block','textAlign': 'center','color': colors['text']}),
            
            html.Div(html.H3("Worldwide Stats - Actual"), 
                    style={'width':'50%','display': 'inline-block','textAlign': 'center','color': colors['text']}),
            
            dcc.Graph(id="world-map",  style={'width':'50%','display': 'inline-block',"textAlign":"left", "height":"600px"}),

            dcc.Graph(
                id='stats',
                figure={'data': [stat],
                        'layout' : go.Layout(
                                    title='Click on the pie for details',
                                    font={'color':colors['gray']},
                                    plot_bgcolor = colors['background'],
                                    paper_bgcolor = colors['background'],
                                    )},
                style={'width':'50%','display': 'inline-block',"textAlign":"right", "height":"600px"}
            ),
            
            html.Div([dcc.Slider(
                id='slider-graph',
                min=0,
                max=60,
                step=1,
                value=10,
                marks={
                0: {'label': '{}'.format(today + datetime.timedelta(days=0))},
                10: {'label': '{}'.format(today + datetime.timedelta(days=10))},
                20: {'label': '{}'.format(today + datetime.timedelta(days=20))},
                30: {'label': '{}'.format(today + datetime.timedelta(days=30))},
                40: {'label': '{}'.format(today + datetime.timedelta(days=40))},
                50: {'label': '{}'.format(today + datetime.timedelta(days=50))},
                60: {'label': '{}'.format(today + datetime.timedelta(days=60))}
                })],
                style={'width':'60%','display': 'inline-block',"textAlign":"left"})         
            
        ]),
        
        
        dcc.Tab(label='Whats going on in India', style=tab_style, selected_style=tab_selected_style, children=[
            ## Tab 2 content
            html.Div(html.H3("Simulate - State wise"), 
             style={'width':'20%','display': 'inline-block','color': colors['text'], "textAlign":"left"}),
            
            html.Div(
                dcc.Dropdown(
                value=['a'],
                options=[{'label': i, 'value': i} for i in COVID.selected_indian_states],
                multi=True,
                id='dropdown-states'
            ),style={'width':'20%','display': 'inline-block', "textAlign":"center"}),
            
            html.Div(html.H3("Active cases in India now"), 
             style={'width':'40%','display': 'inline-block','color': colors['text'], "textAlign":"right"}),
            
            dcc.DatePickerSingle(
                id='date-picker-single-india',
                date=datetime.datetime.now().date(),
                style = {"width":"100%", 'textAlign': 'left'}
            ),
            
            dcc.Graph(id="simulation graph-india", style = {"width":"50%", 'display': 'inline-block',"textAlign":"left","height":"600px"}),
            
            
            
            dcc.Graph(id="india-map",  style={'width':'50%','display': 'inline-block','textAlign': 'right',"height":"600px"},
                      figure = {'data': [go.Densitymapbox(lat=COVID.indian_lat, lon=COVID.indian_long, z=[COVID.indian_data[x]["active"][-1] for x in COVID.indian_data],radius=50)],
                            'layout' : go.Layout(
                            title="Active Cases on {}".format(datetime.datetime.now().date()),
                            mapbox=dict(accesstoken=map_box_key,style="dark", center=dict(lat=20.5937,lon=78.9629), zoom=4),
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}),
            
            dcc.Graph(id="race-india", style = {"width":"50%", 'display': 'inline-block',"textAlign":"left"}),
            dcc.Interval(
                id='race-update',
                interval=1*200
            ),
            
            dcc.Graph(id="graph",
                      figure={'data': st_vis,
                            'layout' : go.Layout(
                                    title='Active Cases - Actual',
                                    font={'color':colors['gray']},
                                    plot_bgcolor = colors['background'],
                                    paper_bgcolor = colors['background'],
                                    )}, style = {"width":"50%", 'display': 'inline-block',"textAlign":"right"}
            )
                          
            
        ]),
        
        dcc.Tab(label='What people think', style=tab_style, selected_style=tab_selected_style, children=[
            ## Tab 3 content
            
            html.Div(html.H3("Sentiment Analysis - What people think about the COVID"), 
             style={'width':'100%','display': 'inline-block','color': colors['text'], "textAlign":"center"}),
            
            html.Div([
                dcc.Graph(id='sentiment-graph', animate=True),], style={'width':'50%','display': 'inline-block',"textAlign":"left"}),
            dcc.Interval(
                id='sentiment-update',
                interval=1*1500
            ),
            
            html.Div([
                dcc.Graph(id='sentiment-pie', animate=False),], style={'width':'50%','display': 'inline-block',"textAlign":"right"}),
            
            html.Div(id="recent-tweets-table", style={'width':'100%',"textAlign":"center"}),

            html.Div(html.H3("Word Cloud for positive sentiment"), 
             style={'width':'50%','display': 'inline-block','color': colors['text'], "textAlign":"left"}),
            
            html.Div(html.H3("Word Cloud for negative sentiment"), 
             style={'width':'50%','display': 'inline-block','color': colors['text'], "textAlign":"right"}),
            
            html.Div([
            html.Img(id = "wordcloud",src='data:image/png;base64,{}'.format(test_base64), style={'width':'100%',"textAlign":"center"})]),
            dcc.Interval(
                id='wordcloud-update',
                interval=1*10000
            ),
        ]),
        
        
        dcc.Tab(label='News', style=tab_style, selected_style=tab_selected_style, children=[
            ## Tab 4 content
        ]),
    ],style=tabs_styles
    )
])

############################################################ TAB 1

# The simulation Graph
@app.callback(
    Output(component_id='simulation graph', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'), Input('date-picker-single', 'date')]
)
def update_world_sim(input_data, date):

    if len(input_data) == 0:
        temp = go.Scatter(
                x=[],
                y=[]
                ) 
        return {'data': [temp],
                'layout' : go.Layout(height=550,
                            title='Choose a Country',
                            font={'color':colors['gray']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}  
    elif input_data[0] in COVID.countries:
        date = datetime.datetime.strptime(date,'%Y-%m-%d').date()
        extra = int((date-datetime.datetime.now().date()).days)
        time, sick, recovered, deaths = COVID.simulate_country(input_data[0], False, extra)
        time_ref, cases_ref, deaths_ref, recovered_ref = COVID.country_real[input_data[0]].values()
        days_real = COVID.convert_dates(time_ref[0], len(time_ref))
        days_sim = COVID.convert_dates(time_ref[0], len(time)) 
        
        
        data1 = go.Scatter(
                x=days_sim,
                y=sick,
                mode="lines",
                name='Active cases - simulated',
                line_color = colors["active"],
                )
        data2 = go.Scatter(
                x=days_sim,
                y=recovered,
                mode="lines",
                name='Recovered cases - simulated',
                line_color = colors["recovered"],
                )
        data3 = go.Scatter(
                x=days_sim,
                y=deaths,
                mode="lines",
                name='Death cases - simulated',
                line_color = colors["deaths"],
                )
        data4 = go.Scatter(
                x=days_real,
                y=cases_ref,
                mode="markers",
                name='Active cases',
                line_color = colors["active"],
                )
        data5 = go.Scatter(
                x=days_real,
                y=recovered_ref,
                mode="markers",
                name='Recovered cases - simulated',
                line_color = colors["recovered"],
                )
        data6 = go.Scatter(
                x=days_real,
                y=deaths_ref,
                mode="markers",
                name='Death cases - simulated',
                line_color = colors["deaths"],
                )


        return {'data': [data1,data2, data3, data4, data5, data6],
                'layout' : go.Layout(height=550,
                            title='{} till {}'.format(input_data[0], date),
                            font={'color':colors['gray']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}

    else:
        temp = go.Scatter(
                x=[],
                y=[]
                ) 
        return {'data': [temp],
                'layout' : go.Layout(height=550,
                            title='Choose a Country',
                            font={'color':colors['gray']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}  
@app.callback(
    Output("world-map", "figure"),
    [Input('slider-graph', 'value')])
def update_worldmap(value):
    t = 60 - int(value)
    cases = [COVID.all_simulated_data[x]["active"][-t] for x in COVID.all_simulated_data]
    data = go.Densitymapbox(lat=COVID.lat, lon=COVID.long, z=cases,radius=30)
    return {'data': [data],
            'layout' : go.Layout(
                            title="Active Cases on {}".format(datetime.datetime.now().date()+datetime.timedelta(days=60-t)),
                            mapbox=dict(accesstoken=map_box_key,style="dark"),
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}

@app.callback(Output('country-stats', 'figure'),
              [Input(component_id='dropdown', component_property='value')])
def update_country_pie(input_data):
    col = [colors[i] for i in ["active", "deaths", "recovered"]]
    if len(input_data) == 0:
        trace = go.Pie(labels=["Active Cases", "Recovered", "Dead"], values=[0,0,0],
                              marker=dict(colors = col))
        return {"data":[trace],'layout' : go.Layout(height=550,font={'color':colors['gray']},
                                                    plot_bgcolor = colors['background'],
                                                    paper_bgcolor = colors['background'],
                                                  title="Choose Country",showlegend=False)}
    elif input_data[0] in COVID.countries:
        time_ref, cases_ref, deaths_ref, recovered_ref = COVID.country_real[input_data[0]].values()
        trace = go.Pie(labels=["Active Cases", "Recovered", "Dead"], values=[cases_ref[-1],deaths_ref[-1],recovered_ref[-1]],
                              marker=dict(colors = col))
        return {"data":[trace],'layout' : go.Layout(height=550,font={'color':colors['gray']},
                                                    plot_bgcolor = colors['background'],
                                                    paper_bgcolor = colors['background'],
                                                  title="Actual Stats in {} as of {}".format(input_data[0], datetime.datetime.now().date()),showlegend=True)}
    else:
        trace = go.Pie(labels=["Active Cases", "Recovered", "Dead"], values=[0,0,0],
                              marker=dict(colors = col))
        return {"data":[trace],'layout' : go.Layout(height=550,
                                                  title="Country doesn't exist in DataBase",showlegend=False,
                                                  font={'color':colors['gray']},
                                                    plot_bgcolor = colors['background'],
                                                    paper_bgcolor = colors['background'])}

###################################################################



##########################################################################
# The simulation Graph
@app.callback(
    Output(component_id='simulation graph-india', component_property='figure'),
    [Input(component_id='dropdown-states', component_property='value'), Input('date-picker-single-india', 'date')]
)
def update_india_sim(input_data, date):

    if len(input_data) == 0:
        temp = go.Scatter(
                x=[],
                y=[]
                ) 
        return {'data': [temp],
                'layout' : go.Layout(height=550,
                            title='Choose a State',
                            font={'color':colors['gray']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}  
    elif input_data[0] in COVID.selected_indian_states:
        date = datetime.datetime.strptime(date,'%Y-%m-%d').date()
        extra = int((date-datetime.datetime.now().date()).days)
        time, sick, recovered, deaths = COVID.simulate_state(input_data[0], extra)
        time_ref, cases_ref, deaths_ref, recovered_ref = COVID.selected_indian_data[input_data[0]].values()
        days_real = COVID.convert_dates(time_ref[0], len(time_ref))
        days_sim = COVID.convert_dates(time_ref[0], len(time)) 
        
        
        data1 = go.Scatter(
                x=days_sim,
                y=sick,
                mode="lines",
                name='Active cases - simulated',
                line_color = colors["active"],
                )
        data2 = go.Scatter(
                x=days_sim,
                y=recovered,
                mode="lines",
                name='Recovered cases - simulated',
                line_color = colors["recovered"],
                )
        data3 = go.Scatter(
                x=days_sim,
                y=deaths,
                mode="lines",
                name='Death cases - simulated',
                line_color = colors["deaths"],
                )
        data4 = go.Scatter(
                x=days_real,
                y=cases_ref,
                mode="markers",
                name='Active cases',
                line_color = colors["active"],
                )
        data5 = go.Scatter(
                x=days_real,
                y=recovered_ref,
                mode="markers",
                name='Recovered cases - simulated',
                line_color = colors["recovered"],
                )
        data6 = go.Scatter(
                x=days_real,
                y=deaths_ref,
                mode="markers",
                name='Death cases - simulated',
                line_color = colors["deaths"],
                )


        return {'data': [data1,data2, data3, data4, data5, data6],
                'layout' : go.Layout(height=550,
                            title='{} till {}'.format(input_data[0], date),
                            font={'color':colors['gray']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}

    else:
        temp = go.Scatter(
                x=[],
                y=[]
                ) 
        return {'data': [temp],
                'layout' : go.Layout(height=550,
                            title='Choose a State',
                            font={'color':colors['gray']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}  
        
@app.callback(
    Output("race-india", "figure"),
    [Input('race-update', 'n_intervals')])
def update_race(selected):
    global time_step
    if time_step == 0:
        time_step = 60
    cases = dict(zip(COVID.all_simulated_states.keys(),[COVID.all_simulated_states[x]["active"][-time_step] for x in COVID.all_simulated_states]))
    cases = {k: v for k, v in sorted(cases.items(), key=lambda item: item[1])}
    
    cols = ["#"+color_states[s] for s in list(cases.keys())[-10:-1]]
    data = go.Bar(y=list(cases.keys())[-10:-1], x=list(cases.values())[-10:-1],
                marker_color=cols,
                 hoverinfo='none',
                textposition='outside', texttemplate='%{x}<br>%{y}',
                cliponaxis=False,orientation='h')
    layout = go.Layout(font={'size': 14, 'color':colors['gray']},
                    plot_bgcolor = colors['background'],
                    paper_bgcolor = colors['background'],
                    xaxis={'showline': False, 'visible': False},
                    yaxis={'showline': False, 'visible': False},
                    bargap=0.15,
                    title="Active Cases on {}".format(datetime.datetime.now().date()+datetime.timedelta(days=60-time_step)))
    time_step = time_step - 1
    return {"data":[data], "layout":layout}
##########################################################################


#########################################################################

@app.callback(Output('sentiment-graph', 'figure'),
              [Input('sentiment-update', 'n_intervals')])
def update_sentiment_graph(selected):
    global i, X, Y
    sent = np.mean(twitter_stream.tweet_csv["Sentiment"][0:i+4].values)
    if sent > 0:
        color = "green"
    elif sent == 0:
        color = "blue"
    else:
        color = "red"
    X.append(i)
    Y.append(sent)
    data = go.Scatter(x=list(X),y=list(Y),name='Scatter',mode= 'lines+markers', fill='tozeroy', line_color=color)
    i = i + 1
    return {'data': [data],'layout' : go.Layout(title="Average sentiment right now",
                                                xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(Y),max(Y)]),
                                                font={'color':colors['gray']},
                                                plot_bgcolor = colors['background'],
                                                paper_bgcolor = colors['background'])}
    
@app.callback(Output('sentiment-pie', 'figure'),
              [Input('sentiment-update', 'n_intervals')])
def update_sentiment_pie(selected):
    global pos_count, nue_count, neg_count, i
    sent = twitter_stream.tweet_csv["Sentiment"][i]
    if sent > 0:
        pos_count = pos_count + 1
    elif sent == 0:
        nue_count = nue_count + 1
    else:
        neg_count = neg_count + 1
    col = ['#007F25', "#add8e6",'#800000']
    trace = go.Pie(labels=["Positive", "Nuetral", "Negative"], values=[pos_count,nue_count,neg_count],
                              marker=dict(colors = col))
    return {"data":[trace],'layout' : go.Layout(title="Positive, Nuetral & Negative sentiment",showlegend=True,
                                                font={'color':colors['gray']},
                                                plot_bgcolor = colors['background'],
                                                paper_bgcolor = colors['background'])}
    
def quick_color(s):
    if s > 0:
        return "#90EE90"
    elif s < 0:
        return "#FF6666"
    else:
        return "#6666ff"

def generate_table(df, max_rows=5):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values]
                                  )
                              ),
                          html.Tbody(
                              [
                                  
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'background-color':quick_color(d[1])}
                                  )
                               for d in df.values.tolist()])
                          ]
    )
    
@app.callback(
              Output('recent-tweets-table','children'),
            [Input('sentiment-update', 'n_intervals')])
def update_recent_tweets(sentiment_term):
    global i
    df = twitter_stream.tweet_csv[i:i+5]
    return generate_table(df, max_rows=5)

@app.callback(Output("wordcloud", "src"),
             [Input('wordcloud-update', 'n_intervals')])
def update_body_image(hover_data):
    global i
    data = twitter_stream.tweet_csv[i:i+10]
    data = data.reset_index(drop=True)
    twitter_stream.data_to_cloud(data)
    test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')
    src = src='data:image/png;base64,{}'.format(test_base64)
    return src
#######################################################################









# The main file!
if __name__ == '__main__':
    app.run_server(debug=True)