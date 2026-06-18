from ultralytics import YOLO
from tensorflow.keras.models import load_model

damage_model = YOLO("ml_models/damage_model.pt") #Damage detection model
parts_model = YOLO("ml_models/parts_model.pt") #Part detection model
severity_model = load_model("ml_models/efficientnetb0_car_damage_severity.keras")# Severity datection model
