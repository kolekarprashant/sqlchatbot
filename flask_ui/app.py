# app.py
from flask import Flask, render_template, request, redirect,session
import requests
from dotenv import load_dotenv
import os
import uuid

app = Flask(__name__)
#app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")  # Fallback if no env set
app.secret_key = "c00b551695036d4c7bd772d32afd7eb63069eaa988f64b44b5b426ab14e58bbd"
#FASTAPI_URL = "http://127.0.0.1:8000"
# for docker
FASTAPI_URL = "http://0.0.0.0:8000"

@app.before_request
def make_session_non_permanent():
    session.permanent = False

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        session["chat_history"] = []
        
    if "chat_history" not in session:
        session["chat_history"] = []

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    if request.method == "POST":        
       user_input = request.form["user_input"]
       print(user_input)
       res = requests.post(f"{FASTAPI_URL}/query/", json={"question": user_input,"session_id": session["session_id"]})
       print(res)
       response = res.json().get("response")
       print(response)
       session["chat_history"].append({"question": user_input, "response": response})
       session.modified = True  
    return render_template("index.html", chat_history=session["chat_history"])


      

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
