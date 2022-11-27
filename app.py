import os
from helpers import apology,login_required
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///patients.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/doctor',methods=["GET","POST"])
def doctor():
    session.clear()
    if request.method=="GET":
        return render_template("doctor.html")
    else:
        if not request.form.get("email"):
            return apology("Must provide Email ID", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM doctors WHERE email = ?", request.form.get("email"))

        # Ensure doctor exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        flash("Logged In!")

        return redirect("/ddashboard")

@app.route('/patient')
def patient():
    return render_template("patient.html")

@app.route('/admin',methods=["GET","POST"])
def admin():
    session.clear()
    if request.method=="GET":
        return render_template("admin.html")
    else:
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM admin WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Logged In!")

        return redirect("/adashboard")

@app.route('/pregister',methods=["GET","POST"])
def pregister():
    if request.method=="GET":
        return render_template("pregister.html")
    else:
        fname = request.form.get("firstName")
        lname = request.form.get("lastName")
        email = request.form.get("email")
        contact = request.form.get("contact")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        gender = request.form.get("gender")
        if not fname or not lname:
            return apology("Please enter your first and last name")
        if not email or not contact:
            return apology("Please enter your email id and your contact info")
        if not password or not confirmation:
            return apology("Please enter a password and confirm it")
        if not gender:
            gender = "N/A"
        if password != confirmation:
            return apology("Your passwords do not match")
        hashed = generate_password_hash(confirmation)
        try:
            newUser = db.execute("INSERT INTO users(fname,lname,mail,contact,password,hash,gender) VALUES(?,?,?,?,?,?,?)",fname,lname,email,contact,confirmation,hashed,gender)
        except:
            return apology("This user already exists")
        session["user_id"] = newUser
        flash("Registered!")
        return redirect("/pdashboard")

@app.route("/plogin",methods=["GET","POST"])
def plogin():
    session.clear()
    if request.method=="GET":
        return render_template("plogin.html")
    else:
        if not request.form.get("email"):
            return apology("Must provide Email ID", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE mail = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Logged In!")

        return redirect("/pdashboard")

@app.route("/pdashboard")
@login_required
def pdashboard():
    userID = session["user_id"]
    name = db.execute("SELECT fname,lname FROM users WHERE id=?",userID)
    user = name[0]["fname"]+" "+name[0]["lname"]
    return render_template("pdashboard.html",user=user)

@app.route("/pbook",methods=["GET","POST"])
@login_required
def pbook():
    user_id = session["user_id"]
    names = db.execute("SELECT fname,lname FROM doctors")
    fullNames = []
    for i in names:
        full = i["fname"] + " " + i["lname"]
        fullNames.append(full)
    if request.method=="GET":
        return render_template("pbook.html",fullNames=fullNames)
    else:
        doctor = request.form.get("doctor")
        date = request.form.get("date")
        time = request.form.get("time")
        if not doctor:
            return apology("Please choose a doctor!")
        if not date:
            return apology("Please choose a date!")
        if not time:
            return apology("Please choose a time!")
        try:
            db.execute("INSERT INTO appointment(user_id,doctor,date,time) VALUES(?,?,?,?)",user_id,doctor,date,time)
        except:
            return apology("Oops! An error occurred!")
        flash("Booked!")
        return redirect("/pdashboard")

@app.route("/pview")
@login_required
def pview():
    userID = session["user_id"]
    row = db.execute("SELECT doctor,date,time FROM appointment WHERE user_id=?",userID)
    return render_template("pview.html",row=row)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged Out!")
    return redirect("/")

@app.route("/ddashboard")
@login_required
def ddashboard():
    userID = session["user_id"]
    name = db.execute("SELECT fname,lname FROM doctors WHERE id=?",userID)
    user = name[0]["fname"]+" "+name[0]["lname"]
    return render_template("ddashboard.html",user=user)

@app.route("/dview")
@login_required
def dview():
    doctorID = session["user_id"]
    names = db.execute("SELECT fname,lname FROM doctors WHERE id=?",doctorID)
    doctorName = names[0]["fname"] + " " + names[0]["lname"]
    appointments = db.execute("SELECT user_id,date,time FROM appointment WHERE doctor=?",doctorName)
    data = []
    if len(appointments)>0:
        for i in appointments:
            pdata = {}
            pid = i["user_id"]
            patient = db.execute("SELECT fname,lname,contact,mail FROM users WHERE id=?",pid)
            if len(patient)>0:
                pdata["fname"] = patient[0]["fname"]
                pdata["lname"] = patient[0]["lname"]
                pdata["contact"] = patient[0]["contact"]
                pdata["mail"] = patient[0]["mail"]
                pdata["date"] = i["date"]
                pdata["time"] = i["time"]
                data.append(pdata)
    return render_template("dview.html",data=data)

@app.route("/adashboard")
@login_required
def adashboard():
    return render_template("adashboard.html")

@app.route("/dlist")
@login_required
def dlist():
    data = db.execute("SELECT fname,lname,password,email FROM doctors")
    if len(data)==0:
        data = []
    return render_template("dlist.html",data=data)

@app.route("/plist")
@login_required
def plist():
    data = db.execute("SELECT fname,lname,mail,contact,password FROM users")
    if len(data)==0:
        data = []
    return render_template("plist.html",data=data)

@app.route("/vapp")
@login_required
def vapp():
    appointments = db.execute("SELECT user_id,doctor,date,time FROM appointment")
    data = []
    for i in appointments:
        user_id = i["user_id"]
        patients = db.execute("SELECT fname,lname,mail,contact FROM users WHERE id=?",user_id)
        if len(patients)>0:
            info = {}
            info["fname"] = patients[0]["fname"]
            info["lname"] = patients[0]["lname"]
            info["mail"] = patients[0]["mail"]
            info["contact"] = patients[0]["contact"]
            info["doctor"] = i["doctor"]
            info["date"] = i["date"]
            info["time"] = i["time"]
            data.append(info)
    return render_template("vapp.html",data=data)

@app.route("/add",methods=["GET","POST"])
@login_required
def dadd():
    if request.method=="GET":
        return render_template("add.html")
    else:
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not fname or not lname:
            return apology("Please enter your first and last name")
        if not email:
            return apology("Please enter your email id")
        if not password or not confirmation:
            return apology("Please enter a password and confirm it")
        if password != confirmation:
            return apology("Your passwords do not match")
        hashed = generate_password_hash(confirmation)
        try:
            newUser = db.execute("INSERT INTO doctors(fname,lname,email,password,hash) VALUES(?,?,?,?,?)",fname,lname,email,confirmation,hashed)
        except:
            return apology("This email already exists")
        flash("Registered!")
        return redirect("/adashboard")

