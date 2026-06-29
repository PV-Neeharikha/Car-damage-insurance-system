#  AI-Powered Car Damage Detection & Insurance Estimation

An AI-powered web application that detects vehicle damages from uploaded images, identifies affected vehicle parts, estimates repair costs based on insurance policies, and generates a professional damage assessment report.

---

##  Features

-  Detects multiple types of vehicle damage using YOLO
-  Supports multi-view vehicle inspection
  - Front
  - Back
  - Left
  - Right
  - Optional Top View
- 🛠 Identifies damaged vehicle parts
- 📊 Classifies damage severity
- 💰 Estimates repair costs based on insurance policy coverage
- 📄 Generates downloadable PDF inspection reports
- 🌐 Simple web interface for uploading vehicle images

---

## 🛠 Tech Stack

### Backend
- Python
- Flask

### AI & Machine Learning
- YOLO (Ultralytics)
- TensorFlow / Keras
- EfficientNetB0
- OpenCV

### Frontend
- HTML
- CSS
- JavaScript

### Libraries
- NumPy
- Pandas
- ReportLab

---

## 📂 Project Structure

```text
CAR-DAMAGE-DETECTION/
│
├── backend/
│   ├── app.py                    # Flask application
│   ├── config.py                 # Application configuration
│   ├── constants.py              # Project constants
│   ├── insurance.py              # Insurance cost estimation logic
│   ├── models.py                 # AI model loading and inference
│   ├── report_generator.py       # PDF report generation
│   ├── utils.py                  # Helper functions
│   └── users.json                # User data storage
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx
│   │   │   ├── ResultsPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   └── SignupPage.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── ml_models/                    # Trained AI models
├── insurance_costs/              # Insurance pricing datasets
├── templates/                    # HTML templates
├── static/                       # Static assets
├── uploads/                      # Uploaded images
├── class_names.json              # Damage class labels
├── classes.py                    # Damage class utilities
├── requirements.txt
└── README.md
```

---

## ⚙️ Workflow

1. Upload vehicle images.
2. Detect vehicle damages using the YOLO damage detection model.
3. Detect affected vehicle parts.
4. Match damages with corresponding vehicle parts.
5. Classify damage severity using EfficientNetB0.
6. Estimate repair cost using insurance policy data.
7. Generate an annotated damage report in PDF format.

---

## 🧠 AI Pipeline

```
Vehicle Images
        │
        ▼
Damage Detection (YOLO)
        │
        ▼
Parts Detection (YOLO)
        │
        ▼
Damage ↔ Part Mapping
        │
        ▼
Severity Classification (EfficientNetB0)
        │
        ▼
Insurance Cost Estimation
        │
        ▼
PDF Report Generation
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/Car-damage-insurance-system.git
```

Move into the project

```bash
cd Car-damage-insurance-system
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

## 📈 Future Improvements

- Real-time damage detection from video
- Mobile application support
- Cloud deployment
- VIN-based vehicle identification
- AI-powered repair recommendations
- Support for additional insurance providers

---

## 👩‍💻 Author

**Neeharikha P V**

GitHub: https://github.com/PV-Neeharikha
