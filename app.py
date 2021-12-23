import firebase_admin
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go

from flask import Flask, render_template, request, Response, make_response
from firebase_admin import credentials
from firebase_admin import db


app = Flask(__name__)
app.config.from_pyfile('settings.py')

cred = credentials.Certificate( app.config['CREDENTIALS'] )

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vehicledatacollected-default-rtdb.firebaseio.com/'
})

def line_chart(df, variable):
    near_crash_df = df.copy()
    no_crash_df = df.copy()
    x = df['timestamp']
    # Filter colums for eventClass
    near_crash_df.loc[df['eventClass'] == 0, variable] = None
    no_crash_df.loc[df['eventClass'] == 1, variable] = None
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
        title='Line Chart',
        xaxis_title='Marca de Tiempo',
        yaxis_title=variable,
        legend_title='Tipo de evento',
        template='plotly_white',
        autosize=True,
        height=450,
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

def pie_chart(df):
    df.rename(columns={'eventClass':'Tipo de Evento'}, inplace=True)
    df['Cantidad'] = 1
    df['Tipo de Evento'].replace([0,1],['Sin evento', 'Near-Crash'], inplace=True)
    
    fig = px.pie(df, values='Cantidad', names='Tipo de Evento', color='Tipo de Evento',
                 color_discrete_map={'Sin evento':'#00D1B1',
                                     'Near-Crash':'#FF385F'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        title={'text':'Porcentaje de eventos detectados en el viaje', 'x':0.5},
        legend_title='Tipo de evento',
        template="plotly_white",
        autosize=True,
        height=450,
        font=dict(
            family="BlinkMacSystemFont,-apple-system,Segoe UI,Roboto,Oxygen,Ubuntu, \
                Cantarell,Fira Sans,Droid Sans,Helvetica Neue,Helvetica,Arial,sans-serif",
            size=14,
            color='#363636'))
    
    return fig


@app.route("/")
def query_trips():
    ref = db.reference('/tripList')
    tripList = ref.get()
    data = {
        'title': 'Información de trayectos',
        'trips': {} if (tripList == None) else tripList
        #'smartphoneTrips': smartphoneTrips,
        #'raspberryTrips': raspberryTrips		
    }
    return render_template('index.html', **data)


@app.route("/trips/details/<id>", methods=["GET", "POST"])
def trip_details(id):    
    if request.method == 'GET':
        ref = db.reference('/tripList/' + str(id))
        trip = ref.get()
        
        trip_name = "-Mqwa3JkKT8ny9lxOPnm"
        data = {
            "trip": trip_name,
            "tripId": id,
            **trip
        }
        return render_template('charts.html', **data)
        
    elif request.method == 'POST':
        request_data = request.get_json()
        graphType = request_data['graph']
        variable = request_data['variable']

        #TODO: Obtener datos de firebase como dataframe
        df = pd.read_csv("./data/raspberry_-Mqwa3JkKT8ny9lxOPnm_data.csv")
        df["timestamp"] = pd.to_datetime(df['timestamp'], unit='s')

        # TODO: Reconocer graficos restantes
        fig = None
        if graphType == 'lineal':
            fig = line_chart(df, variable)
        elif graphType == 'pie':        
            fig = pie_chart(df)
        else:
            res = make_response(json.dumps({"code": 400, "error": "Invalid fields"}), 400)
            res.headers['Content-Type'] = 'application/json'
            return res

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    
    else:
        res = make_response(json.dumps({"code": 404, "error": "NOT FOUND"}), 404)
        res.headers['Content-Type'] = 'application/json'
        return res


@app.route("/removeTrip", methods=["DELETE"])
def remove_trip():
    request_data = request.get_json()
    idTrip = request_data['idTrip']
    device = request_data['device']
    response_data = {
            'result': ''
        }	
    try:
        #raise Exception('spam', 'eggs')
        ref = db.reference('/tripList/'+str(idTrip))
        ref.delete()
        ref = db.reference('/tripData/{}/{}'.format(device, idTrip))
        ref.delete()

        response_data['result'] = 'success'
        res = make_response(json.dumps(response_data), 200)
        res.headers['Content-Type'] = 'application/json'
        print("Data deleted: {} {}".format(request_data['device'], request_data['idTrip'] ) )
        return res

    except:
        response_data['result'] = 'error'
        res = make_response(json.dumps(response_data), 200)
        res.headers['Content-Type'] = 'application/json'
        return res