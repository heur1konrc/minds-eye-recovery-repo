#!/usr/bin/env python3
"""
Check what's in the /data directory on Railway
"""
import os
import json

def check_data_directory():
    """Check contents of /data directory"""
    data_dir = '/data'
    
    print(f"Checking directory: {data_dir}")
    print(f"Directory exists: {os.path.exists(data_dir)}")
    
    if os.path.exists(data_dir):
        try:
            files = os.listdir(data_dir)
            print(f"Files in {data_dir}: {files}")
            
            # Check specific files
            about_content_file = os.path.join(data_dir, 'about_content.json')
            about_image_file = os.path.join(data_dir, 'about_minds_eye_image.json')
            
            print(f"about_content.json exists: {os.path.exists(about_content_file)}")
            print(f"about_minds_eye_image.json exists: {os.path.exists(about_image_file)}")
            
            if os.path.exists(about_content_file):
                with open(about_content_file, 'r') as f:
                    content = json.load(f)
                    print(f"about_content.json content: {content}")
            
            if os.path.exists(about_image_file):
                with open(about_image_file, 'r') as f:
                    content = json.load(f)
                    print(f"about_minds_eye_image.json content: {content}")
                    
        except Exception as e:
            print(f"Error reading directory: {e}")
    else:
        print(f"Directory {data_dir} does not exist")

if __name__ == "__main__":
    check_data_directory()

