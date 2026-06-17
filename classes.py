from ultralytics import YOLO

damage_model = YOLO("models/damage_model.pt")
parts_model = YOLO("models/parts_model.pt")

print(damage_model.names)
print(" ")
print(parts_model.names)