import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import dash_table
import data as d
import main
from datetime import datetime as dt
from datetime import timedelta
import plotly.graph_objs as go
import all_country

temp = d.fetch_data()
countries = [i for i in temp]
countries.remove("MS Zaandam")
countries.remove("Holy See")
countries.remove("Diamond Princess")

cases_country, days = all_country.load_data()
time_step = 0

app = dash.Dash()

app.layout = html.Div(children=[
    html.Div(html.H1("COVID-19")),
    
    html.Div("Choose only one country at a time"),
    
    dcc.Dropdown(
        value=['a'],
        options=[{'label': i, 'value': i} for i in countries],
        multi=True,
        id='dropdown'
    ),
    dcc.DatePickerSingle(
        id='date-picker-single',
        date=dt(2020, 5, 10).date()
    ),
    
    html.Div(id='output-graph'),
    
    dcc.Graph(id="world-map"),
    dcc.Interval(
            id='graph-update',
            interval=1*200
        )
    
    ])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='dropdown', component_property='value'), Input('date-picker-single', 'date')]
)
def update_value(input_data, date):

    if len(input_data) == 0:
        pass    
    elif input_data[0] in countries:
        time, time_number_days, cases_ref, deaths_ref, recovered_ref = d.get_data(input_data[0])
        time_start = dt.strptime(time[0],'%Y-%m-%d').date()
        time_end = dt.strptime(time[len(time)-1],'%Y-%m-%d').date()
        date = dt.strptime(date,'%Y-%m-%d').date()
        extra = int((date-time_end).days)

        t = []
        for i in range((date - time_start).days + 1):
            day = time_start + timedelta(days=i)
            t.append(day)
        
        time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim = main.fit_country(input_data[0], extra)
        c = []
        r = []
        de = []
        i = 0
        while i < len(cases_sim):
            c.append(cases_sim[i])
            r.append(recovered_sim[i])
            de.append(deaths_sim[i])
            i = i + 2
        
        return dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': t, 'y': c, 'type': 'line', 'name': "CONFIRMED - simulated"},
                    {'x': t, 'y': r, 'type': 'line', 'name': "RECOVERED - simulated"},
                    {'x': t, 'y': de, 'type': 'line', 'name': "DEATHS - simulated"},
                    {'x': time, 'y': cases_ref, 'type': 'scattergl','mode': 'markers', 'name': "CONFIRMED - real"},
                    {'x': time, 'y': recovered_ref, 'type': 'scattergl','mode': 'markers', 'name': "RECOVERED - real"},
                    {'x': time, 'y': deaths_ref, 'type': 'scattergl', 'mode': 'markers', 'name': "DEATHS - real"},
                ],
                'layout': {
                    'title': input_data
                }
            }
        )
    else:
        return "Country name incorrect or does'nt exist in database"
    

@app.callback(
    Output("world-map", "figure"),
    [Input('graph-update', 'n_intervals')])
def update_figure(selected):
    global cases_country, time_step
    countries = list(cases_country.keys())
    cases = []
    for country in countries:
        cases.append(cases_country[country][time_step])
    date = days[time_step]
    trace = go.Choropleth(locations=countries,z=cases,text=countries,autocolorscale=False,
                          colorscale="amp",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.5,"x": 0.9,"y": 0.7,"nticks":10,
                                    'title': {"text": "Active cases - {}".format(date), "side": "bottom"}})
    if time_step == len(days) - 1:
        time_step = 0
    else:    
        time_step = time_step + 1
    return {"data": [trace],
            "layout": go.Layout(title="Active cases - {}".format(date),height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}

if __name__ == '__main__':
    app.run_server(debug=True)