#gemini

from flask import Flask, request, render_template
from google import genai
import google.generativeai as genai2
import os
import sqlite3
import datetime
import requests


api_key = os.getenv("gemini") #AIzaSyBTInBvJ6wvpw8rHHOFspHIIJYLkNQLFL8
#AIzaSyDD89GjmQPDluuUAojC7ds-Ramlc1XVrcc
genai2.configure(api_key="api_key")

#genai.configure(api_key="AIzaSyDD89GjmQPDluuUAojC7ds-Ramlc1XVrcc")
model = genai2.GenerativeModel("gemini-2.0-flash")
gemini_telegram_token = os.getenv("gemini_telegram_token") 

gemini_client = genai.Client(api_key=api_key)
gemini_model = "gemini-2.0-flash"

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


@app.route("/start_telegram",methods=["GET","POST"])
def start_telegram():

    domain_url = os.getenv('WEBHOOK_URL')

    # The following line is used to delete the existing webhook URL for the Telegram bot
    delete_webhook_url = f"https://api.telegram.org/bot{gemini_telegram_token}/deleteWebhook"
    requests.post(delete_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    
    # Set the webhook URL for the Telegram bot
    set_webhook_url = f"https://api.telegram.org/bot{gemini_telegram_token}/setWebhook?url={domain_url}/telegram"
    webhook_response = requests.post(set_webhook_url, json={"url": domain_url, "drop_pending_updates": True})
    print('webhook:', webhook_response)
    if webhook_response.status_code == 200:
        # set status message
        status = "The telegram bot is running. Please check with the telegram bot. @gemini_tt_bot"
    else:
        status = "Failed to start the telegram bot. Please check the logs."
    
    return(render_template("telegram.html", status=status))


@app.route("/telegram",methods=["GET","POST"])
def telegram():
    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        # Extract the chat ID and message text from the update
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text == "/start":
            r_text = "Welcome to the Gemini Telegram Bot! You can ask me any finance-related questions."
        else:
            # Process the message and generate a response
            system_prompt = "You are a financial expert.  Answer ONLY questions related to finance, economics, investing, and financial markets. If the question is not related to finance, state that you cannot answer it."
            prompt = f"{system_prompt}\n\nUser Query: {text}"
            r = gemini_client.models.generate_content(
                model=gemini_model,
                contents=prompt
            )
            r_text = r.text
        
        # Send the response back to the user
        send_message_url = f"https://api.telegram.org/bot{gemini_telegram_token}/sendMessage"
        requests.post(send_message_url, data={"chat_id": chat_id, "text": r_text})
    # Return a 200 OK response to Telegram
    # This is important to acknowledge the receipt of the message
    # and prevent Telegram from resending the message
    # if the server doesn't respond in time
    return('ok', 200)

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
