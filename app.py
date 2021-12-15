from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go


app = Flask(__name__)


@app.route('/')
def charts():
    df = pd.read_csv("./data/raspberry_-Mqwa3JkKT8ny9lxOPnm_data.csv")
    df["timestamp"] = pd.to_datetime(df['timestamp'], unit='s')
    
    near_crash_df = df.copy()
    no_crash_df = df.copy()
    # TODO: Reconocer el grafico line,chart,pie, etc
    
    # line chart
    variable = "accZ"
    x = df["timestamp"]
    # Filter colums for eventClass
    near_crash_df[variable][df["eventClass"] == 1] = None
    no_crash_df[variable][df["eventClass"] == 0] = None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y = no_crash_df[variable],
        name = 'No event',
        #connectgaps=True # override default to connect the gaps
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=near_crash_df[variable],
        name='Near Crash',
    ))
    
    fig.update_layout(
        title="Line Chart",
        xaxis_title="Marca de Tiempo",
        yaxis_title=variable,
        legend_title="Tipo de evento",
        font=dict(
            family="poppins",
            size=18,
            color="gray"
        )
    )
    
    
    # Send graph to HTML
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    trip_name = "-Mqwa3JkKT8ny9lxOPnm"
    data = {
        "trip": trip_name,
        "graphJSON" : graphJSON
    }
    return render_template('index.html', **data)

app.run(debug=True, use_debugger=False, use_reloader=True)