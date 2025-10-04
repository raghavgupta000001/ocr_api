from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re
import numpy as np
import cv2

# -----------------------------
#  APP CONFIGURATION
# -----------------------------
app = FastAPI(
    title="Enhanced Tesseract OCR API",
    description="Extracts text and structured data (amount, date, merchant) from receipts using Tesseract OCR + OpenCV preprocessing.",
    version="2.0.0"
)

# Allow CORS (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: specify tesseract executable path (Windows users only)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -----------------------------
#  IMAGE PREPROCESSING
# -----------------------------
def preprocess_image(image: Image.Image) -> np.ndarray:
    """Convert image to grayscale, remove noise, and threshold to improve OCR accuracy."""
    # Convert PIL image to OpenCV format
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise & threshold (adaptive for uneven lighting)
    gray = cv2.medianBlur(gray, 3)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )

    # Optional: Morphological operations for text enhancement
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return processed


# -----------------------------
#  TEXT PARSING
# -----------------------------
def parse_receipt_text(text: str):
    """Extract key info like amount, date, and merchant name from OCR text."""
    result = {}

    # Amount extraction (₹, $, €, or numeric pattern)
    amount_match = re.search(r'(\$|₹|€)\s?(\d+(?:\.\d{1,2})?)', text)
    if amount_match:
        result['amount'] = amount_match.group()
    else:
        fallback_amount = re.search(r'\b\d{1,5}\.\d{2}\b', text)
        if fallback_amount:
            result['amount'] = fallback_amount.group()

    # Date extraction
    date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)
    if not date_match:
        date_match = re.search(r'(\d{4}[/-]\d{2}[/-]\d{2})', text)
    if date_match:
        result['date'] = date_match.group()

    # Merchant name extraction (first line or line containing keywords)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        possible_merchant = lines[0]
        for line in lines:
            if re.search(r'(RESTAURANT|STORE|HOTEL|CAFE|MART|SHOP|COMPANY)', line.upper()):
                possible_merchant = line
                break
        result['merchant'] = possible_merchant

    return result


# -----------------------------
#  API ENDPOINTS
# -----------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Enhanced Tesseract OCR API 🚀"}


@app.post("/extract-receipt")
async def extract_receipt(file: UploadFile = File(...)):
    """
    Upload a receipt image and get:
    - Preprocessed OCR text
    - Structured data (amount, date, merchant)
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Please upload a valid image file (jpg, png, etc.)")

        # Read image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Preprocess for better OCR
        processed_image = preprocess_image(image)

        # OCR with Tesseract
        text = pytesseract.image_to_string(processed_image, lang="eng")

        # Parse structured info
        info = parse_receipt_text(text)

        return {
            "filename": file.filename,
            "extracted_text": text.strip(),
            "structured_data": info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Enhanced OCR API is running smoothly ✅"}


# -----------------------------
#  RUN LOCALLY
# -----------------------------
# Run this API using: uvicorn app:app --reload
