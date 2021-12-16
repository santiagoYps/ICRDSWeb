from threading import Semaphore
import firebase_admin
import json

from flask import Flask, render_template, request, Response, make_response
from firebase_admin import credentials
from firebase_admin import db

app = Flask(__name__)
app.config.from_pyfile('settings.py')

cred = credentials.Certificate( app.config['CREDENTIALS'] )

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://vehicledatacollected-default-rtdb.firebaseio.com/'
})

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

@app.route("/trips/details/<id>", methods=["GET"])
def trip_details(id):
	return "<p>"+str(id)+"</p>"


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

	
