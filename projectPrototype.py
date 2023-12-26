#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import date, datetime, timedelta
import pymysql.cursors
import hashlib
import random

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='dbproject',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def dateCheckFunc(date):
	today = datetime.now().date()
	if(date < today):
		return True
	else:
		return False

@app.route('/', methods = ['GET', 'POST'])
def hello():
    return render_template('index.html')

@app.route('/customerLogin')
def customerLogin():
	return render_template('customerLogin.html')

@app.route('/staffLogin')
def staffLogin():
	return render_template('staffLogin.html')

@app.route('/customerRegister')
def customerRegister():
	return render_template('customerRegister.html')

@app.route('/staffRegister')
def staffRegister():
	return render_template('staffRegister.html')

@app.route('/staffAddCreatePage')
def staffAddCreatePage():
	return render_template('staffAddCreatePage.html')

@app.route('/staffViewPage')
def staffViewPage():
	return render_template('staffViewPage.html')

@app.route('/customerFlightReviewPage')
def customerFlightReviewPage():
	cursor = conn.cursor()
	query = "SELECT flightNum, customerComment, rating FROM Review WHERE email = %s"
	cursor.execute(query, (session['email']))
	posts = cursor.fetchall()
	email = session['email']
	cursor = conn.cursor()
	today = datetime.now().date()
	dateRange = today - timedelta(days = 183)
	monthDate = today
	months = [0] * 6
	monthsSpent = [0]  * 6
	for x in range(6):
		preMonthDate = monthDate
		monthDate = monthDate - timedelta(days = 30)
		months[x] = monthDate.month
		query = "SELECT SUM(ticketPrice) FROM Ticket WHERE email = %s and flightNum in(SELECT flightNum FROM Flight WHERE departDate BETWEEN %s and %s)"
		cursor.execute(query, (email, monthDate, preMonthDate))
		dummy = cursor.fetchone()
		if(dummy == None):
			monthsSpent[x] = 0
		else:
			monthsSpent[x] = dummy['SUM(ticketPrice)']
		
	query = "SELECT SUM(ticketPrice) FROM Ticket WHERE email = %s and flightNum in(SELECT flightNum FROM Flight WHERE departDate BETWEEN %s and %s)"
	cursor.execute(query, (email, dateRange, today))
	print(today)
	data = cursor.fetchone()
	return render_template('customerFlightReviewPage.html', posts = posts, totalSpent = data['SUM(ticketPrice)'], monthData = months, monthsSpent = monthsSpent, length = 6)

@app.route('/searchByAirports', methods = ['GET', 'POST'])
def searchByAirports():
	departAirportID = request.form['departAirportID']
	arrivalAirportID = request.form['arrivalAirportID']
	today = datetime.now().date()
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE departAirportID = %s and arrivalAirportID = %s and departDate > %s'
	cursor.execute(query, (departAirportID, arrivalAirportID, today))
	data = cursor.fetchall()
	if(data):
		return render_template('index.html', data = data)
	else:
		error = "There are no flights of said condition"
		return render_template('index.html', error = error)

@app.route('/searchByDate', methods = ['GET', 'POST'])
def searchByDate():
	departDate = request.form['departDate']
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE departDate = %s'
	cursor.execute(query, (departDate))
	data = cursor.fetchall()
	if(data):
		return render_template('index.html', data = data)
	else:
		error = "There are no flights of said condition"
		return render_template('index.html', error = error)
	
@app.route('/customerFlightSearch', methods =['GET', 'POST'])
def customerFlightSearch():
	departAirportID = request.form['departAirportID']
	departDate = request.form['departDate']
	departDate = datetime.strptime(departDate, '%Y-%m-%d').date()
	arrivalAirportID = request.form['arrivalAirportID']
	cursor = conn.cursor()
	query = "SELECT AirlineName, flightNum, departDate, arrivalDate, departAirportID, arrivalAirportID, flightStatus FROM Flight NATURAL JOIN Ticket WHERE email = %s and departAirportID = %s and arrivalAirportID = %s and departDate = %s"
	cursor.execute(query, (session['email'], departAirportID, arrivalAirportID, departDate))
	data = cursor.fetchall()
	flightType = request.form["oneWayOrRound"]
	if(data):
		if(flightType == 'roundTrip'):
			query = C
			cursor.execute(query, (session['email'], arrivalAirportID, departAirportID))
			returnFlightData = cursor.fetchall()
			return render_template('customerViewPage.html', data = data, returnFlightData = returnFlightData)
		else:
			return render_template('customerViewPage.html', data = data)
		#return render_template('customerViewPage.html', data = data)
	else:
		error = "Flight Does Not Exist"
		return render_template('customerViewPage.html', searchError = error)


@app.route('/purchaseTicket', methods =['GET', 'POST'])
def purchaseTicket():
	flightNum = request.form['flightNum']
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE flightNum = %s'
	cursor.execute(query, (flightNum))
	data = cursor.fetchone()
	if(data == None):
		error = "This flight number doesn't exist"
		return render_template('customerViewPage.html', purchaseError = error)

	query = 'SELECT flightNum FROM Ticket WHERE email = %s and flightNum = %s'
	cursor.execute(query, (session['email'], flightNum))
	data = cursor.fetchone()
	if(data['flightNum'] == flightNum):
		error = "You already purchased the ticket"
		return render_template('customerViewpage.html', purchaseError = error)
	else:
		ticketID = 0
		while(ticketID == 0):
			ticketID = random.randint(10000, 99999)
			checkIfTicketIDExist = "SELECT ticketID FROM Ticket"
			cursor.execute(checkIfTicketIDExist)
			ticketIDArr = cursor.fetchall()
			for each in ticketIDArr:
				if ticketID == each['ticketID']:
					ticketID = 0
		cardType = request.form['paymentType']
		cardNo = request.form['cardNo']
		cardName = request.form['cardName']
		expDate = request.form['expDate']
		ticketPriceQuery = "SELECT basePrice FROM Flight WHERE flightNum = %s"
		cursor.execute(ticketPriceQuery, (flightNum))
		ticketPrice = cursor.fetchone()
		custInfoQuery = "SELECT firstName, lastName FROM Customer WHERE email = %s"
		cursor.execute(custInfoQuery, (session['email']))
		custData = cursor.fetchone()
		ins = "INSERT INTO Ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(ins, (ticketID, flightNum, custData['firstName'], custData['lastName'], session['email'], ticketPrice['basePrice'], cardType, cardNo, cardName, expDate))
		conn.commit()
		ins = "INSERT INTO Purchase VALUES(%s, %s, %s)"
		current_date = datetime.now().strftime('%Y-%m-%d')
		cursor.execute(ins, (ticketID,session['email'], current_date))
		conn.commit()
		notification = "Purchase successfully made"
		return render_template('customerViewPage.html', purchaseNotification = notification)
	
@app.route('/cancelFlight', methods = ['GET', 'POST'])
def cancelFlight():
	flightNum = request.form['flightNum']
	dateCheck = "SELECT departDate FROM Flight WHERE flightNum = %s"
	cursor = conn.cursor()
	cursor.execute(dateCheck, (flightNum))
	dateData = cursor.fetchone()
	if(dateData == None):
		error = "There is no such flight"
		return render_template('customerViewPage.html', cancelError = error)
	
	if(dateCheckFunc(dateData['departDate'])):
		error = "This Flight is in the past"
		return render_template('customerViewPage.html', cancelError = error)
	
	date = dateData['departDate'] + timedelta(days = 1)
	if(dateCheckFunc(date)):
		error = "Flight is in less than 24 hours"
		return render_template('customerViewPage.html', cancelError = error)
	
	else:
		ticketIDquery = "SELECT ticketID from Ticket WHERE flightNum = %s"
		cursor.execute(ticketIDquery, (flightNum))
		ticketID = cursor.fetchone()
		if(ticketID == None):
			error = "You don't have tickets to this flight"
			return render_template('customerViewPage.html', cancelError = error)
		purchaseDeleteQuery = "DELETE FROM Purchase WHERE ticketID = %s"
		cursor.execute(purchaseDeleteQuery, (ticketID['ticketID']))
		conn.commit()
		query = "DELETE FROM Ticket WHERE flightNum = %s"
		cursor.execute(query, (flightNum))
		conn.commit()
		notification = "Flight Successfully Cancelled"
		return render_template('customerViewPage.html', cancelNotification = notification)
	
@app.route('/postCustomerReview', methods = ['GET', 'POST'])
def postCustomerReview():
	flightNum = request.form['flightNum']
	cursor = conn.cursor()
	flightCheckQuery = "SELECT * FROM Ticket WHERE email = %s and flightNum = %s"
	cursor.execute(flightCheckQuery, (session['email'], flightNum))
	flightCheck = cursor.fetchone()
	if(flightCheck == None):
		error = "You weren't on this flight"
		return render_template('customerFlightReviewPage.html', error = error)
	datecheckQuery = "SELECT departDate FROM Flight WHERE flightNum = %s"
	cursor.execute(datecheckQuery, (flightNum))
	dateCheck = cursor.fetchone()
	if(dateCheckFunc(dateCheck['departDate'])):
		error = "This flight didn't happen yet"
		return render_template('customerFlightReviewPage.html', error = error)
	rating = request.form['rating']
	customerComment = request.form['customerComment']
	ins = "INSERT INTO Review VALUES (%s, %s, %s, %s)"
	cursor.execute(ins, (flightNum, session['email'], customerComment, rating))
	conn.commit()
	query = "SELECT flightNum, customerComment, rating FROM Review WHERE email = %s"
	cursor.execute(query, (session['email']))
	posts = cursor.fetchall()
	return render_template('customerFlightReviewPage.html', posts = posts)

@app.route('/customerViewPage')
def customerViewPage():
	email = session['email']
	today = datetime.now().date()
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE departDate > %s and flightNum in (SELECT flightNum FROM Ticket WHERE email = %s)'
	cursor.execute(query, (today, email))
	data = cursor.fetchall()
	print(data)
	if(data):
		return render_template('customerViewPage.html', data = data)
	else:
		error = "There are no flights of said condition"
		return render_template('customerViewPage.html', error = error)
	#return render_template('customerViewPage.html')

@app.route('/viewSpending', methods =['GET', 'POST'])
def view():
	email = session['email']
	cursor = conn.cursor()
	beginDate = request.form['beginDate']
	endDate = request.form['endDate']
	query = "SELECT SUM(ticketPrice) FROM Ticket WHERE email = %s and flightNum in(SELECT flightNum FROM Flight WHERE departDate BETWEEN %s and %s)"
	cursor.execute(query, (email, beginDate, endDate))
	data = cursor.fetchone()
	monthDate = datetime.strptime(endDate, '%Y-%m-%d').date()
	indexHelp = datetime.strptime(endDate, '%Y-%m-%d').date() - datetime.strptime(beginDate, '%Y-%m-%d').date()
	index = indexHelp.days // 30
	print(monthDate)
	months = [0] * index
	monthsSpent = [0]  * index
	for x in range(index):
		preMonthDate = monthDate
		monthDate = monthDate - timedelta(days = 30)
		print(monthDate)
		months[x] = monthDate.month
		print(months[x])
		query = "SELECT SUM(ticketPrice) FROM Ticket WHERE email = %s and flightNum in(SELECT flightNum FROM Flight WHERE departDate BETWEEN %s and %s)"
		cursor.execute(query, (email, monthDate, preMonthDate))
		dummy = cursor.fetchone()
		if(dummy == None):
			monthsSpent[x] = 0
		else:
			monthsSpent[x] = dummy['SUM(ticketPrice)']

	return render_template('customerFlightReviewPage.html', totalSpent = data['SUM(ticketPrice)'], monthData = months, monthsSpent = monthsSpent, length = len(months))

@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	email = request.form['email']
	password = request.form['password']
	password = hashlib.md5(password.encode())
	print(password.hexdigest())
	cursor = conn.cursor()
	query = 'SELECT email, password FROM Customer WHERE email = %s and password = %s'
	cursor.execute(query, (email, password.hexdigest()))
	data = cursor.fetchone()
	cursor.close()
	error = None

	if(data):
		session['email'] = email
		return redirect(url_for('customerViewPage'))
	else:
		error = "Invalid login or username"
		return render_template('customerLogin.html', error = error)
	
	
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
	email = request.form['email']
	password = request.form['password']
	password = hashlib.md5(password.encode())
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	buildingNum = request.form['buildingNum']
	streetName = request.form['streetName']
	aptNum = request.form['aptNum']
	city = request.form['city']
	state = request.form['state']
	zipCode = request.form['zipCode']
	phoneNum = request.form['phoneNum']
	cursor = conn.cursor()
	query = 'SELECT email, password FROM Customer WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	if(data):
		error = "This customer already exists in our database"
		return render_template('customerRegister.html', error = error)
	else:
		ins = 'INSERT INTO Customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, password.hexdigest(), firstName, lastName, buildingNum, streetName, aptNum, city, state, zipCode, phoneNum))
		conn.commit()
		return render_template('index.html')

@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def staffRegisterAuth():
	username = request.form['username']
	password = request.form['password']
	password = hashlib.md5(password.encode())
	print(password.hexdigest())
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	birthDate = request.form['birthDate']
	AirlineName = request.form['AirlineName']
	staffEmail = request.form['staffEmail']
	staffPhoneNum = request.form['staffPhoneNum']
	cursor = conn.cursor()
	airlineCheckQuery = "SELECT AirlineName FROM Airline WHERE AirlineName = %s"
	cursor.execute(airlineCheckQuery, (AirlineName))
	data = cursor.fetchone()
	if(data == None):
		error = "There is no Airline of such"
		return render_template('staffRegister.html', error = error)
	query = 'SELECT username, password FROM AirlineStaff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	if(data):
		error = "This staff already exists in our database"
		return render_template('staffRegister.html', error = error)
	else:
		ins = 'INSERT INTO AirlineStaff VALUES (%s, %s, %s, %s, %s, %s)'
		#birthDate = date(int(birthDateYear), int(birthDateMonth), int(birthDateDay))
		cursor.execute(ins, (username, password.hexdigest(), firstName, lastName, birthDate, AirlineName))
		conn.commit()
		ins = 'INSERT INTO AirlineStaffEmail VALUES (%s, %s)'
		cursor.execute(ins, (username, staffEmail))
		conn.commit()
		ins = 'INSERT INTO AirlineStaffPhoneNum VALUES (%s, %s)'
		cursor.execute(ins, (username, staffPhoneNum))
		conn.commit()
		return render_template('index.html')

@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
	username = request.form['username']
	password = request.form['password']
	password = hashlib.md5(password.encode())
	cursor = conn.cursor()
	query = 'SELECT username, password FROM AirlineStaff WHERE username = %s and password = %s'
	cursor.execute(query, (username, password.hexdigest()))
	data = cursor.fetchone()
	error = None

	if(data):
		session['username'] = username
		query = 'SELECT airlineName FROM AirlineStaff WHERE username = %s'
		cursor.execute(query, (username))
		airlineName = cursor.fetchone()
		session['airlineName'] = airlineName['airlineName']
		return redirect(url_for('home'))
	else:
		error = "Invalid login or username"
		return render_template('staffLogin.html', error = error)

@app.route('/home', methods = ['GET', 'POST'])
def home():
	today = datetime.now().date()
	dateRange = today + timedelta(days = 30)
	query = "SELECT * FROM Flight WHERE airlineName = %s and departDate BETWEEN %s and %s"
	cursor = conn.cursor()
	cursor.execute(query, (session['airlineName'], today, dateRange))
	data = cursor.fetchall()
	return render_template('home.html', data = data)


@app.route('/staffViewFlightByDate', methods = ['GET', 'POST'])
def staffViewFlightByDate():
	searchByDateBeginning = request.form['searchByDateBeginning']
	searchByDateEnd = request.form['searchByDateEnd']
	airlineName = session['airlineName']
	searchQuery = "SELECT * FROM Flight WHERE airlineName = %s and departDate BETWEEN %s and %s"
	cursor = conn.cursor()
	cursor.execute(searchQuery, (airlineName, searchByDateBeginning, searchByDateEnd))
	data = cursor.fetchall()
	return render_template('home.html', data = data)

@app.route('/staffViewFlightByAirport', methods =['GET', 'POST'])
def staffViewFlightByAirport():
	searchByDepartAirportID = request.form['searchByDepartAirportID']
	searchByArrivalAirportID = request.form['searchByArrivalAirportID']
	airlineName = session['airlineName']
	searchQuery = "SELECT * FROM Flight WHERE airlineName = %s and departAirportID = %s and arrivalAirportID = %s"
	cursor = conn.cursor()
	cursor.execute(searchQuery, (airlineName, searchByDepartAirportID, searchByArrivalAirportID))
	data = cursor.fetchall()
	return render_template('home.html', data = data)

@app.route('/staffViewCustomers', methods=['GET', 'POST'])
def staffViewCustomers():
	airlineName = session['airlineName']
	flightNum = request.form['flightNum']
	airlineCheckQuery = "SELECT * FROM Flight WHERE airlineName = %s and flightNum = %s"
	cursor = conn.cursor()
	cursor.execute(airlineCheckQuery, (airlineName, flightNum))
	data = cursor.fetchone()
	if(data == None):
		error = "There is no flight of this flight number in the airline you are working for"
		return render_template('home.html', error = error)
	query = "SELECT flightNum, email, firstName, lastName FROM Ticket WHERE flightNum = %s"
	cursor.execute(query, (flightNum))
	data = cursor.fetchall()
	return render_template('home.html', customerData = data)

@app.route('/staffChangeFlightStatus', methods=['GET', 'POST'])
def staffChangeFlightStatus():
	airlineName = session['airlineName']
	flightNum = request.form['flightNum']
	flightStatus = request.form['flightStatus']
	airlineCheckQuery = "SELECT * FROM Flight WHERE airlineName = %s and flightNum = %s"
	cursor = conn.cursor()
	cursor.execute(airlineCheckQuery, (airlineName, flightNum))
	data = cursor.fetchone()
	print(flightStatus)
	if(data == None):
		error = "There is no flight of this flight number in the airline you are working for"
		return render_template('home.html', error = error)
	query = "UPDATE Flight SET flightStatus = %s WHERE flightNum = %s"
	cursor.execute(query, (flightStatus, flightNum))
	conn.commit()
	notification = "Change Successfully Made"
	return render_template('home.html', notification = notification)

@app.route('/createFlights', methods = ['GET', 'POST'])
def createFlights():
	AirlineName = session['airlineName']
	flightNum = request.form['flightNum']
	departDate = request.form['departDate']
	departTime = request.form['departTime']
	arrivalDate = request.form['arrivalDate']
	arrivalTime = request.form['arrivalTime']
	departAirportID = request.form['departAirportID']
	arrivalAirportID = request.form['arrivalAirportID']
	basePrice = request.form['basePrice']
	flightStatus = request.form['flightStatus']
	cursor = conn.cursor()
	query = "SELECT * FROM Flight Where flightNum = %s"
	cursor.execute(query, (flightNum))
	data = cursor.fetchone()
	if(data):
		error = "This flight already exists"
		return render_template('staffAddCreatePage.html', error = error)
	else:
		airportCheckQuery = "SELECT airportID FROM Airport WHERE airportID = %s"
		cursor.execute(airportCheckQuery, (departAirportID))
		confirm = cursor.fetchone()
		if(confirm == None):
			error = "This AirportID is Not in Our System"
			return render_template('staffAddCreatePage.html', error = error)
		cursor.execute(airportCheckQuery, (arrivalAirportID))
		confirm = cursor.fetchone()
		if(confirm == None):
			error = "This AirportID is Not in Our System"
			return render_template('staffAddCreatePage.html', error = error)
		ins = "INSERT INTO Flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(ins, (AirlineName, flightNum, departDate, departTime, arrivalDate, arrivalTime, departAirportID, arrivalAirportID, basePrice, flightStatus))
		conn.commit()
		notification = "Flight Successfully Created"
		return render_template('staffAddCreatePage.html', createFlightNotification = notification)
	
@app.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
	planeID = request.form['planeID']
	airlineName = session['airlineName']
	numSeat = request.form['numSeat']
	manufacutre = request.form['manufacutre']
	modelNum = request.form['modelNum']
	age = request.form['age']
	manuDate = request.form['manuDate']
	searchQuery = "SELECT * FROM Airplane WHERE planeID = %s"
	cursor = conn.cursor()
	cursor.execute(searchQuery, (planeID))
	confirm = cursor.fetchone()
	if(confirm):
		error = "This Airplane Already Exists"
		return render_template('staffAddCreatePage.html', airplaneAdditionError = error)
	else:
		query = "INSERT INTO Airplane VALUES (%s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(query, (planeID, airlineName, numSeat, manufacutre, modelNum, age, manuDate))
		conn.commit()
		notification = "Airplane Successfully Added"
		return render_template('staffAddCreatePage.html', airplaneAdditionNotification = notification)
	
@app.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
	airportID = request.form['airportID']
	name = request.form['name']
	city = request.form['city']
	country = request.form['country']
	numTerminal = request.form['numTerminal']
	type = request.form['type']
	searchQuery = "SELECT * FROM Airport WHERE airportID = %s"
	cursor = conn.cursor()
	cursor.execute(searchQuery, (airportID))
	confirm = cursor.fetchone()
	if(confirm):
		error = "This Airport Already Exists"
		return render_template('staffAddCreatePage.html', airportAdditionError = error)
	else:
		query = "INSERT INTO Airport VALUES (%s, %s, %s, %s, %s, %s)"
		cursor.execute(query, (airportID, name, city, country, numTerminal, type))
		conn.commit()
		notification = "Airport Successfully Added"
		return render_template('staffAddCreatePage.html', airportAdditionNotification = notification)
	
@app.route('/staffViewFlightRatings', methods=['GET', 'POST'])
def staffViewFlightRatings():
	flightNum = request.form['flightNum']
	airlineName = session['airlineName']
	airlineCheckQuery = "SELECT * FROM Flight WHERE airlineName = %s and flightNum = %s"
	cursor = conn.cursor()
	cursor.execute(airlineCheckQuery, (airlineName, flightNum))
	data = cursor.fetchone()
	if(data == None):
		error = "There is no flight of this flight number in the airline you are working for"
		return render_template('staffViewPage.html', viewRatingError = error)
	else:
		query = "SELECT * FROM Review WHERE flightNum = %s"
		cursor.execute(query, (flightNum))
		reviewData = cursor.fetchall()
		avgRatingQuery = "SELECT AVG(rating) FROM Review WHERE flightNum = %s GROUP BY flightNum"
		cursor.execute(avgRatingQuery, (flightNum))
		avgRating = cursor.fetchone()
		return render_template('staffViewPage.html', reviewData = reviewData, avgRating = avgRating['AVG(rating)'])
	
@app.route('/viewCotY', methods =['GET', 'POST'])
def viewCotY():
	airlineName = session['airlineName']
	today = datetime.now().date()
	dateRange = today - timedelta(days = 365)	
	query = "SELECT email, firstName, lastName, COUNT(*) AS occurrenceCount FROM Ticket WHERE flightNum in(SELECT flightNum FROM Flight WHERE airlineName = %s and departDate BETWEEN %s and %s) GROUP BY email ORDER BY occurrenceCount DESC LIMIT 1"
	cursor = conn.cursor()
	cursor.execute(query, (airlineName, dateRange, today))
	coty = cursor.fetchone()
	return render_template('staffViewPage.html', CotY = coty)

@app.route('/viewCustomerFlight', methods =['GET', 'POST'])
def viewCustomerFlight():
	airlineName = session['airlineName']
	email = request.form['email']
	query = "SELECT flightNum FROM Ticket WHERE email = %s and flightNum in(SELECT flightNum FROM Flight WHERE airlineName = %s)"
	cursor = conn.cursor()
	cursor.execute(query, (email, airlineName))
	data = cursor.fetchall()
	return render_template('staffViewPage.html', flightData = data, email = email)

@app.route('/viewRevenue', methods=['GET', 'POST'])
def viewRevenue():
	airlineName = session['airlineName']
	type = request.form['type']
	today = datetime.now().date()
	cursor = conn.cursor()
	if(type == "month"):
		dateRange = today - timedelta(days = 30)
		query = "SELECT SUM(ticketPrice) FROM Ticket WHERE flightNum in(SELECT flightNum FROM Flight WHERE airlineName = %s and departDate BETWEEN %s and %s)"
		cursor.execute(query, (airlineName, dateRange, today))
		data = cursor.fetchone()
		return render_template('staffViewPage.html', monthRevenue = data['SUM(ticketPrice)'])
	else:
		dateRange = today - timedelta(days = 365)
		query = "SELECT SUM(ticketPrice) FROM Ticket WHERE flightNum in(SELECT flightNum FROM Flight WHERE airlineName = %s and departDate BETWEEN %s and %s)"
		cursor.execute(query, (airlineName, dateRange, today))
		data = cursor.fetchone()
		return render_template('staffViewPage.html', yearRevenue = data['SUM(ticketPrice)'])
	
@app.route('/scheduleMaintenance', methods =['GET', 'POST'])
def scheduleMaintenance():
	planeID = request.form['planeID']
	airlineName = session['airlineName']
	startDate = request.form['startDate']
	startTime = request.form['startTime']
	endDate = request.form['endDate']
	endTime = request.form['endTime']
	today = datetime.now().date()
	undergoing = 0
	compStartDate = datetime.strptime(startDate, '%Y-%m-%d').date()
	compEndDate = datetime.strptime(endDate, '%Y-%m-%d').date()
	if(compStartDate < today < compEndDate):
		undergoing = True
	else:
		undergoing = False
	cursor = conn.cursor()
	checkQuery = "SELECT planeID FROM Airplane WHERE planeID = %s and airlineName = %s"
	cursor.execute(checkQuery, (planeID, airlineName))
	isPlane = cursor.fetchone()
	if(isPlane == None):
		error = "There is no plane with this plane ID in your Airline"
		return render_template('staffAddCreatePage.html', maintenanceError = error)
	checkQuery = "SELECT startDate FROM Maintenance WHERE startDate = %s"
	cursor.execute(checkQuery, (startDate))
	confirm = cursor.fetchone()
	if(confirm):
		error = "There is already a maintenance recorded on this Start Date"
		return render_template('staffAddCreatePage.html', maintenanceError = error)
	ins = "INSERT INTO Maintenance VALUES (%s, %s, %s, %s, %s, %s)"
	cursor.execute(ins, (planeID, undergoing, startDate, endDate, startTime, endTime))
	conn.commit()
	maintenanceNotification = "Maintenance Registration Successful"
	return render_template('staffAddCreatePage.html', maintenanceNotification = maintenanceNotification)

@app.route('/customerLogout')
def customerLogout():
	session.pop('email')
	return redirect('/')

@app.route('/staffLogout')
def staffLogout():
	session.pop('username')
	return redirect('/')

app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
