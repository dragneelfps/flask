from flask import Flask, render_template, request, json
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
app = Flask(__name__)

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'drag'
app.config['MYSQL_DATABASE_PASSWORD'] = 'drag'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



@app.route("/")
def main():
    return render_template("index.htm")

@app.route("/showSignUp")
def showSignUp():
    return render_template("signup.htm")

@app.route("/signUp",methods=['POST'])
def signUp():

    _name = request.form['inputName']
    _email = request.form['inputName']
    _password = request.form['inputPassword']


    conn = mysql.connect()
    cursor = conn.cursor()

    _hashed_password = generate_password_hash(_password)
    cursor.callproc('sp_createUser',(_name,_email,_hashed_password))

    data = cursor.fetchall()
    if len(data) is 0:
        conn.commit()
        return json.dumps({'message':'User created succesfully !'})
    else:
        return json.dumps({'error': str(data[0])})

    if _name and _email and _password:
        return json.dumps({'html':'<span>All fields good!!</span>'})
    else:
        return json.dumps({'html':'<span>Enter the req. fields</span>'})

if __name__ == "__main__":
    app.run()
