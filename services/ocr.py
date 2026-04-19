import pytesseract
from PIL import Image
import cv2
import numpy as np

def extract_text_from_image(uploaded_file):
    try:
        # Read image with PIL
        image = Image.open(uploaded_file)
        
        # Convert to OpenCV format
        open_cv_image = np.array(image) 
        
        # Convert RGB to BGR 
        if len(open_cv_image.shape) == 3 and open_cv_image.shape[2] == 3:
            open_cv_image = open_cv_image[:, :, ::-1].copy() 
            
            # Simple preprocessing to improve OCR
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            # Apply threshold to get black and white image
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Perform OCR on preprocessed image
            text = pytesseract.image_to_string(thresh)
            
            # Fallback if no text found with thresholding
            if not text.strip():
                 text = pytesseract.image_to_string(gray)
        else:
             # If not RGB (e.g. RGBA or grayscale), just use direct extraction
             text = pytesseract.image_to_string(image)
             
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        # Simple fallback without preprocessing
        try:
             image = Image.open(uploaded_file)
             return pytesseract.image_to_string(image).strip()
        except:
             return ""
