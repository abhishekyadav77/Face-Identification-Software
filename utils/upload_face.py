# -*- coding: utf-8 -*-
"""
Upload Face Helper Module
Saves uploaded file objects from the Streamlit UI to the known_faces data folder,
cleaning names to match the structured parsing protocol.
"""

import os
from pathlib import Path
import cv2
import numpy as np

def save_uploaded_face(uploaded_file, full_name, role):
    """
    Decodes an uploaded image stream from memory, standardizes file formats, 
    and writes it to disk with structured name indicators.
    """
    try:
        # Secure the target database paths
        target_dir = Path("data/known_faces")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Read the upload stream as raw binary bytes
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return False, "File format not supported. Upload a standard PNG/JPG image."
            
        # Standardize alphanumeric characters to avoid file structure system errors
        sanitized_name = "".join(c for c in full_name if c.isalnum() or c in (" ", "_", "-")).strip()
        sanitized_name = sanitized_name.replace(" ", "-")
        sanitized_role = role.strip().replace(" ", "-")
        
        # Format string: Name_Role_RandomHex.jpg
        unique_token = int(os.urandom(2).hex(), 16)
        filename = f"{sanitized_name}_{sanitized_role}_{unique_token}.jpg"
        save_path = target_dir / filename
        
        # Save image file to directory using OpenCV write
        cv2.imwrite(str(save_path), image)
        return True, f"Successfully registered and saved as: {filename}"
        
    except Exception as e:
        return False, f"System Error writing image: {str(e)}"
