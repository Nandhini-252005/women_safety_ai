from ultralytics import YOLO

print("🚀 Loading YOLOv8n model...")
model = YOLO("yolov8n.pt")   # Downloads automatically if missing

print("🔥 Exporting to ONNX...")
model.export(format="onnx")

print("✅ Export completed: yolov8n.onnx generated!")
