from dictionary import words
from random import choice
from flask import Flask,render_template,request,url_for,redirect,session,make_response
import time
from flask_mysqldb import MySQL
from flask_mail import Mail,Message


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'bhargav'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'typing-master'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['DEBUG'] = True


app.config.update(
    MAIL_SERVER = '',
    MAIL_PORT = '',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = '',
    MAIL_PASSWORD=  '',
    MAIL_DEFAULT_SENDER= ''
)


mail = Mail(app)


app.secret_key = 'qwertyuiopasdfghjkklzxcvbnm,1234567890-!@#$%^&*()_)+'

mysql = MySQL(app)
initial = time.time()

right = 0
wrong = 0
word_generated = choice(words)

@app.route('/',methods = ['POST',"GET"])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        account = cursor.fetchall()
        if account:
            global initial
            initial = time.time()
            account = list(account)
            session['email'] = account[0]['email']
            session['name'] = account[0]['name']
            return redirect(url_for('index'))
        else:
            return render_template('signlog.html', found='Incorrect Username or Password')        
    return render_template('signlog.html', found='')

@app.route('/signout',methods=['GET','POST'])
def signout():
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST' and 'email' in request.form and 'password' in request.form and 'name' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        check = cursor.execute('SELECT `name`, `email`, `password` FROM `users` WHERE email=%s', [email])
        if check:
            return render_template('signlog.html', found2='User Already exits')
        else:
            cursor.execute('INSERT INTO `users`(`name`, `email`, `password`) VALUES (%s,%s,%s)', (name,email,password))
            mysql.connection.commit()
            session['email'] = email
            session['name'] = name
            global initial
            initial=time.time()
            return redirect(url_for('index'))
    return render_template('signlog.html', found2='')

@app.route('/words', methods = ['POST','GET'])
def index():
    if 'email' in session:
        if request.method=='POST':
            global word_generated,right,wrong
            word_user = request.form['word']
            if (word_generated==word_user):
                right = right + 1
                word_generated = choice(words)
                return render_template('index.html', word=word_generated,name=session['name'])
            else:
                wrong = wrong + 1
                return render_template('index.html', word=word_generated,ame=session['name'])
        right = 0
        return render_template('index.html',word=word_generated,name=session['name'])
    return '<h1>Please Login First</h1>'

@app.route('/reasult')
def reasult():
    if 'email' in session:
        final = time.time()
        interval = int(final - initial)
        return render_template('reasult.html', right=right, interval=interval,wrong=wrong,total=(right+wrong),name=session['name'])
    return '<h1>Please Login First</h1>'

@app.route('/profile')
def profile():
    return ab

  
@app.route('/forget_password',methods=['GET','POST'])   
def forget_password():
    if 'email' in session:
        return 'You are alread logged in sign out first'
    else:
        if request.method == 'POST':
            check_mail = request.form['check_email']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT `name`, `email`, `password` FROM `users` WHERE email=%s',[check_mail])
            detail = cursor.fetchall()
            if detail:
                final_detail = detail[0]
                name = final_detail['name']
                email = final_detail['email']
                password = final_detail['password']
                msg = Message(subject='Reset Password',body='Hello ' + str(detail[0]['name']) + ' your password is ' + str(detail[0]['password']) + ' . Thanks For using our services.',recipients=[str(email)])
                #msg.subject = 'Resr'
                mail.send(msg)
                return 'Sent!!'
    return render_template('forget_password.html')

if __name__ == "__main__":
    app.run(debug=True)
