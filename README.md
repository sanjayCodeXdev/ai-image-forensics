# 🔍 AI Image Authenticity Detection & Digital Forensics System

> A full-stack web application to analyze whether an image is **real**, **AI-generated**, or **inconclusive**, using a multi-layer forensic pipeline.

**Team:**
- Subasri N
- Sanjay Kumar M
- Soundharya K

---

## ⚠️ Important Principles

- **Metadata alone is never treated as proof.** Metadata can be removed, edited, or fabricated.
- **The system never claims 100% accuracy.** Results are estimations only.
- **Multiple analysis layers** are fused into a weighted final verdict.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Tailwind CSS + Recharts |
| Backend | Python 3.8 + FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy + aiosqlite |
| Image Analysis | Pillow, OpenCV, NumPy |
| AI Detection | EfficientNet-B0 (PyTorch — optional) |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd "YOUR_REPO_NAME"
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```
Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/api/docs

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```
Frontend runs at: http://localhost:5173

---

## 📱 Testing on Mobile (Same Wi-Fi)

1. Find your PC's local IP:
   ```
   ipconfig   (Windows)
   ifconfig   (Mac/Linux)
   ```
   Example: `192.168.1.10`

2. Start backend binding to all interfaces:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. Start frontend with host flag:
   ```bash
   npm run dev -- --host
   ```

4. Open on your phone:
   - App: `http://192.168.1.10:5173`
   - API: `http://192.168.1.10:8000/api/docs`

> 💡 **Tip:** Update `frontend/.env` to set `VITE_API_BASE_URL=http://192.168.1.10:8000`

---

## 🧠 Analysis Pipeline

```
Upload → Metadata Analysis → Provenance (C2PA) → Watermark Check
       → AI Visual Detection (EfficientNet) → Digital Forensics (ELA/Noise/Edge)
       → Evidence Fusion (Weighted) → Final Verdict
```

### Analysis Modules

| Module | What it checks |
|---|---|
| **Metadata** | EXIF/XMP/IPTC tags, AI software signatures |
| **Provenance** | C2PA / Content Credentials manifests |
| **Watermark** | OpenAI & Google SynthID signals (stubs — APIs not public) |
| **Visual AI** | EfficientNet-B0 CNN model (requires `models/image_detector.pt`) |
| **Forensics** | ELA, noise analysis, frequency domain, edge consistency, texture |

---

## 🤖 Training the AI Model (Optional)

To enable the Visual AI Detection module:

```bash
cd backend

# Organize your dataset:
# dataset/real/   ← real photographs
# dataset/ai/     ← AI-generated images

python train_model.py
```

The trained model will be saved to `backend/models/image_detector.pt`.

Without the model, all other analysis modules still work and the fusion engine redistributes weights automatically.

---

## 📁 Project Structure

```
mini project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & environment vars
│   │   ├── database.py          # SQLAlchemy async setup
│   │   ├── models.py            # DB models
│   │   ├── schemas.py           # Pydantic response schemas
│   │   ├── routes/              # API route handlers
│   │   └── services/            # Analysis pipeline services
│   │       ├── upload_service.py
│   │       ├── metadata_analyzer.py
│   │       ├── provenance_analyzer.py
│   │       ├── watermark_analyzer.py
│   │       ├── visual_detector.py
│   │       ├── forensic_analyzer.py
│   │       ├── evidence_fusion.py
│   │       └── report_generator.py
│   ├── models/                  # Place image_detector.pt here
│   ├── uploads/                 # Uploaded images (gitignored)
│   ├── requirements.txt
│   └── train_model.py           # Model training script
└── frontend/
    ├── src/
    │   ├── pages/               # Home, Analyze, Results, History, About
    │   └── components/          # UploadBox, Charts, Evidence cards
    ├── index.html
    └── package.json
```

---

## 📋 Environment Variables

Create `backend/.env`:
```env
SECRET_KEY=your-secret-key-here
MAX_FILE_SIZE_MB=10
# Optional — for watermark checks when APIs become available
OPENAI_API_KEY=
GOOGLE_API_KEY=
```

Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## ⚖️ Limitations

- Results are **estimations** — not legal evidence
- The AI model requires training data to function
- C2PA verification requires the `c2pa-python` library
- Watermark APIs (OpenAI, Google SynthID) are not publicly available
- Compressed, resized, or edited images may produce unreliable forensic signals
