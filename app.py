import re
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db

app = Flask(__name__)
app.secret_key = 'a'
conn = ibm_db.connect(
    "DATABASE=bludb ;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=Certificate.crt;UID=ndn31403;PWD=CXByUkMolyENaZVa;", '', '')

print("connected")
@app.route('/')
@app.route('/login', methods=['POST','GET'])
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
            insert_sql = "INSERT INTO USERS VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = 'you have successfully registered !'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('login.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
