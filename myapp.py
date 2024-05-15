from flask import Flask, redirect, render_template, request, url_for
import mysql.connector
import string
import datetime
from flask import session
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="trainticketdb"
)
mycursor = db.cursor()



app = Flask(__name__, template_folder="C:/Users/User/biydaalt2")
app.secret_key = 'bolor'


# @app.route('/')
# def choice():
    
    
    
    
# @app.route('/admin')
# def admin():
    
    

@app.route('/')#/client
def index():
    mycursor.execute("SELECT departureStation FROM train")
    departures = mycursor.fetchall()
    departure_list = [row[0] for row in departures]
    mycursor.execute("SELECT arrivalStation FROM train")
    arrivals = mycursor.fetchall()
    arrival_list = [row[0] for row in arrivals]
    
    return render_template('index.html', departures=departure_list, arrivals=arrival_list)



@app.route('/direct', methods=['POST'])
def direct(): 
    departure = request.form['departure']
    arrival = request.form['arrival']  
    
    # Save departure and arrival in the session
    session['departure'] = departure
    session['arrival'] = arrival 
    
    mycursor.execute("SELECT departureDate, arrivalDate FROM train WHERE departureStation = %s AND arrivalStation = %s", (departure, arrival))
    dates = mycursor.fetchall()
    
    
    mycursor.execute("SELECT capacity FROM train WHERE departureStation = %s AND arrivalStation = %s", (departure, arrival))
    capacity = mycursor.fetchone()
    if capacity:
        capacity_value = int(capacity[0])
        cap_list = list(range(1,capacity_value+1))
    else:
        cap_list = []  

    mycursor.execute("SELECT seatNumber FROM ticket WHERE trainID IN (SELECT trainID FROM train WHERE departureStation = %s AND arrivalStation = %s)", (departure, arrival))

    seatNumbers = mycursor.fetchall()
    seat_list = [int(row[0]) for row in seatNumbers]
    for c in cap_list:
        for f  in seat_list:
            if c == f:
                cap_list.remove(c)
    
    date_list = ['{} {}'.format(row[0].strftime('%Y-%m-%d'), row[1].strftime('%Y-%m-%d')) for row in dates]  
    return render_template("direct.html", dates=date_list, seats = cap_list)

   
@app.route('/previous_page1')
def previous_page1():
    return redirect(url_for('index'))

@app.route('/verify',methods = ['POST','GET'])
def verify():
    date = request.form['date']
    bname = request.form['bname']
    regNumber = request.form['regNumber']
    age = request.form['age']
    phoneNumber = request.form['phoneNumber']
    seatNum = int(request.form['seatNum'])
    seatType = request.form['seatType']
    session['bname'] = bname
    session['regNumber'] = regNumber
    session['phoneNumber'] = phoneNumber
    session['seatNum'] = seatNum
    session['seatType'] = seatType 
    session['age'] = age
    session['date'] = date
    price = 0
    if seatType == "regular" and age == "Том хүн":
        price = 60000
    elif seatType == "luxury" and age == "Том хүн":
        price = 90000
    elif seatType == "regular" and age == "Хүүхэд":
        price = 20000
    elif seatType == "luxury" and age == "Хүүхэд":
        price = 35000
    session['price'] = price
    return render_template("verify.html",bname = bname,regNumber = regNumber,age = age,price = price,date = date)
@app.route('/end', methods=['GET', 'POST'])
def end():
    try:
        date = session.get('date')
        bname = session.get('bname')
        regNumber = session.get('regNumber')
        phoneNumber = session.get('phoneNumber')
        seatNum = session.get('seatNum')
        seatType = session.get('seatType')
        age = session.get('age')
        departure = session.get('departure')
        arrival = session.get('arrival')
        dates = [d[0] for d in date]
        print("Departure:", departure)
        print("Arrival:", arrival)
        print("Date:", date)

        if None in (date, bname, regNumber, phoneNumber, seatNum, seatType, age, departure, arrival):
            raise ValueError("One or more session variables are missing")

        sql = "INSERT INTO buyer (bname,regNumber, pNumber, age) VALUES (%s, %s, %s, %s)"
        values = (bname, regNumber, phoneNumber, age,)
        mycursor.execute(sql, values)
        db.commit()
        
        
        mycursor.execute("SELECT buyerID FROM buyer WHERE bname = %s AND regNumber = %s", (bname, regNumber))
        buyer = mycursor.fetchone()
        if not buyer:
            raise ValueError("Buyer not found")
        buyerID = buyer[0]

        sql_train = "SELECT trainID FROM train WHERE departureStation = %s AND arrivalStation = %s "
        mycursor.execute(sql_train, (departure, arrival))
        train = mycursor.fetchone()

        print("SQL Result (Train):", train)

        if not train:
            raise ValueError("Train not found")
        trainID = train[0]

        sql_ticket = "INSERT INTO ticket (buyerID, trainID, seatNumber, seatType, startDate) VALUES (%s, %s, %s, %s, %s)"
        values = (buyerID, trainID, seatNum, seatType, date[0])
        mycursor.execute(sql_ticket, values)
        db.commit()

        return "Verification completed successfully"
    
    except Exception as e:
        return f"Error: {str(e)}"



@app.route('/previous_page2')
def previous_page2():
    return redirect(url_for('direct'))


if __name__ == '__main__':
    app.run(debug=True)
