# 🛡️ DeepShield – AI Deepfake Detector with Blockchain Verification

DeepShield is a full-stack application that detects deepfake images/videos using AI and ensures authenticity using blockchain-based verification.

---

## 🚀 Features

* 📤 Upload images or videos for analysis
* 🧠 AI-powered deepfake detection
* 🔐 SHA-256 hash generation for media
* ⛓️ Blockchain-based authenticity proof (local / Ethereum-ready)
* 🔍 Verify media using SHA-256 hash
* 💾 Stores analysis history in database
* 🎨 Modern responsive UI (React + Vite)

---

## 🏗️ Project Structure

```
deepfake-detector/
├── backend/        # Flask API + AI + DB + Blockchain logic
├── frontend/       # React frontend (Vite)
├── contracts/      # Solidity smart contract
└── docker-compose.yml
```

---

## ⚙️ Tech Stack

* **Frontend:** React (Vite)
* **Backend:** Flask (Python)
* **AI/ML:** PyTorch, FaceNet, OpenCV
* **Database:** SQLite
* **Blockchain:** Solidity (local simulation / Ethereum ready)

---

## 🧠 How It Works

```
Upload Media
     ↓
AI Detection (Real/Fake)
     ↓
Generate SHA-256 Hash
     ↓
Store in Database
     ↓
Register on Blockchain
     ↓
Verify anytime using hash
```

---

## 🖥️ Setup & Run Locally

### 🔹 Backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

### 🔹 Frontend

```
cd frontend
npm install
npm run dev
```

---

## 🔍 API Endpoints

* `POST /analyse` → Upload & analyze media
* `POST /verify` → Verify using SHA-256
* `GET /history` → Get previous records

---

## 🔐 Blockchain Note

* Uses **local blockchain simulation** for development
* Can be upgraded to **Ethereum (Sepolia testnet)** using Web3

 

---

## 🎯 Future Improvements

* Real-time video stream detection
* Ethereum smart contract integration
* Improved AI model accuracy
* User authentication system

---

## 👨‍💻 Author

Aryan Shedge

---

## ⭐ Show Your Support

If you like this project, give it a ⭐ on GitHub!
