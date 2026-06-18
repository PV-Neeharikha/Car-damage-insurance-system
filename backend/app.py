from flask import Flask, request, jsonify, send_file

import cv2
import os

from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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