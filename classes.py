from ultralytics import YOLO

damage_model = YOLO("damage_model.pt")
parts_model = YOLO("parts_model.pt")

print(damage_model.names)
print(" ")
print(parts_model.names)