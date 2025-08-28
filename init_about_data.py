#!/usr/bin/env python3
"""
Initialize About page data files for Railway deployment
This script creates the required JSON files in the /data directory
"""
import os
import json

def init_about_data():
    """Initialize About page data files"""
    data_dir = '/data'
    
    # Ensure /data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Create about_content.json
    about_content = {
        "main_content": "Welcome to Mind's Eye Photography, where every moment is captured with artistic vision and technical precision. Our passion lies in transforming fleeting moments into timeless memories that tell your unique story.\n\nWith years of experience in portrait, landscape, and event photography, we specialize in creating images that not only document but also evoke emotion and preserve the essence of each moment. Whether it's a wedding, family portrait, or commercial project, we approach each shoot with creativity, professionalism, and attention to detail.\n\nOur philosophy is simple: photography is not just about taking pictures, it's about seeing the world through a different lens and sharing that vision with others. We believe that every person, every place, and every moment has a story worth telling, and we're here to help you tell yours.\n\nUsing state-of-the-art equipment and techniques, we ensure that every image meets the highest standards of quality while maintaining the authentic feel that makes each photograph special. From the initial consultation to the final delivery, we work closely with our clients to understand their vision and bring it to life.",
        "signature": "- Mind's Eye Photography"
    }
    
    about_content_file = os.path.join(data_dir, 'about_content.json')
    if not os.path.exists(about_content_file):
        with open(about_content_file, 'w') as f:
            json.dump(about_content, f, indent=2)
        print(f"✅ Created {about_content_file}")
    else:
        print(f"ℹ️  {about_content_file} already exists")
    
    # Create about_minds_eye_image.json
    about_image = {
        "filename": None
    }
    
    about_image_file = os.path.join(data_dir, 'about_minds_eye_image.json')
    if not os.path.exists(about_image_file):
        with open(about_image_file, 'w') as f:
            json.dump(about_image, f, indent=2)
        print(f"✅ Created {about_image_file}")
    else:
        print(f"ℹ️  {about_image_file} already exists")

if __name__ == "__main__":
    init_about_data()
    print("🎉 About page data initialization complete!")

