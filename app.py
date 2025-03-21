import os
from flask import Flask, render_template, request, redirect, session, url_for
from sqlite3 import *
from flask_mail import Mail, Message
from random import randrange
import pickle
import pandas as pd
import io
import base64
from matplotlib.figure import Figure

app = Flask(__name__)
app.secret_key = "myheart"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "your e-mail"
app.config["MAIL_PASSWORD"] = "your mail password given by app password" 
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


mail = Mail(app)

@app.route("/")
def home():
	if 'username' in session:
		return render_template("home.html", name = session['username'])
	else:
		return redirect(url_for('signup'))

@app.route("/find")
def find():
	if 'username' in session:
		return render_template("find.html", name = session['username'])
	else:
		return redirect(url_for('home'))



@app.route("/signup", methods = ["GET", "POST"])
def signup():
	if request.method == "POST":
		em = request.form["em"]
		un = request.form["un"]
		pw = ""
		text = "0123456789"
		for i in range(6):
			pw = pw + text[randrange(len(text))]
		print(pw)
		msg = Message("Welcome to HeartDiseasePrediction", sender = "your mail", recipients = [em])
		msg.body = "Greetings from HeartDiseasePredictor! Your password is " + str(pw)
		mail.send(msg)
		con = None
		try:
			con = connect("myheart.db")
			cursor = con.cursor()
			sql = "insert into user values('%s', '%s')"
			con.execute(sql % (un, pw))
			con.commit()
			return render_template("login.html", msg = "Password has been mailed to you")
		except Exception as e:
			con.rollback()
			return render_template("signup.html", msg = "User already exists" + str(e))
	else:
		return render_template("signup.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
	if request.method == "POST":
		un = request.form["un"]
		pw = request.form["pw"]
		con = None
		try:
			con = connect("myheart.db")
			cursor = con.cursor()
			sql = "select * from user where username = '%s' and password = '%s'"
			cursor.execute(sql % (un,pw))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html", msg = "invalid login")
			else:	
				session['username'] = un
				return redirect( url_for('home'))
		
		except Exception as e:
			msg = "Issue " + str(e)
			return render_template("login.html", msg = msg)
	else:
		return render_template("login.html")

@app.route("/forgot", methods = ["GET", "POST"])
def forgot():
	if request.method == "POST":
		un = request.form["un"]
		em = request.form["em"]
		con = None
		try:
			con = connect('myheart.db')		
			cursor = con.cursor()
			sql = "select * from user where username = '%s'"
			cursor.execute(sql % (un))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("forgot.html", msg = "invalid login")
			else:	
				session['username'] = un
				pw1 = ""
				text = "0123456789"
				for i in range(6):
					pw1 = pw1 + text[randrange(len(text))]
				print(pw1)
				msg = Message("Hello again from HeartDiseasePrediction", sender = "your mail", recipients = [em])
				msg.body = "Greetings from HeartDiseasePredictor! Seems like you forgot your password. Your new password is " + str(pw1)
				mail.send(msg)
				try:
					con = connect("myheart.db")
					cursor = con.cursor()
					sql = "update user set password = '%s' where username = '%s'"
					con.execute(sql % (pw1, un))
					con.commit()
					return render_template("login.html", msg = "Password has been mailed to you")
				except Exception as e:
					con.rollback()
					return render_template("forgot.html", msg = "Some Issue: " + str(e))
		except Exception as e:
			msg = "Issue " + str(e)
			return render_template("forgot.html", msg = msg)	
	else:
		return render_template("forgot.html")	

@app.route("/check", methods=["POST"])
def check():
    if request.method == "POST":
        if 'username' in session:
            name = session['username']

      
        age = float(request.form.get("age", 0))
        cp = int(request.form.get("r1", 1))  
        BP = float(request.form.get("BP", 0))
        CH = float(request.form.get("CH", 0))  
        maxhr = float(request.form.get("maxhr", 0))
        STD = float(request.form.get("STD", 0))  
        fluro = float(request.form.get("fluro", 0))  
        Th = float(request.form.get("Th", 0))  

        
        feature_names = ['Age', 'Chest pain type', 'BP', 'Cholesterol', 'Max HR', 'ST depression', 'Number of vessels fluro', 'Thallium']
        features_df = pd.DataFrame([[age, cp, BP, CH, maxhr, STD, fluro, Th]], columns=feature_names)

        
        with open("heartdiseaseprediction.model", "rb") as f:
            model = pickle.load(f)

       
        res = model.predict(features_df)

        
        return render_template(
            "find.html",
            msg=res[0], 
            name=session.get('username', 'Guest'),
            age=age,
            chest_pain=cp,
            BP=BP,
            CH=CH,
            maxhr=maxhr,
            STD=STD,
            fluro=fluro,
            Th=Th
        )
    else:
        return render_template("home.html")


@app.route('/show_graph', methods=['POST'])

def show_graph():
    
    chest_pain = float(request.form['r1'])
    bp = float(request.form['BP'])
    chol = float(request.form['CH'])
    maxhr = float(request.form['maxhr'])
    std = float(request.form['STD'])
    fluro = float(request.form['fluro'])
    thallium = float(request.form['Th'])

   
    healthy_data = {
        'Chest Pain': 1,  
        'BP': 120,  
        'Cholesterol': 200,  
        'Max HR': 150,  
        'ST Depression': 1.0,  
        'Vessels Fluro': 1,  
        'Thallium': 3  
    }

   
    patient_data = {
        'Chest Pain': chest_pain,
        'BP': bp,
        'Cholesterol': chol,
        'Max HR': maxhr,
        'ST Depression': std,
        'Vessels Fluro': fluro,
        'Thallium': thallium
    }

    
    fig = Figure(figsize=(12, 5))  
    fig.patch.set_facecolor('#feb898')
    ax = fig.subplots()
    ax.set_facecolor('#bff4ed')

    
    labels = list(patient_data.keys())

   
    patient_values = list(patient_data.values())
    healthy_values = list(healthy_data.values())

 
    x = range(len(labels))
    width = 0.35  
   
    ax.bar([pos - width/2 for pos in x], patient_values, width, label='Your Data')
    ax.bar([pos + width/2 for pos in x], healthy_values, width, label='Healthy Person Data')

    
    ax.set_ylabel('Values')
    ax.set_title("")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    
    for i in range(len(labels)):
        ax.text(i - width/2, patient_values[i] + 0.5, f'{patient_values[i]:.2f}', ha='center', va='bottom', fontsize=10)
        ax.text(i + width/2, healthy_values[i] + 0.5, f'{healthy_values[i]:.2f}', ha='center', va='bottom', fontsize=10)

    
    buf = io.BytesIO() 
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf8')  
    
 
    return render_template('graph.html', graph=image_base64)

@app.route("/logout", methods = ["POST"])
def logout():
	session.clear()	
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.run(debug = True)