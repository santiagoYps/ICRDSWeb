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

variables_dict = {'speed':'Velocidad','breakPosition':'Presión del freno',
                  'accX':'Aceleración en X', 'accY':'Aceleración en Y', 'accZ':'Aceleración en Z',
                  'magX':'Fuerza magnética en X','magY':'Fuerza magnética en Y','magZ':'Fuerza magnética en Z',
                  'velAngX':'Velocidad angular en X','velAngY':'Velocidad angular en Y','velAngZ':'Velocidad angular en Z'}
units_dict = {'speed':'m/s','breakPosition':'% de presión',
              'accX':'m/s\u00B2', 'accY':'m/s\u00B2', 'accZ':'m/s\u00B2',
              'magX':'\u03BC T','magY':'\u03BC T','magZ':'\u03BC T',
              'velAngX':'rad/seg','velAngY':'rad/seg','velAngZ':'rad/seg'}

def create_df(rows):
    # Create a data frame and set index by id
    df = pd.json_normalize(rows)
    df.set_index('id', inplace=True)
    df.sort_index(inplace=True)
    # CHange timestampt to human date
    df["timestamp"] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Bogota')
    return df

def update_layout(fig, chart_title:str, **kwargs):
    
    x_title= kwargs.get('xaxis_title', None)
    y_title= kwargs.get('yaxis_title', None)
    height_size = kwargs.get('height', 450)
    
    fig.update_layout(
        title={'text':chart_title, 'x':0.5},
        legend_title='Tipo de evento',
        xaxis_title=x_title,
        yaxis_title=y_title,
        template='plotly_white',
        autosize=True,
        height= height_size,
        font=dict(
            family="BlinkMacSystemFont,-apple-system,Segoe UI,Roboto,Oxygen,Ubuntu, \
                    Cantarell,Fira Sans,Droid Sans,Helvetica Neue,Helvetica,Arial,sans-serif",
            size=14,
            color="#363636"
        )
    )
    
    return fig

def line_chart(df, variable):
    near_crash_df = df.copy()
    no_crash_df = df.copy()
    x = df['timestamp']
    # Filter colums for eventClass
    near_crash_df.loc[df['eventClass'] == 0, variable] = None # Set all normal events to NaN
    no_crash_df.loc[df['eventClass'] == 1, variable] = None # Set all near-crash events to NaN
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y = no_crash_df[variable],
        name = 'Sin evento',
        marker_color='#00D1B1'
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=near_crash_df[variable],
        name='Near-Crash',
        marker_color='#FF385F'
    ))
    
    fig = update_layout(fig, f'Gráfico de linea de la {variables_dict[variable]}', 
                        xaxis_title= 'Marca de Tiempo', yaxis_title=units_dict[variable])
    fig.update_yaxes(nticks=12)
    fig.update_xaxes(nticks=12, tickangle=45)
    
    return fig

def histogram_chart(df, variable):
    df['eventClass'].replace([0,1],['Sin evento', 'Near-Crash'], inplace=True)
    
    fig = px.histogram(df, x=variable, color="eventClass", marginal="box", nbins=35, barmode="overlay",
                       color_discrete_map={'Sin evento':'#00D1B1',
                                           'Near-Crash':'#FF385F'})
    fig = update_layout(fig, f'Histograma de la {variables_dict[variable]}',
                        xaxis_title=units_dict[variable], yaxis_title='Repeticiones')
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
    fig = update_layout(fig, 'Porcentaje de eventos detectados en el viaje')
    
    return fig

def scatter_matrix_chart(df):
    df['eventClass'].replace([0,1],['Sin evento', 'Near-Crash'], inplace=True)
    
    # TODO: add the other values speed, pedal position, etc.
    fig = px.scatter_matrix(df, dimensions=["accX", "accY", "accZ",
                                            "magX", "magY", "magZ",
                                            "velAngX", "velAngY", "velAngZ"],
                            color="eventClass", symbol="eventClass",
                            color_discrete_map={'Sin evento':'#00D1B1',
                                                'Near-Crash':'#FF385F'})
    fig = update_layout(fig, 'Matriz de dipsersión',height=1000)
    return fig


@app.route("/")
def query_trips():
    ref = db.reference('/tripList')
    tripList = ref.get()
    data = {
        'title': 'Información de trayectos',
        'trips': {} if (tripList == None) else tripList
    }
    return render_template('index.html', **data)

@app.route("/trips/details/<id>", methods=["GET", "POST"])
def trip_details(id):    
    ref = db.reference('/tripList/' + str(id))
    trip = ref.get()
    
    if request.method == 'GET':
        trip_name = '-Mqwa3JkKT8ny9lxOPnm'
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
        # Get all trip data from firebase
        ref_trip = db.reference('/tripData/'+ str(trip['device']).lower() + "/" + str(id))
        # Transform json to dataframe
        rows = list(filter(None, ref_trip.get().values()))
        df = create_df(rows)
        # Julian data (Especial case)
        #rows = list(filter(None, ref_trip.get()))
        #df = create_df(rows)
        
        fig = None
        if graphType == 'lineal':
            fig = line_chart(df, variable)
        elif graphType == 'histogram':
            fig = histogram_chart(df, variable)
        elif graphType == 'pie':
            fig = pie_chart(df)
        elif graphType == 'scatter':
            fig = scatter_matrix_chart(df)
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
    response_data = {'result': ''}
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