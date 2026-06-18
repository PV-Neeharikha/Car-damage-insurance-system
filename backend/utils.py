import os
import cv2
import numpy as np
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from models import (damage_model,parts_model,severity_model)

from constants import class_names

from config import (damage_colors,display_names,damage_to_part,AMBIGUOUS_CLASSES)
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
    upload_path = os.path.join(BASE_DIR,"uploads",f"{side}_{file.filename}") #The uploaded image is saved in uploads folder
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
        damage_details.append({"damage": class_name,"display_name": display_names.get(class_name, class_name),"severity": severity,"confidence": confidence,"box": (x1,y1,x2,y2)})
        
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
    
    output_path = os.path.join(BASE_DIR,"static","results",f"{side}_{file.filename}")#Storing the final image in static/results

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
