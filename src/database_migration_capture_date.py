#!/usr/bin/env python3
"""
Database Migration: Add capture_date field and populate from EXIF data
"""

import os
import sys
from datetime import datetime
from PIL import Image as PILImage
from PIL.ExifTags import TAGS

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import db, Image
from src.config import PHOTOGRAPHY_ASSETS_DIR

def extract_capture_date_from_exif(image_path):
    """Extract capture date from EXIF data"""
    try:
        with PILImage.open(image_path) as img:
            exif_data = img._getexif()
            
            if exif_data is not None:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Look for DateTime tags
                    if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        try:
                            # Parse EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
                            capture_date = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            print(f"   📅 Found capture date: {capture_date}")
                            return capture_date
                        except ValueError as e:
                            print(f"   ⚠️  Could not parse date '{value}': {e}")
                            continue
                            
    except Exception as e:
        print(f"   ❌ Error reading EXIF data: {e}")
    
    return None

def migrate_capture_dates():
    """Migrate existing images to add capture dates from EXIF data"""
    print("🔄 Starting capture date migration...")
    
    # Get all images from database
    images = Image.query.all()
    print(f"📊 Found {len(images)} images in database")
    
    if len(images) == 0:
        print("ℹ️  No images to migrate")
        return
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for image in images:
        print(f"\n🔍 Processing: {image.filename}")
        
        # Skip if capture_date already exists
        if image.capture_date:
            print(f"   ⏭️  Already has capture date: {image.capture_date}")
            skipped_count += 1
            continue
        
        # Get image file path
        image_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, image.filename)
        
        if not os.path.exists(image_path):
            print(f"   ❌ Image file not found: {image_path}")
            error_count += 1
            continue
        
        # Extract capture date from EXIF
        capture_date = extract_capture_date_from_exif(image_path)
        
        if capture_date:
            image.capture_date = capture_date
            updated_count += 1
            print(f"   ✅ Updated capture date: {capture_date}")
        else:
            print(f"   ⚠️  No capture date found in EXIF data")
            # Use file modification time as fallback
            try:
                file_mtime = os.path.getmtime(image_path)
                fallback_date = datetime.fromtimestamp(file_mtime)
                image.capture_date = fallback_date
                updated_count += 1
                print(f"   📁 Using file modification time: {fallback_date}")
            except Exception as e:
                print(f"   ❌ Could not get file modification time: {e}")
                error_count += 1
    
    # Commit all changes
    try:
        db.session.commit()
        print(f"\n🎉 Migration completed successfully!")
        print(f"   ✅ Updated: {updated_count} images")
        print(f"   ⏭️  Skipped: {skipped_count} images (already had capture date)")
        print(f"   ❌ Errors: {error_count} images")
        
        # Show some statistics
        total_with_capture_date = Image.query.filter(Image.capture_date.isnot(None)).count()
        print(f"   📊 Total images with capture date: {total_with_capture_date}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration failed: {e}")
        raise

def update_exif_data_for_all_images():
    """Update EXIF data for all images (including new capture_date field)"""
    print("\n🔄 Updating EXIF data for all images...")
    
    images = Image.query.all()
    updated_count = 0
    
    for image in images:
        image_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, image.filename)
        
        if not os.path.exists(image_path):
            continue
            
        try:
            with PILImage.open(image_path) as img:
                exif_data = img._getexif()
                
                if exif_data is not None:
                    # Update existing EXIF fields
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == 'Make' and not image.camera_make:
                            image.camera_make = str(value)[:100]
                        elif tag == 'Model' and not image.camera_model:
                            image.camera_model = str(value)[:100]
                        elif tag == 'LensModel' and not image.lens_model:
                            image.lens_model = str(value)[:100]
                        elif tag == 'FocalLength' and not image.focal_length:
                            if isinstance(value, tuple) and len(value) == 2:
                                focal_mm = value[0] / value[1] if value[1] != 0 else value[0]
                                image.focal_length = f"{focal_mm:.1f}mm"
                            else:
                                image.focal_length = f"{value}mm"
                        elif tag == 'FNumber' and not image.aperture:
                            if isinstance(value, tuple) and len(value) == 2:
                                f_number = value[0] / value[1] if value[1] != 0 else value[0]
                                image.aperture = f"f/{f_number:.1f}"
                            else:
                                image.aperture = f"f/{value}"
                        elif tag == 'ExposureTime' and not image.shutter_speed:
                            if isinstance(value, tuple) and len(value) == 2:
                                if value[0] == 1:
                                    image.shutter_speed = f"1/{value[1]}"
                                else:
                                    exposure_time = value[0] / value[1]
                                    image.shutter_speed = f"{exposure_time:.2f}s"
                            else:
                                image.shutter_speed = str(value)
                        elif tag == 'ISOSpeedRatings' and not image.iso:
                            image.iso = str(value)
                    
                    updated_count += 1
                    
        except Exception as e:
            print(f"   ⚠️  Error updating EXIF for {image.filename}: {e}")
    
    try:
        db.session.commit()
        print(f"✅ Updated EXIF data for {updated_count} images")
    except Exception as e:
        db.session.rollback()
        print(f"❌ EXIF update failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting database migration for capture dates...")
    
    # Initialize Flask app context
    from src.main import app
    with app.app_context():
        # Run migrations
        migrate_capture_dates()
        update_exif_data_for_all_images()
        
    print("\n🎉 Migration completed!")

