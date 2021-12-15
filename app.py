from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def query_trips():
	data = {
		'title': 'Información de trayectos'
	}
	return render_template('index.html', **data)