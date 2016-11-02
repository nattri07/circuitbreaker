import logging
import urllib
import string
import random
from flask import request, json, Flask, render_template
from flask import jsonify, redirect
from cb.circuitbreaker import circuitBreaker
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry



import redis  				#import for demo function



DSN_URL = 'https://c6e82df45a6b4362a50f95a053d6d949:4918d4a757574a90812d7c4236adaa72@sentry.io/110511'


# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['SECRET_KEY'] = "random string"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


sentry = Sentry(app, logging=True, level=logging.INFO, dsn=DSN_URL)

redisDB = redis.Redis('localhost')				#dont need this in app as such
												#here to provide manual control over trip demo


db = SQLAlchemy(app)


class stuff(db.Model):
	id = db.Column('user_id', db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	reqType = db.Column(db.String(100))

	def __init__(self, name, email, reqType):
		self.name = name
		self.email = email
		self.reqType = reqType


cb=circuitBreaker()



# Define a route for the default URL, which loads the form
@app.route('/index')
@app.route('/')
def form():

    return render_template('form_submit.html')


#proxy function to issue post requests
@app.route('/postcaller', methods=['POST'])
def postcaller():

	name = request.form['yourname']
	email = request.form['youremail']

	sentry.captureMessage(request)

# our parameters
	params = dict(yourname=name, youremail=email)

	url_params = urllib.urlencode(params)
	callServ = cb.postreq(
										"http://127.0.0.1:5000/hello",
										headers={'Content-Type' : 'application/x-www-form-urlencoded'}, # Form type
										data=url_params) # post data

	sentry.captureMessage(callServ)
	return callServ._content



#proxy function to issue get requests
@app.route('/getcaller', methods=['GET'])
def getcaller():

	sentry.captureMessage(request)
	callServ = cb.getreq('http://127.0.0.1:5000/gethello', params=request.args)
	sentry.captureMessage(callServ)

	return callServ._content


##################################################################
### DEMO FUNCTIONS ####
##################################################################

@app.route('/manualControl')
def manualControl():

	return render_template('restoreList.html')




@app.route('/trippyStuff', methods=['POST'])
def trippyStuff():

	getStatus = request.form['getHello']
	postStatus = request.form['postHello']

	if getStatus == 'trip':
		redisDB.hset('circuitStatus', "('http://127.0.0.1:5000/gethello',)", 0)
	else:
		redisDB.hset('circuitStatus', "('http://127.0.0.1:5000/gethello',)", 1)

	if postStatus == 'trip':
		redisDB.hset('circuitStatus', "('http://127.0.0.1:5000/hello',)", 0)
	else:
		redisDB.hset('circuitStatus', "('http://127.0.0.1:5000/hello',)", 1)
	

	return redirect('/')

######################################################################################
######################################################################################


####function to fire 50 random requests

@app.route('/superfire')
def superfire():

	for i in range(1, 50):
		num = random.randrange(1, 3)			#randomly issue post or get request
		if num == 1:

			#random string generator
			name = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(5)])
			email = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(10)])
			reqType = "POST"

			params = dict(yourname=name,
						youremail=email,
						reqType=reqType)

			url_params = urllib.urlencode(params)
			callServ = cb.postreq(
					"http://127.0.0.1:5000/hello",
					headers={'Content-Type' : 'application/x-www-form-urlencoded'}, # Form type
					data=params # post data
					)

			sentry.captureMessage(callServ)

		elif num == 2:

			name = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(5)])
			callServ = cb.getreq('http://127.0.0.1:5000/gethello', params={'yourname':name})

			sentry.captureMessage(callServ)

	return render_template('DisplayAll.html',	entries=stuff.query.all())



#####################################################################################
##################################### EXTERNAL SERVICE
#####################################################################################


#GET simulation
@app.route('/gethello', methods=['GET'])
def gethello():

	name = request.args['yourname']

	num = random.randrange(0, 3)

	if num == 0:

		return jsonify({'Message': 'Sucbess', 'Name': name}), 200

	elif num == 1:

		return jsonify({'Message': '400 Errors', 'Name': name}), 400

	elif num == 2:

		return jsonify({'Message': '500 Errors', 'Name': name}), 500





# Responder Service (POST simulation)
@app.route('/hello', methods=['POST'])
def hello():

	num = random.randrange(0, 3)
	name = request.form['yourname']
	email = request.form['youremail']
	reqType = "POST"

	if num == 0:

		newStuff = stuff(name, email, reqType)
		db.session.add(newStuff)
		db.session.commit()
		return jsonify({'code': 200, "name": name, "email": email}), 200

	elif num == 1:
		return jsonify({"code":400, "name": name, "email": email}), 400

	elif num == 2:
		return jsonify({"code": 500, "name": name, "email": email}), 500




######################################################################################
######################################################################################


#written as a post method (which captures nothing actually)
#scaled to implement a queue of live requests

@app.route('/serviceDown', methods=['POST'])
def serviceDown():
	return render_template("400.html")


#small view to display all db entries 
@app.route('/test')
def test():
	return render_template('DisplayAll.html',	entries=stuff.query.all())

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True, threaded=True)
