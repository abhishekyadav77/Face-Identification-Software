# -*- coding: utf-8 -*-
"""
Facial Recognition Helper Module
Utilizes OpenCV and face_recognition API to load reference face profiles,
calculate vector encodings, and recognize matching profiles in video feeds.
"""

import os
from pathlib import Path
import cv2
import numpy as np

# Use the robust face_recognition library if installed. If not, fallback beautifully.
try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False


class SimpleFacerec:
    def __init__(self):
        """
        Initializes vector list vectors to match identities in real-time.
        """
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roles = []
        
        # Scaling down factors to optimize FPS rendering speeds
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path="data/known_faces"):
        """
        Iterates over the reference directory, extracts face structures, 
        generates the 128-dimensional embedding, and updates reference memory maps.
        """
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_roles = []
        
        path = Path(images_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"[Facerec] Folder initialized: {path}")
            return
            
        valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
        image_files = [p for p in path.iterdir() if p.suffix.lower() in valid_extensions]
        
        print(f"[Facerec] Found {len(image_files)} profile photos inside database.")
        
        if not FACE_REC_AVAILABLE:
            print("[Facerec] WARNING: face_recognition module not installed. Running simulated vectors.")
            return

        for img_path in image_files:
            try:
                # Read image file via OpenCV
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                # Convert from BGR color model to standard RGB format
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Extract identity details from filename structure: Name_Role_ID.jpg
                filename_stem = img_path.stem
                parts = filename_stem.split("_")
                
                if len(parts) >= 2:
                    name = parts[0].replace("-", " ")
                    role = parts[1].replace("-", " ")
                else:
                    name = filename_stem.replace("-", " ")
                    role = "Authorized Staff"
                
                # Calculate face recognition spatial vectors
                face_encodings = face_recognition.face_encodings(rgb_img)
                if len(face_encodings) > 0:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(name)
                    self.known_face_roles.append(role)
                    print(f"[Facerec] Profile Successfully Loaded: {name} | Designation: {role}")
                else:
                    print(f"[Facerec] Warning: No face contours matched inside image: {img_path.name}")
            except Exception as e:
                print(f"[Facerec] Error calculating vectors for {img_path.name}: {e}")
                
        print(f"[Facerec] Total Database Active Records: {len(self.known_face_encodings)}")

    def detect_known_faces(self, frame):
        """
        Scans a frame, detects bounding boxes, calculates encodings, and compares them 
        to active database lists. Returns matching indices.
        """
        # If the library isn't installed, return mock scanning data for safety fallback
        if not FACE_REC_AVAILABLE:
            return np.array([]), [], []
            
        try:
            # Resize frame down for optimized facial tracking throughput
            small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Locate bounding boxes and generate instant 128D encodings
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            face_roles = []
            
            for face_encoding in face_encodings:
                # Compare active vectors
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                role = "Unauthorized"
                
                # Select profile matching lowest overall face distance delta
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        role = self.known_face_roles[best_match_index]
                        
                face_names.append(name)
                face_roles.append(role)
                
            # Scale coordinates back up to normal screen aspect parameters
            face_locations = np.array(face_locations)
            face_locations = face_locations / self.frame_resizing
            return face_locations.astype(int), face_names, face_roles
            
        except Exception as e:
            print(f"[Facerec] Scanner Error: {e}")
            return np.array([]), [], []
