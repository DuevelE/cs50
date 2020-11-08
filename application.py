import os
import datetime
import random
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from selenium import webdriver

var=[]  

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///Answer.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    num_q = 5
    if request.method == "POST":
        right = 0.0
        answerd = 0.0
        # replace with SELECT column FROM table ORDER BY RAND() LIMIT 5
        questions = db.execute("SELECT * FROM Questions")
        boolean = 2
        string = request.form.get("answer")
        answers = []
        boolea = []

        split_string = string.split()

        for i in range(0, len(split_string) - 1,2) :
            if i < len(split_string) - 1:
                answers.append(" ".join([split_string[i], split_string[i+1]]))
            else:
                answers.append(split_string[i])
        
        for i in range(num_q):
            boolean = 2
            temp = answers[i].split()

            if (temp[0] == "True"):
                boolean = 1
            elif (temp[0] == "False"):
                boolean = 0

            
            if (boolean != 2):
                if (questions[int(temp[1]) - 1]["answer"] == boolean):
                    boolean = 1
                    right += 1
                    answerd += 1
                else:
                    boolean = 0
                    answerd += 1
                
            db.execute("INSERT INTO Answers (user_id, question_id, correct) VALUES (:user_id, :question_id, :c)", user_id=session["user_id"], question_id = int(temp[1]), c = boolean)
            boolea.append(boolean)
            answers[i] = temp[0]
            
        return render_template("results.html", answers = answers, boolea = boolea, length = len(answers), questions = questions, var = var, right = right) 
    
    var.clear()    
    while len(var) < num_q:
        k=random.randint(0,11)
        if k not in var:
            var.append(k)
    questions = db.execute("SELECT * FROM Questions")
    return render_template("answer.html", num_q = num_q, questions = questions, var = var)  
    
    
@app.route("/LeaderBoard")
@login_required
def LeaderBoards():
    return render_template("rankings.html")
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    
    error = ""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Input Username"
            return render_template("login.html", error = error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Input Password"
            return render_template("login.html", error = error)

        # Query database for username
        rows = db.execute("SELECT * FROM Users WHERE user_name = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pash"], request.form.get("password")):
            error = "Password Incorrect"
            return render_template("login.html", error = error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    error = ""

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Input Username"
            return render_template("register.html", error = error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Input Password"
            return render_template("register.html", error = error)
         
        # Ensure password equals confirmation 
        elif request.form.get("confirmation") != request.form.get("password"):
            error = "Password Doesn't Match Confirmation"
            return render_template("register.html", error = error)
        
        # Ensures useername is available
        rows = db.execute("SELECT * FROM Users WHERE user_name = :username", username=request.form.get("username"))
        
        if len(rows) != 0:
            error = "Username Taken"
            return render_template("register.html", error = error)
            
        # Stores user
        Username = request.form.get("username") 
        PasHash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO Users (user_name, pash) VALUES (:Username, :PasHash)", Username=Username, PasHash=PasHash)
        
        return redirect("/")
            
    else:
        return render_template("register.html")
        



