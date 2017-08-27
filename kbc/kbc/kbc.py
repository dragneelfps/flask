import sqlite3,os
from flask import Flask, g, render_template, session, request

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'test.db'),
    SECRET_KEY='development key'
))

def get_db():
    """
    Another way to return database connection
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db
    """
    if not hasattr(g, '_database'):
        g._database = sqlite3.connect(app.config['DATABASE'])
        g._database.row_factory = sqlite3.Row
    return g._database

@app.teardown_appcontext
def close_connection(error):
    """
    Another way to close database connection
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()
    """
    if hasattr(g, '_database'):
        g._database.close()

def init_db():
    """Initilizes db with the provided schema.sql"""
    db = get_db()
    with app.open_resource('schema.sql',mode='r') as f:
        db.cursor().executescript(f.read())

@app.cli.command('initdb')
def initdb():
    """command line for init_db()"""
    init_db()
    print('Db initialized')


@app.route('/')
def showHome():
    """route for welcome screen"""
    return render_template('index.html')


@app.route('/login',methods=['GET','POST'])
def login():
    """if request method is post, user credentials is checked. Else shows login screen"""
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select username,password from tbl_users')
        users = cur.fetchall()
        found = False
        for user in users:
            if user['username'] == request.form['username'] and user['password'] == request.form['password']:
                session['logged_in'] = True
                session['username'] = request.form['username']
                found = True
                print("%s:%s"%(user['username'],user['password']))
                return render_template('index.html')
        if not found:
            error = "User not found"
    return render_template('login.html',error=error)

@app.route('/signup',methods=['GET','POST'])
def signup():
    """if request is post, user is created if it doesnt exist. Else shows signup screen"""
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into tbl_users(username,password) values(?,?)',(request.form['username'],request.form['password']))
        db.commit()
        session['logged_in'] = True
        session['username'] = request.form['username']
        print('%s:%s user created'%(request.form['username'],request.form['password']))
        return render_template('index.html')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """logs out"""
    session['logged_in'] = False
    return render_template('index.html')

@app.cli.command('initquiz')
def initquiz():
    """Initilizes quiz questions"""
    questions = [('What is 3-1?','2','3','0','4',1),
                ('What is 3-2?','2','3','0','1',4),
                ('What is 3-3?','2','3','0','4',3)]
    db = get_db()
    db.executemany('insert into quiz values(?,?,?,?,?,?)',questions)
    db.commit()
    print('initialized quiz data')

def getquiz():
    """returns the quiz questions"""
    db = get_db()
    cur = db.execute('select * from quiz')
    questions = cur.fetchall()
    for question in questions:
        print(question['question'])
    return questions


@app.cli.command('getquiz')
def get_quiz():
    """cli command for getquiz"""
    getquiz()

@app.route('/quiz')
def quiz():
    """shows quiz"""
    questions = getquiz()
    return render_template('quiz.html',questions=questions)

@app.route('/result',methods=['POST'])
def result():
    """shows result"""
    score = 0
    questions = getquiz()
    for i in range(len(questions)):
        print(type(request.form[str(i)]),type(questions[i]['answer']))
        if request.form[str(i)] == str(questions[i]['answer']):
            print('here')
            score = score + 1
    return render_template('result.html',score=score)
