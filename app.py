#gemini

from flask import Flask, request, render_template
import google.generativeai as genai
import os
import sqlite3
import datetime

api_key = os.getenv("gemini") #AIzaSyBTInBvJ6wvpw8rHHOFspHIIJYLkNQLFL8
#AIzaSyDD89GjmQPDluuUAojC7ds-Ramlc1XVrcc
genai.configure(api_key="api_key")
#genai.configure(api_key="AIzaSyDD89GjmQPDluuUAojC7ds-Ramlc1XVrcc")
model = genai.GenerativeModel("gemini-2.0-flash")

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/gemini", methods=["GET","POST"])
def gemini():
    return(render_template("gemini.html"))

@app.route("/main", methods=["GET","POST"])
def main():   
    q = request.form.get("q")
    if q:
        t = datetime.datetime.now().astimezone()
        conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("Insert into users(name,timestamp) values(?,?)",(q,t))
        conn.commit()
        c.close()
        conn.close()
    return(render_template("main.html"))

@app.route("/gemini_reply", methods=["GET","POST"])
def gemini_reply():
    q = request.form.get("q")
    print(q)
    #gemini
    r = model.generate_content(q)
    return(render_template("gemini_reply.html",r=r.text))


@app.route("/prediction_reply", methods=["GET","POST"])
def prediction_reply():
    q = float(request.form.get("q"))
    print(q)
    r = 90.2+(-50.6*q)
    return(render_template("prediction_reply.html",r=r))

@app.route("/paynow", methods=["GET","POST"])
def paynow():
    return(render_template("paynow.html"))

@app.route("/prediction", methods=["GET","POST"])
def prediction():
    return(render_template("prediction.html"))

@app.route("/user_log", methods=["GET","POST"])
def user_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("select * from users")
    r=""
    count = 0
    for row in c:
        r = r + str(row)
        count = count + 1
    c.close()
    conn.close()
    return(render_template("user_log.html",r=r,count=count))

@app.route("/delete_log", methods=["GET","POST"])
def delete_log():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute("Delete from users")
    conn.commit()
    c.close()
    conn.close()
    return(render_template("delete_log.html", r="All logs deleted successfully!"))

@app.route("/logout", methods=["GET","POST"])
def logout():
    return(render_template("index.html"))

if __name__== "__main__":
    app.run()
