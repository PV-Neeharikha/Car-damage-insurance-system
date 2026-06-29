from flask import Flask, request, jsonify, send_file
import re
import cv2
import os

from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import json
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
import numpy as np
from flask_cors import CORS
from report_generator import *
from config import (damage_colors,display_names,damage_to_part,AMBIGUOUS_CLASSES)
from models import (damage_model,parts_model,severity_model)
from utils import *
from constants import (RAW_COSTS,THIRD_PARTY,POLICY_A,POLICY_B,POLICY_C)
from insurance import *
import os
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

app = Flask(__name__,static_folder=os.path.join(BASE_DIR, "static"))
CORS(app)

inspection_results = {}

USERS_FILE = "backend/users.json"

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    for user in users:

        if (
            user["email"].strip() == email and
            user["password"].strip() == password
        ):

            print("LOGIN SUCCESS")

            return jsonify({
                "success": True,
                "username": user["username"]
            })

    print("LOGIN FAILED")

    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })

@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    # Empty field validation
    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        })

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required"
        })

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required"
        })

    # Email validation
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

    if not re.match(email_regex, email):
        return jsonify({
            "success": False,
            "message": "Invalid email format"
        })

    # Password validation
    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters"
        })

    # Load existing users
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    # Duplicate username/email check
    for user in users:

        if user["username"].lower() == username.lower():
            return jsonify({
                "success": False,
                "message": "Username already exists"
            })

        if user["email"].lower() == email.lower():
            return jsonify({
                "success": False,
                "message": "Email already exists"
            })

    # Add new user
    users.append({
        "username": username,
        "email": email,
        "password": password
    })

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    return jsonify({
        "success": True,
        "message": "Account created successfully"
    })

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    # Check if email already exists
    for user in users:
        if user["email"] == email:
            return jsonify({
                "success": False,
                "message": "Email already exists"
            })

    users.append({
        "username": username,
        "email": email,
        "password": password
    })

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    return jsonify({
        "success": True,
        "message": "Account created successfully"
    })

@app.route("/")
def home():
    return {
        "message": "Vehicle Damage Detection API Running"
    }

@app.route("/classify",methods=["POST"])
def classification():

    front_file = request.files["front"]
    back_file = request.files["back"]
    left_file = request.files["left"]
    right_file = request.files["right"]
    top_file = request.files.get("top") # Get the file from the frontend
    policy_type = request.form["policy_type"] #Get the policy type

    vehicle_views = {"FRONT": front_file,"BACK": back_file,"LEFT": left_file,"RIGHT": right_file}

    required_files = [front_file,back_file,left_file,right_file]

    for uploaded_file in required_files:

        if uploaded_file.filename == "":

            return "All four images are required" #Incase no image gets uploaded
    
    global inspection_results

    inspection_results = {}
    inspection_results["policy_type"] = policy_type

    if top_file and top_file.filename != "":
        vehicle_views["TOP"] = top_file

    for side, file in vehicle_views.items():
        inspection_results[side] = process_vehicle_side(file,side)
        print("CLASSIFY RESULTS")
        print(inspection_results.keys())


    return jsonify(inspection_results)#Calling the results page

@app.route("/download-report")
def download_report():

    pdf_path = generate_pdf_report(
        inspection_results
    )
    print("DOWNLOAD RESULTS")
    print(inspection_results.keys())
    return send_file(
        pdf_path,
        as_attachment=True
    )
if __name__ == "__main__":
    app.run(debug=True)