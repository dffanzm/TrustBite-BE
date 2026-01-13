# 🧠 TrustBite AI Core (The Intelligent Backend)

![TrustBite Backend Badge](https://img.shields.io/badge/TrustBite-AI%20Core-10B981?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![OCR Engine](https://img.shields.io/badge/Engine-HalalAIEngine%20V5-purple?style=for-the-badge)

---

## 📖 Introduction

Selamat datang di **TrustBite AI Core** — otak dari seluruh ekosistem TrustBite.

Ini bukan backend CRUD receh. Ini adalah **mesin analisis kognitif** yang dirancang untuk membaca, memahami, dan memutuskan status kehalalan produk makanan dari **gambar dunia nyata**.

Backend ini ditenagai **Python** dengan **FastAPI (async, ngebut)**. Namun bintang utamanya adalah **HalalAIEngine V5 — "The Librarian"**.

Engine ini bukan sekadar OCR. Ia:

* Menyaring noise visual (barcode, tabel nutrisi, teks marketing)
* Mengekstrak komposisi relevan
* Melakukan *fuzzy matching* terhadap ribuan bahan global
* Menghasilkan keputusan **HALAL / HARAM / SYUBHAT** berbasis confidence score

Keamanan? Tidak setengah-setengah. Filosofi **Defense in Depth** diterapkan dari layer HTTP sampai logic internal.

---

## 🚀 Key Features

* **Advanced OCR Pipeline**
  EasyOCR + OpenCV preprocessing (CLAHE, denoising, adaptive thresholding) untuk teks susah dibaca.

* **HalalAIEngine V5 (The Librarian)**
  Parsing teks presisi tinggi dengan logika *Surgical Splitter*.

* **Fuzzy Matching Intelligence**
  TheFuzz untuk toleransi typo OCR ("Sugqr" → "Sugar").

* **Dynamic Ingredient Database**
  Database `ingredients.json` hasil scraping ribuan bahan global (OpenFoodFacts).

* **Enterprise-Grade Security**

  * Rate Limiting (SlowAPI)
  * Secure API Key Validation (`secrets.compare_digest`)
  * Strict CORS Policy

---

## 🛠️ Tech Stack & Libraries

* **Language:** Python 3.10+
* **Framework:** FastAPI + Uvicorn
* **OCR & CV:** EasyOCR, OpenCV (`opencv-python-headless`)
* **Data Processing:** NumPy, TheFuzz
* **Security:** SlowAPI, Pydantic Settings
* **Utilities:** Python-Multipart, Requests

---

## 📋 Prerequisites

Pastikan environment siap tempur:

* Python **3.10+**
* PIP
* Virtual Environment (**wajib, jangan barbar**)

---

## ⚡ Installation & Setup

### 1️⃣ Masuk ke Folder Backend

```bash
cd backend
```

---

### 2️⃣ Setup Virtual Environment (WAJIB)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

⏳ *Catatan:* `easyocr` & `torch` agak berat. Sabar, ini otaknya.

---

### 4️⃣ Setup Environment Variables

Buat file `.env` di root folder `backend`.

```env
API_SECRET_KEY=developmentbydaffa
CONFIDENCE_THRESHOLD=80
```

---

### 5️⃣ Generate Ingredient Database (Sekali Saja)

"Kasih makan" AI sebelum dipakai.

```bash
python scripts/generate_db.py
```

Output akan tersimpan di:

```
app/data/ingredients.json
```

---

## 🏃‍♂️ Running the Server

```bash
python -m uvicorn app.main:app --reload
```

Server aktif di:

```
http://127.0.0.1:8000
```

Swagger Docs:

```
http://127.0.0.1:8000/docs
```

---

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── limiter.py
│   ├── services/
│   │   └── ocr_engine.py     # 🔥 HalalAIEngine V5
│   ├── models/
│   │   └── schemas.py
│   ├── data/
│   │   └── ingredients.json
│   └── main.py
├── scripts/
│   └── generate_db.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🔍 API Endpoints

### Health Check

```http
GET /
```

Response:

```json
{"status": "ok"}
```

---

### Analyze Product Image

```http
POST /api/v1/analyze
```

**Headers**

* `x-api-key` (required)

**Body**

* `file` → Image (jpg / png)

**Response**

```json
{
  "status": "HALAL",
  "confidence": 92,
  "ingredients": ["Sugar", "Salt", "Water"]
}
```

---

## ✨ Author

Engineered with 🧠 & 🐍 by **Daffa Najmudin Hanif**

Built for precision. Secured by design. Ready for scale.
