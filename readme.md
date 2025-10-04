# 🧾 Tesseract OCR FastAPI Service

A lightweight **FastAPI-based OCR microservice** using **Tesseract** and **OpenCV** to extract text and structured fields (amount, date, merchant) from receipts, invoices, and bills.

---

## 🚀 Features
- Extracts **raw text** using Tesseract OCR
- Preprocesses images with **OpenCV** (grayscale + threshold + denoise)
- Detects structured fields:
  - 💰 Amount  
  - 📅 Date  
  - 🏪 Merchant name
- Simple REST API, easy to integrate with any app
- Ready for deployment on Render / Railway / Hugging Face

---

## ⚙️ Setup Instructions

### 1️⃣ Clone & Install
```bash
git clone https://github.com/<your-username>/tesseract-ocr-api.git
cd tesseract-ocr-api
pip install -r requirements.txt
