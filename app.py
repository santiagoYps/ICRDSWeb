from flask import Flask, render_template, request
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go


app = Flask(__name__)

def line_chart(df):
    near_crash_df = df.copy()
    no_crash_df = df.copy()
    variable = "accY"
    x = df["timestamp"]
    # Filter colums for eventClass
    near_crash_df.loc[df["eventClass"] == 0, variable] = None
    no_crash_df.loc[df["eventClass"] == 1, variable] = None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y = no_crash_df[variable],
        name = 'No event',
        marker_color='#00D1B1'
        #connectgaps=True # override default to connect the gaps
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=near_crash_df[variable],
        name='Near Crash',
        marker_color='#FF385F'
    ))
    
    fig.update_layout(
        title="Line Chart",
        xaxis_title="Marca de Tiempo",
        yaxis_title=variable,
        legend_title="Tipo de evento",
        template="plotly_white",
        autosize=True,
        height=600,
        font=dict(
            family="BlinkMacSystemFont,-apple-system,Segoe UI,Roboto,Oxygen,Ubuntu, \
                    Cantarell,Fira Sans,Droid Sans,Helvetica Neue,Helvetica,Arial,sans-serif",
            size=14,
            color="#363636"
        )
    )
    fig.update_yaxes(nticks=12)
    fig.update_xaxes(nticks=12, tickangle=45)
    
    return fig

@app.route('/')
def charts():
    
    # TODO: change for data listed
    trip_name = "-Mqwa3JkKT8ny9lxOPnm"
    df = pd.read_csv("./data/raspberry_-Mqwa3JkKT8ny9lxOPnm_data.csv")
    df["timestamp"] = pd.to_datetime(df['timestamp'], unit='s')
    
    fig = line_chart(df)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    data = {
        "trip": trip_name,
        "graphJSON": graphJSON
    }
    # TODO: Reconocer el grafico line,chart,pie, etc
    
    if request.method == 'POST':
        req = request.get_json()
        
        if req["chart"] == "line":
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            data = {
                "trip": trip_name,
                "graphJSON": graphJSON
            }
            return render_template('index.html', **data)-
        else:
            return render_template('index.html', **data)
        
    else:
        return render_template('index.html', **data)
        
    # line chart
    
    
    
    # Send graph to HTML

app.run(debug=True, use_reloader=True)