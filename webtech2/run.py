from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, url_for , jsonify, flash,Response
from flask_sqlalchemy import SQLAlchemy
from flask import request, session
import datetime
import json
import hashlib 
from sqlalchemy import func, create_engine
import time
from flask_mail import Mail, Message
import math





#Bengaluru = {"park":0.2,"lake":0.15,"historic":0.15,"holy":0.05,"amusement":0.2,"trek":0.1,"market":0.05,"waterfalls":0.1}
#Hyderabad = {"park":0.2,"historic":0.3,"holy":0.25,"lake":0.1,"amusement":0.2}
#Mumbai = {"historic":0.15,"holy":0.1,"beach":0.3,"park":0.1,"lake":0.1,"amusement":0.2,"trek":0.05}
#Goa = {"beach":0.5,"holy":0.1,"historic":0.05,"party":0.2,"market":0.05,"park":0.025,"trek":0.025,"waterfalls":0.05}

#gen = {"park":0.156,"lake":0.09,"historic":0.16,"holy":0.125,"amusement":0.15,"trek":0.043,"market":0.025,"waterfalls":0.037,"beach":0.164,"party":0.05}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brain1.sqlite3'
app.config['SECRET_KEY'] = "randomstring"
'''
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tourismprp@gmail.com'
app.config['MAIL_PASSWORD'] = 'prpt1234'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
'''
db = SQLAlchemy(app)

class User(db.Model):
   uid = db.Column(db.Integer, primary_key = True,autoincrement=True)
   name = db.Column(db.String(30),nullable=False)
   username = db.Column(db.String(20), unique = True, nullable = False)
   password = db.Column(db.String(256), nullable = False) 
   
   email = db.Column(db.String(20))
   health = db.Column(db.Integer)
   space = db.Column(db.Integer)
   tech = db.Column(db.Integer)
   envrn = db.Column(db.Integer)
   credits = db.column(db.Integer)


def __init__(self, uid, name ,username, password, email,health,space,tech,envrn):
   self.uid = uid
   self.username = username
   self.password = password
   self.email = email
   self.name = name
   self.health = health
   self.space = space
   self.tech = tech
   self.envrn = envrn
   self.credits = 30






@app.route('/')
def show_all():
   return render_template('page1.html')
   
@app.route('/signup/', methods=['GET','POST'])
def signup():
    if(request.method=="POST"):
        name = request.form['name']
        username = request.form['username']
        emailid = request.form['email']
        password = request.form['password']
        checklist = request.form.getlist('preference')
        h = 0
        s = 0
        t= 0
        e = 0
        if 'envi' in checklist:
            e = 1
        if 'space' in checklist:
            s = 1
        if 'tech' in checklist:
            t = 1
        if 'health' in checklist:
            h = 1
        
        user=User(1,name = name,username=username, password=password,email=emailid ,health = h,space=s,tech = t,envrn = e)
        db.session.add(user)
        #db.add(user)
        #db.commit()
        #ResultProxy = connection.execute(query)
        db.session.commit()
        app.logger.info(user.uid)
        session['logged_in'] = True
    return render_template('signup.html')






@app.route('/login/', methods=['GET','POST'])
def login():
    if(request.method=="POST"):
        if session.get('logged_in'):
            return render_template('page1.html')
        username=request.form['username']
        pwd=request.form['password']
        p=User.query.filter_by(username=username).first()
        #print("###################",p.uid)
        #session['current_user']=p.uid
        if(p==None):
            flash("Invalid, please register")
            return render_template("signup.html")
        else:
            print(p.password)
            if(pwd==p.password):
                session['logged_in'] = True
            #results=suggest("Bengaluru")
                return render_template("page1.html")
            else:
                flash("Wrong password")
    return render_template('login.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['current_user']=0
    return show_all()
   



@app.route('/pagelog', methods=['GET'])
def pagelog():
    return render_template('login.html')
    
  
    

    
@app.route('/log' ,methods=['POST','GET'])
def log():
   return render_template('log.html') 



@app.route('/about/')
def about_us():
	return render_template('about.html')

@app.route('/contact/')
def contact():
	return render_template('contact.html')

'''
@app.route('/login/', methods=['GET', 'POST'])
def login():
	error = None
	if (request.method == "POST"):
		username = request.form['username']
		password = request.form['password']
		print(username)
		print(password)
		#res = sql_query(''' ''')
		for row in res:
			u = row['Username']
			p = row['Password']
			if u==username:
				if p==password:
					print('logged in')
					return redirect(url_for('main'))
	
'''







'''
@app.route('/signup/',methods=['GET','POST'])
def signup():
	if(request.method=="POST"):
		name = request.form['name']
		username = request.form['username']
		emailid = request.form['email']
		password = request.form['password']
		checklist = request.form.getlist('preference')
		h = 0
		s = 0
		t= 0
		e = 0
		if 'envi' in checklist:
			e = 1
		if 'space' in checklist:
			s = 1
		if 'tech' in checklist:
			t = 1
		if 'health' in checklist:
			h = 1
		sql_insert(name,username,password,emailid,h,s,t,e)
	return render_template('signup.html')
    '''



    
    
if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
   
   
   
   
  