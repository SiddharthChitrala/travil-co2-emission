import re
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import requests
import os
import ibm_boto3  # pip install ibm-cos-sdk in terminal
from ibm_botocore.client import Config, ClientError

app = Flask(__name__)
app.secret_key = 'a'
conn = ibm_db.connect(
    "DATABASE=bludb ;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=Certificate.crt;UID=ndn31403;PWD=CXByUkMolyENaZVa;", '', '')

print("connected")

# Constants for IBM COS values
COS_ENDPOINT = "https://s3.eu-de.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "AFiLtRUmpqrrduuqNnsVY0cZGJRs2XeUqv5MgHnUAl4s"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/f768e793d0064938ab9b701fb75900da:5a9826eb-a1b8-471c-a76c-7c5709ec90d3::"
# Create resource
cos = ibm_boto3.client("s3",
                       ibm_api_key_id=COS_API_KEY_ID,
                       ibm_service_instance_id=COS_INSTANCE_CRN,
                       config=Config(signature_version="oauth"),
                       endpoint_url=COS_ENDPOINT
                       )


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    global userid
    msg = ''

    if request.method == 'POST':
        # print("Haiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM USERS WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            
            session['loggedin'] = True
            session['USERID']=account['USERID']
            session['id'] = account['USERNAME']
            userid = account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'logged in successfully !'
            return render_template('index.html', msg=msg)
        else:

            msg = 'Incorrect username/password'
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # print('hi----------------------')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # print(username)
        sql = "SELECT * FROM USERS WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email address !"
        else:
            sql = "SELECT count(*) FROM USERS"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql = "INSERT INTO USERS VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt,1,length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
            msg = 'you have successfully registered !'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template('login.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route("/co2calculator")
def co2():

    return render_template('co2calculator.html')


@app.route("/co2calculator1", methods=['POST', 'GET'])
def output1():

    if request.method == 'POST':
        VehicleType = request.form['VehicleType']
        VehicleFuelType = request.form['VehicleFuelType']
        Distance = request.form['Distance']
        NumberOfPeople = request.form['NumberOfPeople']
        # print(cars,fuels,dists,nump)

        url = "https://travel-co2-climate-carbon-emissions.p.rapidapi.com/api/v1/transport"

        payload = {
            "vehicle": {
                "type": VehicleType,
                "fuel": {"type": VehicleFuelType}
            },
            "distance": Distance,
            "people": NumberOfPeople
        }
        headers = {
            "content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {YOUR_API_KEY}",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": "27b6565a30mshe87cd65f16384b3p180f40jsn268e26e0d7ef",
            "X-RapidAPI-Host": "travel-co2-climate-carbon-emissions.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)
        output1 = response.json()

        pp = output1['co2e_pp']
        print(pp)
        e = output1['co2e']

        if request.method == 'POST':
            VehicleType = request.form['VehicleType']
            VehicleFuelType = request.form['VehicleFuelType']
            Distance = request.form['Distance']
            NumberOfPeople = request.form['NumberOfPeople']
            co2e_pp = pp
            print(pp)
            co2e = e
            insert_sql = "INSERT INTO VEHICLES VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, VehicleType)
            ibm_db.bind_param(prep_stmt, 2, VehicleFuelType)
            ibm_db.bind_param(prep_stmt, 3, Distance)
            ibm_db.bind_param(prep_stmt, 4, NumberOfPeople)
            ibm_db.bind_param(prep_stmt, 5, co2e_pp)
            ibm_db.bind_param(prep_stmt, 6, co2e)
            ibm_db.execute(prep_stmt)
        return render_template("co2calculator.html", pp=pp, e=e)
    return render_template("co2calculator.html")


@app.route("/co2calculator2", methods=['POST', 'GET'])
def output2():

    if request.method == 'POST':
        VehicleType = request.form['VehicleType']
        VehicleFuelType = request.form['VehicleFuelType']
        Distance = request.form['Distance']
        NumberOfPeople = request.form['NumberOfPeople']
        # print(cars,fuels,dists,nump)

        url = "https://travel-co2-climate-carbon-emissions.p.rapidapi.com/api/v1/transport"

        payload = {
            "vehicle": {
                "type": VehicleType,
                "fuel": {"type": VehicleFuelType}
            },
            "distance": Distance,
            "people": NumberOfPeople
        }
        headers = {
            "content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {YOUR_API_KEY}",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": "27b6565a30mshe87cd65f16384b3p180f40jsn268e26e0d7ef",
            "X-RapidAPI-Host": "travel-co2-climate-carbon-emissions.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)
        output2 = response.json()

        pp = output2['co2e_pp']
        print(pp)
        e = output2['co2e']
        if request.method == 'POST':
            VehicleType = request.form['VehicleType']
            VehicleFuelType = request.form['VehicleFuelType']
            Distance = request.form['Distance']
            NumberOfPeople = request.form['NumberOfPeople']
            co2e_pp = pp
            print(pp)
            co2e = e
            insert_sql = "INSERT INTO VEHICLES VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, VehicleType)
            ibm_db.bind_param(prep_stmt, 2, VehicleFuelType)
            ibm_db.bind_param(prep_stmt, 3, Distance)
            ibm_db.bind_param(prep_stmt, 4, NumberOfPeople)
            ibm_db.bind_param(prep_stmt, 5, co2e_pp)
            ibm_db.bind_param(prep_stmt, 6, co2e)
            ibm_db.execute(prep_stmt)
        return render_template("co2calculator.html", pp=pp, e=e)
    return render_template("co2calculator.html")


@app.route("/co2calculator3", methods=['POST', 'GET'])
def output3():

    if request.method == 'POST':
        VehicleType = request.form['VehicleType']
        VehicleFuelType = request.form['VehicleFuelType']
        Distance = request.form['Distance']
        NumberOfPeople = request.form['NumberOfPeople']
        # print(cars,fuels,dists,nump)

        url = "https://travel-co2-climate-carbon-emissions.p.rapidapi.com/api/v1/transport"

        payload = {
            "vehicle": {
                "type": VehicleType,
                "fuel": {"type": VehicleFuelType}
            },
            "distance": Distance,
            "people": NumberOfPeople
        }
        headers = {
            "content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {YOUR_API_KEY}",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": "27b6565a30mshe87cd65f16384b3p180f40jsn268e26e0d7ef",
            "X-RapidAPI-Host": "travel-co2-climate-carbon-emissions.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)
        output3 = response.json()

        pp = output3['co2e_pp']
        print(pp)
        e = output3['co2e']
        if request.method == 'POST':
            VehicleType = request.form['VehicleType']
            VehicleFuelType = request.form['VehicleFuelType']
            Distance = request.form['Distance']
            NumberOfPeople = request.form['NumberOfPeople']
            co2e_pp = pp
            print(pp)
            co2e = e
            insert_sql = "INSERT INTO VEHICLES VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, VehicleType)
            ibm_db.bind_param(prep_stmt, 2, VehicleFuelType)
            ibm_db.bind_param(prep_stmt, 3, Distance)
            ibm_db.bind_param(prep_stmt, 4, NumberOfPeople)
            ibm_db.bind_param(prep_stmt, 5, co2e_pp)
            ibm_db.bind_param(prep_stmt, 6, co2e)
            ibm_db.execute(prep_stmt)
        return render_template("co2calculator.html", pp=pp, e=e)
    return render_template("co2calculator.html")


@app.route("/co2calculator4", methods=['POST', 'GET'])
def output4():

    if request.method == 'POST':
        VehicleType = request.form['VehicleType']
        VehicleFuelType = request.form['VehicleFuelType']
        Distance = request.form['Distance']
        NumberOfPeople = request.form['NumberOfPeople']
        # print(cars,fuels,dists,nump)

        url = "https://travel-co2-climate-carbon-emissions.p.rapidapi.com/api/v1/transport"

        payload = {
            "vehicle": {
                "type": VehicleType,
                "fuel": {"type": VehicleFuelType}
            },
            "distance": Distance,
            "people": NumberOfPeople
        }
        headers = {
            "content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer {YOUR_API_KEY}",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": "27b6565a30mshe87cd65f16384b3p180f40jsn268e26e0d7ef",
            "X-RapidAPI-Host": "travel-co2-climate-carbon-emissions.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)
        output4 = response.json()

        pp = output4['co2e_pp']
        print(pp)
        e = output4['co2e']
        if request.method == 'POST':
            VehicleType = request.form['VehicleType']
            VehicleFuelType = request.form['VehicleFuelType']
            Distance = request.form['Distance']
            NumberOfPeople = request.form['NumberOfPeople']
            co2e_pp = pp
            print(pp)
            co2e = e
            insert_sql = "INSERT INTO VEHICLES VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, VehicleType)
            ibm_db.bind_param(prep_stmt, 2, VehicleFuelType)
            ibm_db.bind_param(prep_stmt, 3, Distance)
            ibm_db.bind_param(prep_stmt, 4, NumberOfPeople)
            ibm_db.bind_param(prep_stmt, 5, co2e_pp)
            ibm_db.bind_param(prep_stmt, 6, co2e)
            ibm_db.execute(prep_stmt)
        return render_template("co2calculator.html", pp=pp, e=e)
    return render_template("co2calculator.html")


#  ride sharing details
@app.route("/ride_sharing", methods=['POST', 'GET'])
def ride_sharing():

    return render_template("ride_sharing.html")

# publish ride


@app.route("/publish")
def publish():

    return render_template("publish.html")


@app.route("/publishDetails", methods=['POST'])
def publishing():
    global ProfilePic

    sql = "SELECT * FROM USERS WHERE USERID="+ str(session['USERID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    # account['USERID']=account['USERID']

    if request.method == 'POST':
        ProfilePic = request.files['ProfilePic']
        FullName = request.form['FullName']
        PhoneNumber = request.form['PhoneNumber']
        Email = request.form['Email']
        Password = request.form['Password']
        Location = request.form['Location']
        Destination = request.form['Destination']
        DateTime = request.form['DateTime']
        NumberOfPeople = request.form['NumberOfPeople']
        insert_sql = "INSERT INTO RIDEPUBLISH VALUES (?,?,?,?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, FullName)
        ibm_db.bind_param(prep_stmt, 2, PhoneNumber)
        ibm_db.bind_param(prep_stmt, 3, Email)
        ibm_db.bind_param(prep_stmt, 4, Password)
        ibm_db.bind_param(prep_stmt, 5, Location)
        ibm_db.bind_param(prep_stmt, 6, Destination)
        ibm_db.bind_param(prep_stmt, 7, DateTime)
        ibm_db.bind_param(prep_stmt, 8, NumberOfPeople)
        ibm_db.bind_param(prep_stmt,9,account["USERID"])
        ibm_db.execute(prep_stmt)

        # os.mkdir('userupload')
        # getting the current path i.e where app.py is present
        basepath = os.path.dirname(__file__)
        # print("current path",basepath)
        # from anywhere in the system we can give image but we want that image later  to process so we are saving it to uploads folder for reusing
        filepath = os.path.join(basepath, 'profilepic', '.jpg')
        # print("upload folder is",filepath)
        ProfilePic.save(filepath)
        cos.upload_file(Filename=filepath,
                        Bucket='profilepictures27', Key=FullName + '.jpg')
        # image.save(os.path.join("static/images", filename))
        # print('data sent tô Object storage')
        # ProfilePic=ProfilePic
        # NumberOfPeople=NumberOfPeople
        # FullName=FullName
        # PhoneNumber=PhoneNumber
        # Location=Location
        # Destination=Destination
        # Email= Email
        print(ProfilePic)
        sql = "SELECT * FROM RIDEPUBLISH WHERE USERID=" + str(session['USERID'])
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        row = []
        while True:
            data = ibm_db.fetch_assoc(stmt)
            if not data:
                break
            else:
                data['USERID'] = str(data['USERID'])
                row.append(data)
            print('rows: ', row)
    return render_template("ride_sharing.html", rows = row, NumberOfPeople=NumberOfPeople,  FullName=FullName,  PhoneNumber=PhoneNumber, Location=Location, Destination=Destination, Email=Email)


if __name__ == '__main__':
    app.run(debug=True)
