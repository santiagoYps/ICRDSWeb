from threading import Semaphore
import firebase_admin

from flask import Flask, render_template
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

	smartphoneTrips = [trip for trip in tripList.values() if trip['device'] == 'Smartphone']
	raspberryTrips = [trip for trip in tripList.values() if trip['device'] == 'Raspberry']
	data = {
		'title': 'Información de trayectos',
		'smartphoneTrips': smartphoneTrips,
		'raspberryTrips': raspberryTrips		
	}
	return render_template('index.html', **data)