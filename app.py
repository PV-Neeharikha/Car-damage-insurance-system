from flask import Flask, request ,render_template
from ultralytics import YOLO

import cv2
import os

from flask import send_file

from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from datetime import datetime

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from tensorflow.keras.models import load_model
import numpy as np
import json


app=Flask(__name__)

inspection_results = {}

damage_model = YOLO("models/damage_model.pt") #Damage detection model
parts_model = YOLO("models/parts_model.pt") #Part detection model
severity_model = load_model("models/efficientnetb0_car_damage_severity.keras")# Severity datection model

with open("class_names.json","r") as f:
    class_names = json.load(f)

damage_colors = {

    "Front-windscreen-damage": (255, 255, 0),
    "Rear-windscreen-Damage": (255, 255, 0),

    "Headlight-damage": (0, 255, 255),
    "Taillight-Damage": (0, 255, 255),

    "Sidemirror-Damage": (255, 0, 255),

    "Runningboard-Damage": (0, 165, 255),

    "bonnet-dent": (0, 0, 255),
    "boot-dent": (0, 0, 255),
    "doorouter-dent": (0, 0, 255),
    "fender-dent": (0, 0, 255),
    "front-bumper-dent": (0, 0, 255),
    "quaterpanel-dent": (0, 0, 255),
    "rear-bumper-dent": (0, 0, 255),
    "roof-dent": (0, 0, 255)
} # Different colours for each damage

display_names = {
    "Front-windscreen-damage": "Front Windscreen Damage",
    "Headlight-damage": "Headlight Damage",
    "Rear-windscreen-Damage": "Rear Windscreen Damage",
    "Runningboard-Damage": "Running Board Damage",
    "Sidemirror-Damage": "Side Mirror Damage",
    "Taillight-Damage": "Tail Light Damage",
    "bonnet-dent": "Bonnet Dent",
    "boot-dent": "Boot Dent",
    "doorouter-dent": "Door Outer Dent",
    "fender-dent": "Fender Dent",
    "front-bumper-dent": "Front Bumper Dent",
    "quaterpanel-dent": "Quarter Panel Dent",
    "rear-bumper-dent": "Rear Bumper Dent",
    "roof-dent": "Roof Dent"
} # Proper names instad of model names 

damage_to_part = {
    "Headlight-damage": "Headlight",
    "Taillight-Damage": "Tail-light",
    "Front-windscreen-damage": "Windshield",
    "Rear-windscreen-Damage": "Back-windshield",
    "Sidemirror-Damage": "Mirror",
    "front-bumper-dent": "Front-bumper",
    "rear-bumper-dent": "Back-bumper",
    "bonnet-dent": "Hood",
    "boot-dent": "Trunk",
    "fender-dent": "Fender",
    "roof-dent": "Roof",
    "quaterpanel-dent": "Quarter-panel",
    "Runningboard-Damage": "Rocker-panel"
}

AMBIGUOUS_CLASSES = {
    "doorouter-dent"
}

#Used to calculate the severity

def predict_severity(crop):

    crop = cv2.resize(
        crop,
        (224,224)
    )

    crop = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2RGB
    )

    crop = np.expand_dims(
        crop,
        axis=0
    )

    preds = severity_model.predict(
        crop,
        verbose=0
    )[0]

    pred_idx = np.argmax(preds)

    return class_names[pred_idx]

#Used to calculate the overlap

def calculate_iou(boxA, boxB):

    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])

    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    if interArea == 0:
        return 0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(
        boxAArea + boxBArea - interArea
    )

#Used to do for each side

def process_vehicle_side(file, side):
    upload_path = os.path.join("uploads",f"{side}_{file.filename}") #The uploaded image is saved in uploads folder
    file.save(upload_path)

    damage_results = damage_model.predict(source=upload_path,save=False) #Damage result
    parts_results = parts_model.predict(source=upload_path,save=False) #Part result
    
    original_img = cv2.imread(upload_path)

    img = original_img.copy() #Read the image

    detected_parts = []
    part_boxes=[]
    for box in parts_results[0].boxes:
        class_id = int(box.cls[0])
        part_name = parts_model.names[class_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        detected_parts.append(part_name)
        part_boxes.append({
            "name": part_name,
            "box": (x1, y1, x2, y2)
        })
    print("Detected Parts:")
    print(detected_parts)

    damage_classes = []
    detected_damages = [] 
    damage_boxes=[]
    damage_details = []
    severity_results = []

    for box in damage_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        height,width = original_img.shape[:2]
        padding = 5
        crop_x1 = max(0,x1-padding)
        crop_y1 = max(0,y1-padding)
        crop_x2 = min(width,x2+padding)
        crop_y2 = min(height,y2+padding)
        damage_crop = original_img[
            crop_y1:crop_y2,
            crop_x1:crop_x2
        ]
        
        severity = predict_severity(damage_crop)
        severity_results.append(severity)
        class_id = int(box.cls[0]) #The damage ID
        class_name = damage_model.names[class_id] #The damage Name
        damage_boxes.append({"damage": class_name,"box": (x1, y1, x2, y2)})
        damage_classes.append(class_name)
        friendly_name = display_names.get(class_name,class_name)# Proper name
        confidence = float(box.conf[0]) #The model's confidence score
        damage_details.append({"damage": class_name,"severity": severity,"confidence": confidence,"box": (x1,y1,x2,y2)})
        
        damage_number = len(detected_damages) + 1
        detected_damages.append(
            f"{damage_number} → {friendly_name} | Severity: {severity.title()} | ({confidence:.0%})"
        ) #Add the damages to detected_damages
        color = damage_colors.get(
            class_name,
            (0, 0, 255)
        )#Get the corresponding color or use default (0,0,255)

        overlay = img.copy() #Copy of the image

        cv2.rectangle(
            overlay,
            (x1, y1),
            (x2, y2),
            color,
            -1 # fills rectangle completely
        ) #FIll the box

        img = cv2.addWeighted(
            overlay,
            0.4,
            img,
            0.6,
            0
        ) #Making sure its translucent and not opaque

        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            color,
            2 #Thickness
        ) #Outline of the box

        box_number = len(detected_damages)
        circle_x = max(x1, 20)
        circle_y = max(y1, 20)
        cv2.circle(img,(circle_x, circle_y),18,color,-1)

        text = str(box_number)

        (text_w, text_h), _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            2
        )

        text_x = circle_x - text_w // 2
        text_y = circle_y + text_h // 2
        cv2.putText(img,text,(text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,255), 2) #Adding the label for each of the box
    
    output_path = os.path.join("static","results",f"{side}_{file.filename}")#Storing the final image in static/results

    cv2.imwrite(output_path, img)
    return {"damages": detected_damages,"damage_classes": damage_classes,"parts": detected_parts,"part_boxes": part_boxes,"damage_boxes": damage_boxes,"damage_details": damage_details,"severity_results": severity_results,"image": f"results/{side}_{file.filename}"}

#Used for ambiguous classes

def get_damaged_parts(data):

    damaged_parts = set()

    for damage_item in data["damage_boxes"]:

        damage_name = damage_item["damage"]
        damage_box = damage_item["box"]

        best_part = None
        best_iou = 0

        for part_item in data["part_boxes"]:

            iou = calculate_iou(
                damage_box,
                part_item["box"]
            )

            if iou > best_iou:

                best_iou = iou
                best_part = part_item["name"]

        # Ambiguous classes → use IoU

        if damage_name in AMBIGUOUS_CLASSES:

            if best_part and best_iou > 0.20:

                damaged_parts.add(best_part)

            continue

        # Normal classes → direct mapping

        mapped_part = damage_to_part.get(
            damage_name
        )

        if mapped_part:

            damaged_parts.add(mapped_part)

        else:

            damaged_parts.add(
                display_names.get(
                    damage_name,
                    damage_name
                )
            )

    return damaged_parts

@app.route("/")
def home():
    return render_template("Front.html") #Initial Home page


@app.route("/classify",methods=["POST"])
def classification():

    front_file = request.files["front"]
    back_file = request.files["back"]
    left_file = request.files["left"]
    right_file = request.files["right"]
    top_file = request.files.get("top") # Get the file from the frontend

    vehicle_views = {"FRONT": front_file,"BACK": back_file,"LEFT": left_file,"RIGHT": right_file}

    required_files = [front_file,back_file,left_file,right_file]

    for uploaded_file in required_files:

        if uploaded_file.filename == "":

            return "All four images are required" #Incase no image gets uploaded
    
    global inspection_results

    inspection_results = {}

    if top_file and top_file.filename != "":
        vehicle_views["TOP"] = top_file

    for side, file in vehicle_views.items():
        inspection_results[side] = process_vehicle_side(file,side)


    return render_template("Results.html",results=inspection_results) #Calling the results page

@app.route("/download-report")
def download_report():
    global inspection_results
    pdf_path = "Damage_Report.pdf"
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle",parent=styles["Title"],fontSize=24,textColor=colors.HexColor("#1F4E79"),alignment=TA_CENTER)
    section_style = ParagraphStyle("SectionStyle",parent=styles["Heading2"],fontSize=18,textColor=colors.HexColor("#3F6625"))

    elements = []

    elements.append(Paragraph("AI VEHICLE DAMAGE INSPECTION REPORT",title_style))

    elements.append(Spacer(1,15))

    elements.append(Paragraph("Insurance-Oriented Multi-View Vehicle Damage Assessment",styles["Italic"]))

    elements.append(Spacer(1,10))

    elements.append(Paragraph(f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",styles["Normal"]))

    elements.append(Spacer(1,10))

    summary_data = [["Vehicle Side", "Damage Status", "Damage Count"]]

    elements.append(Spacer(1,20))

    elements.append(Paragraph("VEHICLE VIEWS ANALYSED",section_style))

    elements.append(Spacer(1,10))

    for side in inspection_results.keys():
        elements.append(Paragraph(f"✓ {side}",styles["BodyText"]))
    
    elements.append(Paragraph("AI MODELS USED",section_style))

    elements.append(Spacer(1,10))

    elements.append(Paragraph("• Damage Model (YOLOv8)",styles["BodyText"]))

    elements.append(Paragraph("• Parts Model (YOLOv8)",styles["BodyText"]))

    elements.append(Spacer(1,15))

    elements.append(Paragraph("OVERALL DAMAGE SUMMARY",section_style))

    elements.append(Spacer(1,10))

    total_damage_count = 0

    sides = list(inspection_results.items())

    for index,(side,data) in enumerate(sides):

        damage_count = len(data["damages"])
        total_damage_count += damage_count
        status = (
            "Damaged"
            if damage_count > 0
            else "No Damage")

        summary_data.append([side,status,str(damage_count)])

    summary_table = Table(summary_data,colWidths=[150,150,120])

    summary_table.setStyle(
        TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black)]))

    elements.append(summary_table)

    elements.append(Spacer(1,20))

    elements.append(PageBreak())

    for index,(side,data) in enumerate(sides):

        pdf_image_path = os.path.join("static",data["image"])

        elements.append(Spacer(1,10))

        elements.append(Paragraph(f"{side} VIEW ANALYSIS",section_style))

        elements.append(Spacer(1,10))

        if os.path.exists(pdf_image_path):

            elements.append(Image(pdf_image_path,width=350,height=250))
            elements.append(Spacer(1,10))
            elements.append(Paragraph(f"Figure: {side} View Damage Inspection",styles["Italic"]))
            elements.append(Spacer(1,10))

        elements.append(Spacer(1,10))

        damaged_parts = set()
        part_severity = {}

        for item in data["damage_details"]:

            damage_name = item["damage"]

            # Ambiguous classes -> IoU mapping

            if damage_name in AMBIGUOUS_CLASSES:

                damage_box = item["box"]

                best_part = None
                best_iou = 0

                for part_item in data["part_boxes"]:

                    iou = calculate_iou(
                        damage_box,
                        part_item["box"]
                    )

                    if iou > best_iou:

                        best_iou = iou
                        best_part = part_item["name"]

                if best_part and best_iou > 0.20:

                    damaged_parts.add(best_part)
                    part_severity[best_part] = item["severity"]

            # Normal classes -> direct mapping

            else:

                mapped_part = damage_to_part.get(
                    damage_name
                )

                if mapped_part:

                    damaged_parts.add(mapped_part)
                    part_severity[mapped_part] = item["severity"]

        print(f"\n{side}")
        print("DAMAGED PARTS =", damaged_parts)
        all_components = set(data["parts"])

        for damaged in damaged_parts:
            all_components.add(damaged)

        table_data = [
            ["Component", "Status", "Severity"]
        ]
        for part in sorted(all_components):

            status = (
                "Damaged"
                if part in damaged_parts
                else "No Damage"
            )

            severity = "-"

            if status == "Damaged":

                severity = part_severity.get(
                    part,
                    "-"
                )
            print(
    f"{side} | "
    f"Part={part} | "
    f"Status={status} | "
    f"Severity={severity}"
)
            table_data.append([
                part,
                status,
                severity.title()
                if severity != "-"
                else "-"
            ])

        table = Table(
            table_data,
            colWidths=[180,120,100]
        )

        table_style = [
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]

        for row in range(1,len(table_data)):

            status = table_data[row][1]
            severity = str(table_data[row][2]).lower()

            if severity == "severe":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#F4CCCC")
                    )
                )

            elif severity == "moderate":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#FCE5CD")
                    )
                )

            elif severity == "minor":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#D9EAD3")
                    )
                )

            elif status == "No Damage":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#E8F5E9")
                    )
                )

        table.setStyle(
            TableStyle(table_style)
        )

        elements.append(table)

        elements.append(Spacer(1,20))
        if index != len(sides)-1:
            elements.append(PageBreak())


    elements.append(Spacer(1,20))
    elements.append(PageBreak())

    elements.append(Paragraph("FINAL ASSESSMENT",section_style))

    elements.append(Spacer(1,10))

    affected_sides = []

    for side,data in inspection_results.items():

        if len(data["damages"]) > 0:

            affected_sides.append(side)

    severity = (
        "Low"
        if total_damage_count <= 2
        else "Moderate"
        if total_damage_count <= 5
        else "High")

    conclusion = f"""The AI inspection detected a total of{total_damage_count} damage instance(s).Affected Vehicle Sides:{', '.join(affected_sides)}
        Estimated Visible Damage Severity:{severity}
        Recommendation:
        A detailed physical inspection should be
        performed before final repair cost estimation
        and insurance claim settlement.
        """
    elements.append(Paragraph(conclusion,styles["BodyText"]))

    doc.build(elements)

    return send_file(
        pdf_path,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)