import json
import os
from turtle import width

import firebase_admin
import pandas as pd
import numpy as np
from scipy import stats as st
from machine_learning.pykalman import KalmanFilter
from joblib import load

import plotly
import plotly.express as px
import plotly.graph_objects as go
from firebase_admin import credentials, db
from flask import (Flask, Response, abort, make_response, render_template,
                   request, send_from_directory)

# Init flask app
app = Flask(__name__)
app.config.from_pyfile('settings.py')

cred = credentials.Certificate( app.config['CREDENTIALS'] )

# Firebase intialization
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vehicledatacollected-default-rtdb.firebaseio.com/'
})

# Dicts with variables translates
variables_dict = {'speed':'Velocidad','accPosition':'Presión del acelerador',
                  'accX':'Aceleración en X', 'accY':'Aceleración en Y', 'accZ':'Aceleración en Z',
                  'magX':'Fuerza magnética en X','magY':'Fuerza magnética en Y','magZ':'Fuerza magnética en Z',
                  'velAngX':'Velocidad angular en X','velAngY':'Velocidad angular en Y','velAngZ':'Velocidad angular en Z'}
units_dict = {'speed':'m/s','accPosition':'% de presión',
              'accX':'m/s\u00B2', 'accY':'m/s\u00B2', 'accZ':'m/s\u00B2',
              'magX':'\u03BC T','magY':'\u03BC T','magZ':'\u03BC T',
              'velAngX':'rad/seg','velAngY':'rad/seg','velAngZ':'rad/seg'}

def create_df(firebase_data):
    """Create a DataFrame with a json from firebase

    Args:
        firebase_data (dict or list): all captured data for the device,
        each item in the list contains a JSON data (dict) or a list of all data

    Returns:
        DataFrame: a dataframe with all kinematic variable in its columns
    """
    # Check type of data (list or dict) for manage the logic to transform json to dataframe
    rows = list(filter(None, firebase_data.values())) if isinstance(firebase_data, dict) else filter(None, firebase_data)
    # Create a data frame and set index by id
    df = pd.json_normalize(rows)
    df.set_index('id', inplace=True)
    df.sort_index(inplace=True)
    # Change timestampt to human date
    df["timestamp"] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('America/Bogota')
    # Check if the eventClass column is boolean or int
    if (df.dtypes['eventClass'] == bool):
        df['eventClass'] = df['eventClass'].astype('int64')
    return df

def update_layout(fig, chart_title:str, **kwargs):
    """Update layout for every chart

    Args:
        fig: A plotly figure
        chart_title (str): A title for chart

    Returns:
        fig: the updated layout for the plotly figure
    """
    # Get kwards data if is needed
    x_title= kwargs.get('xaxis_title', None)
    y_title= kwargs.get('yaxis_title', None)
    height_size = kwargs.get('height', 450)
    
    # Update layout of the figure
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
    """Line chart created with plotly graphic object

    Args:
        df (DataFrame): The dataframe that contains the data to plot
        variable (str): The specific variable to plot

    Returns:
        fig: A plotly figure
    """
    # Create a copy of the data frame to avoid losing important data
    near_crash_df = df.copy()
    no_crash_df = df.copy()
    x = df['timestamp']
    # Filter colums for eventClass
    near_crash_df.loc[df['eventClass'] == 0, variable] = None # Set all variables where have a normal events to NaN
    no_crash_df.loc[df['eventClass'] == 1, variable] = None # Set all variables where have a near-crash events to NaN
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y = no_crash_df[variable],
        name = 'Sin evento',
        marker_color='#00D1B1',
        text= no_crash_df.index,
        hovertemplate="X = %{x}<br>Y = %{y}<br>ID = %{text}"
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=near_crash_df[variable],
        name='Near-Crash',
        marker_color='#FF385F',
        text=near_crash_df.index,
        hovertemplate="X = %{x}<br>Y = %{y}<br>ID = %{text}"
    ))
    
    fig = update_layout(fig, f'Gráfico de linea de la {variables_dict[variable]}', 
                        xaxis_title= 'Marca de Tiempo', yaxis_title=units_dict[variable])
    fig.update_yaxes(nticks=12)
    fig.update_xaxes(nticks=12, tickangle=45)
    
    return fig

def histogram_chart(df, variable):
    """Histogram chart created with plotly express

    Args:
        df (DataFrame): The dataframe that contains the data to plot
        variable (str): The specific variable to plot

    Returns:
        fig: A plotly figure
    """
    df['eventClass'].replace([0,1],['Sin evento', 'Near-Crash'], inplace=True)
    
    fig = px.histogram(df, x=variable, color="eventClass", marginal="box", nbins=35, barmode="overlay",
                       color_discrete_map={'Sin evento':'#00D1B1',
                                           'Near-Crash':'#FF385F'})
    fig = update_layout(fig, f'Histograma de la {variables_dict[variable]}',
                        xaxis_title=units_dict[variable], yaxis_title='Repeticiones')
    fig.update_xaxes(nticks=12, tickangle=45)
    
    return fig

def pie_chart(df):
    """Pie chart created with plotly express

    Args:
        df (DataFrame): The dataframe that contains the data to plot

    Returns:
        fig: A plotly figure
    """
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
    """Scatter matrix chart created with plotly express

    Args:
        df (DataFrame): The dataframe that contains the data to plot

    Returns:
        fig: A plotly figure
    """
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

def sliding_windows(df, features, window_size=20):
    """Create a sliding window with a defined window size and return the calculation for each record inside the sliding window.

    The calculations made are for each time window: 
    - The mean.
    - The median.
    - The standard deviation.
    - The maximum and minimum value.
    - The trend.

    Note the process is explained in greater detail in: <TODO: reference link>

    Args:
        dataset (numpy.array): An array with the data taken on a vehicle trip, 
        composed for rows: dataset registers and columns: first data index, and subsequent dataset event features.
        window_size (int, optional): number Number of registers contained in the time window. Defaults to 10.
        event_features (str, optional): the names of dataset features. Defaults to "X".

    Returns:
        tuple: A tuple structured like this: (sliding window id, sliding window featured data, sliding window label data, features name)
    """
    features = ["id", *features,  "eventClass"]
    dataset = df[features].to_numpy()

    sld_window = np.lib.stride_tricks.sliding_window_view(dataset, window_size, axis=0) #[::1, :] Add this for define window step

    # Splitin dataset id
    id = sld_window[:,0:1,:]
    sld_window_id = np.concatenate((id[:,:,0], id[:,:,-1]), axis=1) # get the first and last id from registers in every sliding window

    # Spliting the dataset (features, label)
    separator = dataset.shape[1] - 1 # Split the last page corresponding to the eventClass
    features_data = sld_window[:, 1:separator, :] # Get the features of the data in every sliding window
    label_data = sld_window[:, separator, :] # Get the labels of the data in every sliding window

    # Processing the sliding window
    # Get the mean, median, std, max and min value
    mean = features_data.mean(axis=2)
    median = np.median(features_data, axis=2)
    std = features_data.std(axis=2)
    max_val = features_data.max(axis=2)
    min_val = features_data.min(axis=2)
    # Get tendency
    divider = np.array([mean[0], *mean[:-1]])
    tendency = mean/np.where(divider == 0, 1, divider)
    label = st.mode(label_data, axis=1)[0]

    # Concatenate processed sliding window
    sld_window_features = np.concatenate((mean, median, std, max_val, min_val, tendency), axis=1)
    # Reshape label for sklearn standard
    label = label.reshape(label.shape[0])

    # Make input algorithm df
    X = pd.DataFrame(sld_window_features)
    X[["first","last"]] = sld_window_id
    X.set_index(["first","last"], inplace=True)

    return (X, label)

def data_filter(df_filter):
    """Make Kalman filter to specified features for a dataset

    Args:
        df (Pandas.DataFrame): The dataframe with driving data

    Returns:
        Pandas.DataFrame: The dataframe with driving data transformed through the Kalman Filter
    """
    features = ["accX", "accY", "velAngZ", "magX", "magY"]
    for var in features:
        data = df_filter[var]

        # Kalman filter process
        kf = KalmanFilter(initial_state_mean = data.iloc[0], n_dim_obs=1)
        filter_data = kf.em(data).filter(data)[0].T[0]
        filter_data_s = pd.Series(np.array(filter_data), name=var)
        df_filter[var] = filter_data_s

        # Normalized magnetometer data with min-max normalization
        if var == "magX" or var =="magY":
            normalized_data = (data-data.min())/(data.max()-data.min())
            df_filter[var] = normalized_data
    return df_filter

@app.route("/")
def query_trips():
    """Query trips, get data from trips and show

    Returns:
        template: render template for index.html with all necesarry data
    """
    ref = db.reference('/tripList')
    tripList = ref.get()
    data = {
        'title': 'Información de trayectos',
        'trips': {} if (tripList == None) else tripList
    }
    return render_template('index.html', **data)

@app.route("/trips/details/<id>", methods=["GET", "POST"])
def trip_details(id):
    """Trip details, get info and plot all data from one trip

    Args:
        id (str): id from firebase

    Returns:
        template: render template for charts.html with all necesarry data
    """
    ref = db.reference('/tripList/' + str(id))
    trip = ref.get()
    if not("tripLocalId" in trip):
        trip['tripLocalId'] = '-';
    
    if request.method == 'GET':
        trip_name = str(id)
        data = {
            "title": "Datos del viaje: ",
            "trip": trip_name,
            "tripId": id,
            **trip
        }
        return render_template('charts.html', **data)
        
    elif request.method == 'POST':
        # get data from fetch in javascript
        request_data = request.get_json()
        graphType = request_data['graph']
        variable = request_data['variable']
        # Get all trip data from firebase
        ref_trip = db.reference('/tripData/'+ str(trip['device']).lower() + "/" + str(id))
        firebase_data = ref_trip.get()
            
        # Transform json to dataframe if firebase returns a dict
        df = create_df(firebase_data)
        
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
    """Remove a trip

    Returns:
        res: A response to frontend
    """
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
    
@app.route('/download/<string:data_id>')
def download_csv(data_id):
    """[summary]

    Args:
        data_id (str): A string with the trip id

    Returns:
        [type]: [description]
    """
    # Get trip info from firebase
    ref = db.reference('/tripList/' + data_id)
    trip = ref.get()
    
    device_name = str(trip['device']).lower()
    route_name = str(trip['route']).lower()
    
    # Get trip data from firebase
    ref_trip = db.reference('/tripData/'+ device_name + "/" + data_id)
    # Transform json to dataframe
    firebase_data = ref_trip.get()
    df = create_df(firebase_data)

    # Formating date trip
    date = trip["date"].split(" ")
    time = date[1].split(":") 
    trip_date = str(date[0] + "-" + time[0] + "-" + time[1])
    
    # Generate the CSV file
    csv_name = device_name + "_" + trip_date + "_" + route_name + "_Data" + data_id + ".csv"
    df.to_csv(f"./data/{csv_name}",index=True)
    #uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    # Returning file from appended path
    try:
        return send_from_directory(app.config['CSV_PATH'], path=csv_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# Check near crash routes
@app.route('/checkNearCrash/<string:data_id>')
def check_nearcrash(data_id):
    """[summary]
    """
    # Get trip info from firebase
    ref = db.reference('/tripList/' + data_id)
    trip = ref.get()
    
    device_name = str(trip['device']).lower()
    route_name = str(trip['route']).lower()

    # Get trip data from firebase
    ref_trip = db.reference('/tripData/'+ device_name + "/" + data_id)
    # Transform json to dataframe
    firebase_data = ref_trip.get()
    df = create_df(firebase_data)

    # TODO: before filter is need to manage the offset of the data, for this reason in the experiments we need to make a standby time
    max_standby = 80
    var_with_offset = ["accY","accX"]
    for var_offset in var_with_offset:
        offset = df.iloc[:max_standby][var_offset].mean()
        df[var_offset] = df[var_offset] - offset

    df["id"] = df.index
    df.reset_index(drop=True, inplace=True)

    # Algorithms and combinantions
    clasifiers = ["clf_sudden_braking_smartphone", "clf_sudden_braking_raspberry",
                  "clf_sudden_acceleration_smartphone", "clf_sudden_acceleration_raspberry",
                  "clf_chg_line_right_smartphone", "clf_chg_line_right_raspberry",
                  "clf_chg_line_left_smartphone", "clf_chg_line_left_raspberry",
                  "clf_agg_turn_right_smartphone", "clf_agg_turn_right_raspberry",
                  "clf_agg_turn_left_smartphone", "clf_agg_turn_left_raspberry"]
    features = [["speed","accY"], ["speed","accY"],
                ["speed","accY"], ["speed", "accPosition", "accY"],
                ["accX", "velAngZ"], ["accX", "velAngZ"],
                ["accX", "velAngZ"], ["accX", "velAngZ"],
                ["accX" ,"accY", "velAngZ", "magX", "magY"], ["speed", "accX", "accY", "velAngZ", "magX"],
                ["accX" ,"accY", "velAngZ", "magX", "magY"], ["speed", "accX", "accY", "velAngZ", "magX"]]

    if device_name == "smartphone":
        clasifiers = clasifiers[::2]
        features = features[::2]
    else:
        clasifiers = clasifiers[1::2]
        features = features[1::2]

    # Make filter kalman for all data
    print("filter kalman")
    df_filtered = data_filter(df)
    print("exit kalman")
    # Check near crash
    near_crash = {}
    for c, f in zip(clasifiers, features):
    #Make sliding window
        X, y = sliding_windows(df_filtered, f, 40)

        # Check near-crash
        clf = load(str("./machine_learning/built_algorithms/"+c+".joblib"))
        y_predict = clf.predict(X.values)
        y_predict_proba = clf.predict_proba(X.values)[:,1]

        if (len(np.where(y_predict == 1.0)[0]) != 0):
            near_crash_df = X.iloc[np.where(y_predict == 1.0)[0]]
            near_crash[c] = near_crash_df
    print("Cantidad de eventos detectados {}, Eventos: [{}]".format(len(near_crash), near_crash.keys()))
    stepsize = 1
    for id in near_crash.values():
        data = id.index.get_level_values('first')
        print("Id de los datos:\n",data)
        nc = np.split(data.values, np.where(np.diff(data.values) != stepsize)[0]+1)
        print("Near crash split:\n",nc)
