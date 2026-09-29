"""Optical Character Recognition (OCR) Service for Crisis Screenshots.
Supports local Tesseract OCR with OpenCV preprocessing, with automatic
multimodal Gemini Vision fallback when Tesseract is not installed on the system.
"""
import os
import shutil
from typing import Tuple
from PIL import Image
import numpy as np

# Standard Tesseract search paths on Windows
TESSERACT_CANDIDATE_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
]

def _configure_tesseract():
    try:
        import pytesseract
        # Check if already in PATH
        if shutil.which("tesseract"):
            return pytesseract
        for p in TESSERACT_CANDIDATE_PATHS:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                return pytesseract
        return pytesseract
    except ImportError:
        return None

def is_ocr_available() -> Tuple[bool, str]:
    """Check if local Tesseract OCR engine or Gemini Vision fallback is available."""
    pytess = _configure_tesseract()
    if pytess:
        try:
            pytess.get_tesseract_version()
            return True, "Local Tesseract OCR active"
        except Exception:
            pass
            
    # Check if Gemini Vision is available as fallback
    from services.gemini import get_model
    if get_model():
        return True, "Gemini Multimodal Vision OCR active (Fallback)"
        
    return False, "Tesseract OCR binary not detected and Gemini API unconfigured."

def extract_text_from_image(uploaded_file) -> str:
    """
    Extract text from an uploaded image using local Tesseract (with OpenCV preprocessing)
    or Gemini Vision multimodal fallback.
    """
    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file)
    except Exception as e:
        print(f"Image read error: {e}")
        return ""

    # 1. Try local Tesseract OCR first
    pytess = _configure_tesseract()
    if pytess:
        try:
            # Test if tesseract binary is actually executable
            pytess.get_tesseract_version()
            
            # Preprocessing with OpenCV if available
            try:
                import cv2
                open_cv_image = np.array(image)
                if len(open_cv_image.shape) == 3 and open_cv_image.shape[2] == 3:
                    open_cv_image = open_cv_image[:, :, ::-1].copy()
                    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                    text = pytess.image_to_string(thresh).strip()
                    if not text:
                        text = pytess.image_to_string(gray).strip()
                    if text:
                        return text
            except Exception:
                pass
                
            text = pytess.image_to_string(image).strip()
            if text:
                return text
        except Exception as e:
            # Tesseract binary not installed or failed
            print(f"Local Tesseract OCR unavailable: {e}")

    # 2. Multimodal LLM Fallback (Gemini Vision)
    try:
        from services.gemini import get_model
        model = get_model()
        if model:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            img = Image.open(uploaded_file)
            prompt = "Transcribe all visible text from this screenshot or crisis image accurately. Output only the extracted text, nothing else."
            response = model.generate_content([prompt, img])
            if response and response.text:
                return response.text.strip()
    except Exception as e:
        print(f"Gemini Vision fallback error: {e}")

    return ""
