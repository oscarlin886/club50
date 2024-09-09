import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, usd, admin_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///clubs.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show their portfolio of requests"""
    # go to admin if admin
    if session["user_id"] == 1:
        return redirect(url_for("admin"))
    # get their portfolio of requests
    portfolio = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session["user_id"])
    if not portfolio:
        return apology("No Grants Found", 200)
    # sum the approved values and set into the user's cash
    sum = db.execute("SELECT IFNULL(SUM(moneyrequested), 0) AS sum FROM portfolio WHERE user_id = ? AND status = 'Approved'", session["user_id"])
    db.execute("UPDATE users SET cash = ? WHERE id = ?", sum[0]['sum'], session["user_id"])
    # get their current total of granted funds
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    granttotal = usd(cash[0]["cash"])
    return render_template("index.html", portfolio = portfolio, granttotal = granttotal)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """set up club information"""
    #if by POST
    if request.method == "POST":
        # Ensure club name was submitted
        if not request.form.get("newclubname"):
            return apology("must enter previous password", 400)
        # Ensure clubname was submitted or confirmed
        elif not request.form.get("newclubname") or not request.form.get("confirmation"):
            return apology("must provide/confirm password", 400)
        # check that club name matches
        elif request.form.get("newclubname") != request.form.get("confirmation"):
            return apology("Club names do not match", 400)

        # update club name otherwise
        db.execute("UPDATE users SET clubname = ? WHERE id = ?", request.form.get("newclubname"), session["user_id"])
        # update the portfolios as well
        db.execute("UPDATE portfolio SET clubname = ? WHERE user_id = ?", request.form.get("newclubname"), session["user_id"])
        # update clubname table
        clubname = db.execute("SELECT clubname FROM users WHERE id = ?", session["user_id"])
        db.execute("UPDATE forum SET clubname = ?", clubname[0]["clubname"])
        return redirect("/")

    #if by GET
    else:
        return render_template("profile.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

    if request.method == "POST":

        # Ensure username and club name were submitted
        if not request.form.get("username") or not request.form.get("clubname"):
            return apology("must provide username and a club name", 400)

        # check duplicate usernames
        if db.execute("SELECT username FROM users WHERE username LIKE ?", request.form.get("username")):
            return apology("username taken", 400)

        # Ensure password was submitted or confirmed
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide/confirm password", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # hash the password and insert a new row
        hashpass = generate_password_hash(request.form.get("password"))
        new_row = db.execute("INSERT INTO users (username, hash, clubname) VALUES (?, ?, ?)", request.form.get("username"), hashpass, request.form.get("clubname"))

        # login the user and remeber them and redirect user to home page
        session["user_id"] = new_row
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/request", methods=["GET", "POST"])
@login_required
def req():
    """Requesting funds"""

    #if by POST
    if request.method == "POST":
        # the fractional thing is being dumb
        try:
            funding_request = int(request.form.get("amount"))
        except ValueError:
            return apology("requests must be an Integer Number", 400)
        # ensure something submitted
        if not request.form.get("amount") or not request.form.get("reason"):
            return apology("please enter a reason and request amount", 400)
        # ensure positive number of funding
        elif int(request.form.get("amount")) <= 0 or not str.isdigit(request.form.get("amount")):
            return apology("must be postive/nonfractional number for your request amount", 400)
        # add their request
        clubname = db.execute("SELECT clubname FROM users WHERE id = ?", session["user_id"])
        db.execute("INSERT INTO portfolio (user_id, requestreason, moneyrequested, clubname, date) VALUES (?, ?, ?, ?, ?)", session["user_id"], request.form.get("reason"), request.form.get("amount"), clubname[0]["clubname"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return redirect("/")
    #if by GET
    else:
        if session["user_id"] == 1:
            return apology("Not Available to Admins", 400)
        return render_template("request.html")

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    """admin page for approving or denying applicants"""
    # if by POST
    if request.method == "POST":
        # get the grants normally first
        grants = db.execute("SELECT id, status FROM portfolio")
        # get form ids
        formids = request.form.getlist('id')
        # iterate through all the id's from the form
        for currentid in formids:
            # change to approved if pending or denied
            if grants[int(currentid)-1]["status"] == "Pending" or grants[int(currentid)-1]["status"] == "Denied":
                db.execute("UPDATE portfolio SET status = 'Approved' WHERE id = ?", currentid)
            # else deny that one
            else:
                db.execute("UPDATE portfolio SET status = 'Denied' WHERE id = ?", currentid)
        #remake admin.html
        grants = db.execute("SELECT * FROM portfolio ORDER BY CASE WHEN status = 'Pending' THEN 1 WHEN status = 'Denied' THEN 2 WHEN status = 'Approved' THEN 3 ELSE 4 END")
        if not grants:
            return apology("No Pending/Approved/Denied Grants")
        return render_template("admin.html", grants = grants)

    # if by GET
    grants = db.execute("SELECT * FROM portfolio ORDER BY CASE WHEN status = 'Pending' THEN 1 WHEN status = 'Denied' THEN 2 WHEN status = 'Approved' THEN 3 ELSE 4 END")
    if not grants:
        return apology("No Pending/Approved/Denied Grants", 400)
    return render_template("admin.html", grants = grants)


@app.route("/comments", methods=["GET", "POST"])
@login_required
def forum():
    """a page for comments"""
    # if by POST
    if request.method == "POST":
        #check for inputs
        if not request.form.get("comment"):
            return apology("Missing Comment")
        elif not request.form.get("email"):
            return apology("Missing Email")
        # add the comment
        clubname = db.execute("SELECT clubname FROM users WHERE id = ?", session["user_id"])
        db.execute("INSERT INTO forum (user_id, comment, clubname, email) VALUES(?, ?, ?, ?)", session["user_id"], request.form.get("comment"), clubname[0]["clubname"], request.form.get("email"))
        comments = db.execute("SELECT * FROM forum ORDER BY id DESC")
        if not comments:
            return apology("No Comments Found", 400)
        return render_template("comments.html", comments = comments)
    #if by GET
    comments = db.execute("SELECT * FROM forum ORDER BY id DESC")
    if not comments:
        return apology("No Comments Found", 400)
    return render_template("comments.html", comments = comments)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """a change your password route!"""
    # if by post
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("oldpass"):
            return apology("must enter previous password", 400)

        # Ensure password was submitted or confirmed
        elif not request.form.get("oldpass") or not request.form.get("newpass") or not request.form.get("confirmation"):
            return apology("must provide/confirm password", 400)

        # Ensure password and confirmation match
        elif request.form.get("newpass") != request.form.get("confirmation"):
            return apology("new passwords do not match", 400)

        # ensure old password is correct
        oldpasshash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(oldpasshash[0]["hash"], request.form.get("oldpass")):
            return apology("incorrect previous password", 400)

        # otherwise: hash the password and insert a new row
        hashpass = generate_password_hash(request.form.get("newpass"))
        new_row = db.execute("UPDATE users SET hash = ? WHERE id = ?", hashpass, session["user_id"])

        return redirect("/")
    # if by GET
    else:
        return render_template("changepass.html")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)