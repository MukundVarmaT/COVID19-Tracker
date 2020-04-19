import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from dash.dependencies import Input, Output
import main
import plotly.graph_objs as go


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
time_step = 60

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
map_box_key = "pk.eyJ1IjoibXVrdW5kdmFybWEiLCJhIjoiY2s5NTNubWUyMGpvdTNmb20wbmh5eHB5MCJ9.P6zlR2twAwpZNW-x_X-l3Q"

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
map_box_key = "pk.eyJ1IjoibXVrdW5kdmFybWEiLCJhIjoiY2s5NTNubWUyMGpvdTNmb20wbmh5eHB5MCJ9.P6zlR2twAwpZNW-x_X-l3Q"
colors = {
    'background': '#111111',
    'text': '#505050',
    "active": "#FFA500",
    "deaths": "#B22222",
    "recovered": "#008000",
    "graph-markers": "#505050"
}

app.layout = html.Div(style={'backgroundColor': colors['background'], 'height':'1450px'}, children=[
    # Main Heading
    html.H1(
        children='Tracking the COVID-19 pandemic',
        style={'textAlign': 'center','color': colors['active']}
    ),
    
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
    
    html.Div(html.H3("Worldwide Active Cases for the next 60 days"), 
             style={'width':'50%','display': 'inline-block','textAlign': 'center','color': colors['text']}),
    
    html.Div(html.H3("Worldwide Stats - Actual"), 
             style={'width':'50%','display': 'inline-block','textAlign': 'center','color': colors['text']}),
    
    dcc.Graph(id="world-map",  style={'width':'50%','display': 'inline-block',"textAlign":"left", "height":"600px"}),
    dcc.Interval(
        id='graph-update',
        interval=1*250
        ),
    dcc.Graph(
        id='stats',
        figure={'data': [stat],
                'layout' : go.Layout(
                            title='Click on the pie for details',
                            font={'color':colors['graph-markers']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )},
        style={'width':'50%','display': 'inline-block',"textAlign":"right", "height":"600px"}
    )
   
])

# The simulation Graph
@app.callback(
    Output(component_id='simulation graph', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'), Input('date-picker-single', 'date')]
)
def update_value(input_data, date):

    if len(input_data) == 0:
        temp = go.Scatter(
                x=[],
                y=[]
                ) 
        return {'data': [temp],
                'layout' : go.Layout(height=550,
                            title='Choose a Country',
                            font={'color':colors['graph-markers']},
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
                            font={'color':colors['graph-markers']},
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
                            font={'color':colors['graph-markers']},
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}  
@app.callback(
    Output("world-map", "figure"),
    [Input('graph-update', 'n_intervals')])
def update_worldmap(selected):
    global time_step
    if time_step == 0:
        time_step = 60
    cases = [COVID.all_simulated_data[x]["active"][-time_step] for x in COVID.all_simulated_data]
    data = go.Densitymapbox(lat=COVID.lat, lon=COVID.long, z=cases,radius=30)
    time_step = time_step - 1
    return {'data': [data],
            'layout' : go.Layout(
                            title="Active Cases on {}".format(datetime.datetime.now().date()+datetime.timedelta(days=60-time_step)),
                            mapbox=dict(accesstoken=map_box_key,style="dark"),
                            plot_bgcolor = colors['background'],
                            paper_bgcolor = colors['background'],
                            )}

@app.callback(Output('country-stats', 'figure'),
              [Input(component_id='dropdown', component_property='value')])
def update_pie(input_data):
    col = [colors[i] for i in ["active", "deaths", "recovered"]]
    if len(input_data) == 0:
        trace = go.Pie(labels=["Active Cases", "Recovered", "Dead"], values=[0,0,0],
                              marker=dict(colors = col))
        return {"data":[trace],'layout' : go.Layout(height=550,font={'color':colors['graph-markers']},
                                                    plot_bgcolor = colors['background'],
                                                    paper_bgcolor = colors['background'],
                                                  title="Choose Country",showlegend=False)}
    elif input_data[0] in COVID.countries:
        time_ref, cases_ref, deaths_ref, recovered_ref = COVID.country_real[input_data[0]].values()
        trace = go.Pie(labels=["Active Cases", "Recovered", "Dead"], values=[cases_ref[-1],deaths_ref[-1],recovered_ref[-1]],
                              marker=dict(colors = col))
        return {"data":[trace],'layout' : go.Layout(height=550,font={'color':colors['graph-markers']},
                                                    plot_bgcolor = colors['background'],
                                                    paper_bgcolor = colors['background'],
                                                  title="Actual Stats at {} on {}".format(input_data[0], datetime.datetime.now().date()),showlegend=True)}
    else:
        trace = go.Pie(labels=["Active Cases", "Recovered", "Dead"], values=[0,0,0],
                              marker=dict(colors = col))
        return {"data":[trace],'layout' : go.Layout(height=550,
                                                  title="Country doesn't exist in DataBase",showlegend=False,
                                                  font={'color':colors['graph-markers']},
                                                    plot_bgcolor = colors['background'],
                                                    paper_bgcolor = colors['background'])}


if __name__ == '__main__':
    app.run_server(debug=True)