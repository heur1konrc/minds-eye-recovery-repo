#!/usr/bin/env python3
"""
Set the existing about-minds-eye image as the About page image
"""
import json
import os

def set_about_image():
    """Set about-minds-eye-fe05c603.png as the About page image"""
    data_dir = '/data'
    about_image_file = os.path.join(data_dir, 'about_minds_eye_image.json')
    
    # Update the image filename
    about_image_data = {
        "filename": "about-minds-eye-fe05c603.png"
    }
    
    with open(about_image_file, 'w') as f:
        json.dump(about_image_data, f, indent=2)
    
    print(f"✅ Set About page image to: about-minds-eye-fe05c603.png")

if __name__ == "__main__":
    set_about_image()

