from flask import Flask, redirect, render_template, request, flash, session
# import the function connectToMySQL from the file mysqlconnection.pycopy
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
app.secret_key = 'denvernuggets'

# invoke the connectToMySQL function and pass it the name of the database we're using
# connectToMySQL returns an instance of MySQLConnection, which we will store in the variable 'mysql'
mysql = connectToMySQL('useraccounts')
# now, we may invoke the query_db method

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def addFriend():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']  

    if len(first_name) < 1  or len(last_name) < 1 or len(email) < 1 or len(password) < 1:
        flash("Must Fill out everything")
        return redirect('/')

    if len(first_name) < 2:
        print("First Name Should be atleast 2 characters")
        return redirect('/')

    if len(last_name) < 2:
        flash("Last Name Should be atleast 2 characters")
        return redirect('/')

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect('/')

    #checking if the email address is already taken
    query_select = "SELECT email FROM users WHERE email = %(email)s;"
    data1 = {
             'email': request.form['email']
           }

    email_dup = mysql.query_db(query_select, data1)
    if email_dup:
        flash("Email is Already Taken!")
        return redirect('/')

    if password != confirm_password:
        flash("password didnt match")
        return redirect('/')

    add_query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': request.form['password']
        }

    #adds user in the table 
    mysql.query_db(add_query, data)

    flash("Registered Successfully")



    return redirect('/success')

@app.route('/success')
def success():
    if session['userId']:
        all_users = mysql.query_db("SELECT * FROM users")
        print("Fetched all users", all_users)
        return render_template("success.html", all_users = all_users)
    else:
        flash("You're currently not logged in!")
        return redirect('/')
    

@app.route('/delete', methods=['POST'])
def deleteEmail():
    id = int(request.form['deleteId'])
    query1 = "DELETE FROM users WHERE id = '{}'".format(id)
    mysql.query_db(query1)
    return redirect('/success')


@app.route('/logout', methods=['POST'])
def clear():
    session['firstName'] = ''
    session['userId'] =''

    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    query2 = "SELECT id, first_name, email FROM users WHERE email = %(email)s AND password = %(password)s;"
    email = request.form['email']
    password = request.form['password']
    data = {
        'email': request.form['email'],
        'password': request.form['password']
        }
    savedid = mysql.query_db(query2, data)
    if savedid:
        session['userId'] = savedid[0]['id']
        session['firstName'] = savedid[0]['first_name']
        print("-------------------------")
        print(session['userId'])
        print(session['firstName'])
        return redirect('success')

    else: 
        flash("pass and email didnt match")
        return redirect('/')
        

if __name__ == "__main__":
    app.run(debug=True)