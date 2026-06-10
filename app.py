from flask import Flask, request ,render_template
from ultralytics import YOLO

import cv2
import os

from flask import send_file

from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from datetime import datetime

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle

app=Flask(__name__)

latest_damages = []
latest_damage_classes = []
latest_parts = []
latest_image = ""

damage_model = YOLO("damage_model.pt") #Damage detection model
parts_model = YOLO("parts_model.pt") #Part detection model

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

@app.route("/")
def home():
    return render_template("Front.html") #Initial Home page


@app.route("/classify",methods=["POST"])
def classification():

    file=request.files["damage"] # Get the file from the frontend

    if file.filename == "":
        return "No image selected" #Incase no image gets uploaded
    
    upload_path = os.path.join("uploads", file.filename) #The uploaded image is saved in uploads folder
    file.save(upload_path)

    damage_results = damage_model.predict(source=upload_path,save=False) #Damage result
    parts_results = parts_model.predict(source=upload_path,save=False) #Part result
    
    img = cv2.imread(upload_path) #Read the image

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

    for box in damage_results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_id = int(box.cls[0]) #The damage ID
        class_name = damage_model.names[class_id] #The damage Name
        damage_boxes.append({"damage": class_name,"box": (x1, y1, x2, y2)})
        damage_classes.append(class_name)
        friendly_name = display_names.get(class_name,class_name)# Proper name
        confidence = float(box.conf[0]) #The model's confidence score

        damage_number = len(detected_damages) + 1
        detected_damages.append(
            f"{damage_number} → {friendly_name} ({confidence:.0%})"
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
    
    output_path = os.path.join(
        "static",
        "results",
        file.filename
    )#Storing the final image in static/results

    cv2.imwrite(output_path, img)

    global latest_damages
    global latest_damage_classes
    global latest_parts
    global latest_part_boxes
    global latest_damage_boxes
    global latest_image

    latest_damages = detected_damages
    latest_damage_classes = damage_classes
    latest_parts = detected_parts

    latest_part_boxes = part_boxes
    latest_damage_boxes = damage_boxes

    latest_image = output_path

    return render_template(
        "Results.html",
        image_path=f"results/{file.filename}",
        damages=detected_damages
    ) #Calling the results page


@app.route("/download-report")
def download_report():
    from datetime import datetime
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle

    pdf_path = "Damage_Report.pdf"
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle",parent=styles["Title"],fontSize=24,textColor=colors.HexColor("#1F4E79"),alignment=TA_CENTER)
    section_style = ParagraphStyle("SectionStyle",parent=styles["Heading2"],fontSize=18,textColor=colors.HexColor("#3F6625"))
    elements = []


    # TITLE

    elements.append(Paragraph("CAR DAMAGE DETECTION REPORT",title_style))
    elements.append(Spacer(1, 15))
    elements.append( Paragraph(f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",styles["Normal"]))
    elements.append(Spacer(1, 20))


    # SUMMARY

    elements.append(Paragraph("SUMMARY",section_style))
    elements.append(Spacer(1, 10))

    summary_table = Table(
        [
            ["Metric", "Value"],
            ["Total Damages Detected", str(len(latest_damages))],
            ["Total Visible Parts Detected", str(len(set(latest_parts)))]
        ],
        colWidths=[250, 150]
    )

    summary_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # DETECTED DAMAGES

    elements.append(Paragraph("DETECTED DAMAGES",section_style))
    elements.append(Spacer(1, 10))

    if latest_damages:
        for damage in latest_damages:
            elements.append(
                Paragraph(
                    damage,
                    styles["BodyText"]
                )
            )
    else:
        elements.append(
            Paragraph(
                "No damages detected.",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 20))

    # PROCESSED IMAGE

    elements.append(Paragraph("PROCESSED IMAGE",section_style))

    elements.append(Spacer(1, 10))

    if latest_image:
        img = Image(
            latest_image,
            width=420,
            height=300
        )
        elements.append(img)

    elements.append(Spacer(1, 20))

    # INSPECTION TABLE
    
    elements.append(Paragraph("VEHICLE INSPECTION SUMMARY",section_style))
    elements.append(Spacer(1, 10))

    report_data = [
        ["Detected Part", "Status"]
    ]

    # Combine parts detected by Parts Model
    # and parts inferred from Damage Model

    damaged_parts = []

    for damage_item in latest_damage_boxes:
        damage_box = damage_item["box"]
        best_part = None
        best_iou = 0
        for part_item in latest_part_boxes:
            iou = calculate_iou(
                damage_box,
                part_item["box"]
            )
            if iou > best_iou:
                best_iou = iou
                best_part = part_item["name"]
        if best_part:
            damaged_parts.append(best_part)

    all_parts = set(latest_parts)

    for damage in latest_damage_classes:
        mapped_part = damage_to_part.get(damage)
        if mapped_part:
            all_parts.add(mapped_part)
            if mapped_part not in damaged_parts:
                damaged_parts.append(mapped_part)

    for part in sorted(all_parts):

        status = (
            "Damaged"
            if part in damaged_parts
            else "No Damage"
        )

        report_data.append(
            [part, status]
        )

    table = Table(
        report_data,
        colWidths=[250, 150]
    )

    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B9BD5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]

    for row in range(1, len(report_data)):

        if report_data[row][1] == "Damaged":

            table_style.append(
                (
                    'BACKGROUND',
                    (0, row),
                    (-1, row),
                    colors.HexColor("#F4CCCC")
                )
            )

        else:

            table_style.append(
                (
                    'BACKGROUND',
                    (0, row),
                    (-1, row),
                    colors.HexColor("#D9EAD3")
                )
            )

    table.setStyle(TableStyle(table_style))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # CONCLUSION

    elements.append(Paragraph("CONCLUSION",section_style))

    elements.append(Spacer(1, 10))

    if len(latest_damages) == 0:

        conclusion = ("No visible damages were detected in the uploaded vehicle image.")
    else:
        conclusion = (
            f"{len(latest_damages)} damaged component(s) were detected by the AI system."
        )
    
    elements.append(Paragraph(conclusion,styles["BodyText"]))

    elements.append(Spacer(1, 20))

    doc.build(elements)

    return send_file(
        pdf_path,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)