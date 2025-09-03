import os
import json
from flask import Blueprint, request, render_template_string, redirect, url_for, session, jsonify
from PIL import Image as PILImage
from PIL.ExifTags import TAGS
from datetime import datetime
from ..config import PHOTOGRAPHY_ASSETS_DIR, PORTFOLIO_DATA_FILE

def load_portfolio_data():
    """Load portfolio data from SQL database - EXACT SAME AS ADMIN DASHBOARD"""
    try:
        from ..models import Image, Category
        
        # Get all images from database - sorted by capture date newest to oldest
        images = Image.query.order_by(
            Image.upload_date.desc()
        ).all()
        portfolio_data = []
        
        for image in images:
            # Get categories for this image
            image_categories = [cat.category.name for cat in image.categories]
            
            portfolio_data.append({
                'id': image.id,
                'image': image.filename,  # Featured manager expects 'image' field
                'title': image.title,
                'description': image.description,
                'categories': image_categories,
                'upload_date': image.upload_date.isoformat() if image.upload_date else None,
            })
        
        return portfolio_data
    except Exception as e:
        print(f"Error loading portfolio data from SQL: {e}")
    return []

featured_bp = Blueprint('featured', __name__)

# File paths
FEATURED_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'featured-image.json')
STATIC_ASSETS_DIR = PHOTOGRAPHY_ASSETS_DIR  # Use the same directory as configured

def load_featured_data():
    """Load featured image data from SQL database"""
    try:
        from ..models import Image
        
        # Get the currently featured image
        featured_image = Image.query.filter_by(is_featured=True).first()
        
        if featured_image:
            # Get categories for this image
            image_categories = [cat.category.name for cat in featured_image.categories]
            
            return {
                'id': featured_image.id,
                'image': featured_image.filename,
                'title': featured_image.title,
                'description': featured_image.description,
                'categories': image_categories,
                'story': featured_image.featured_story or '',
                'set_date': featured_image.upload_date.strftime('%Y-%m-%d %H:%M:%S') if featured_image.upload_date else 'Unknown',
                'exif_data': {}  # Will be populated if needed
            }
    except Exception as e:
        print(f"Error loading featured data from SQL: {e}")
    return None

def save_featured_data(image_id, story):
    """Save featured image data to SQL database"""
    try:
        from ..models import Image, db
        
        # Clear any existing featured image
        Image.query.filter_by(is_featured=True).update({'is_featured': False, 'featured_story': None})
        
        # Set the new featured image
        featured_image = Image.query.get(image_id)
        if featured_image:
            featured_image.is_featured = True
            featured_image.featured_story = story
            
            db.session.commit()
            return True
        else:
            print(f"Image with ID {image_id} not found")
            return False
            
    except Exception as e:
        print(f"Error saving featured data to SQL: {e}")
        db.session.rollback()
        return False

def extract_exif_data(image_path):
    """Extract EXIF data from image"""
    try:
        with PILImage.open(image_path) as image:
            exif_data = {}
            
            # Get basic EXIF data
            exif = image._getexif()
            if exif is not None:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except:
                            value = str(value)
                    
                    # Format common EXIF tags
                    if tag == 'Make':
                        exif_data['camera_make'] = str(value)
                    elif tag == 'Model':
                        exif_data['camera_model'] = str(value)
                    elif tag == 'LensModel':
                        exif_data['lens_model'] = str(value)
                    elif tag == 'FocalLength':
                        if isinstance(value, tuple) and len(value) == 2:
                            focal_length = value[0] / value[1] if value[1] != 0 else value[0]
                            exif_data['focal_length'] = f"{focal_length:.1f}mm"
                        else:
                            exif_data['focal_length'] = f"{value}mm"
                    elif tag == 'FNumber':
                        if isinstance(value, tuple) and len(value) == 2:
                            f_number = value[0] / value[1] if value[1] != 0 else value[0]
                            exif_data['aperture'] = f"f/{f_number:.1f}"
                        else:
                            exif_data['aperture'] = f"f/{value}"
                    elif tag == 'ExposureTime':
                        if isinstance(value, tuple) and len(value) == 2:
                            if value[0] < value[1]:
                                exif_data['shutter_speed'] = f"1/{int(value[1]/value[0])}"
                            else:
                                exif_data['shutter_speed'] = f"{value[0]/value[1]:.2f}s"
                        else:
                            exif_data['shutter_speed'] = str(value)
                    elif tag == 'ISOSpeedRatings':
                        exif_data['iso'] = f"ISO {value}"
                    elif tag == 'Flash':
                        flash_fired = value & 1
                        exif_data['flash'] = "Yes" if flash_fired else "No"
            
            return exif_data
            
    except Exception as e:
        print(f"Error extracting EXIF data from {image_path}: {e}")
        return {}

@featured_bp.route('/api/featured')
def get_featured_image():
    """API endpoint to get current featured image data with EXIF"""
    featured_data = load_featured_data()
    
    if featured_data and featured_data.get('image'):
        # Try multiple possible image locations
        possible_paths = [
            os.path.join(STATIC_ASSETS_DIR, featured_data['image']),  # Photography assets dir
            os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', featured_data['image']),  # Static assets
            os.path.join('/home/ubuntu/mindseye-complete-restore/src/static/assets', featured_data['image'])  # Absolute static path
        ]
        
        exif_data = {}
        for image_path in possible_paths:
            if os.path.exists(image_path):
                print(f"Found image at: {image_path}")
                exif_data = extract_exif_data(image_path)
                break
            else:
                print(f"Image not found at: {image_path}")
        
        featured_data['exif_data'] = exif_data
    
    return jsonify(featured_data)

@featured_bp.route('/admin/featured-image')
def featured_admin():
    """Featured image admin interface"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        # Load portfolio and featured data
        portfolio_data = load_portfolio_data()
        featured_data = load_featured_data()
        
        admin_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Featured Image Management</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: #000; 
                    color: #fff; 
                    margin: 0; 
                    padding: 20px; 
                }
                .header { 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin-bottom: 30px; 
                    padding-bottom: 20px; 
                    border-bottom: 2px solid #ff6b35; 
                }
                .header h1 { 
                    color: #ff6b35; 
                    margin: 0; 
                }
                .btn { 
                    background: #ff6b35; 
                    color: white; 
                    padding: 10px 20px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    border: none; 
                    cursor: pointer; 
                    font-size: 14px; 
                }
                .btn:hover { 
                    background: #e55a2b; 
                }
                .current-featured { 
                    background: #1a1a1a; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin-bottom: 30px; 
                    border: 2px solid #ff6b35; 
                }
                .portfolio-grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin-top: 20px; 
                }
                .portfolio-item { 
                    background: #1a1a1a; 
                    border-radius: 10px; 
                    overflow: hidden; 
                    transition: transform 0.3s; 
                    border: 2px solid transparent; 
                }
                .portfolio-item:hover { 
                    transform: scale(1.05); 
                    border-color: #ff6b35; 
                }
                .portfolio-item img { 
                    width: 100%; 
                    height: 150px; 
                    object-fit: cover; 
                }
                .portfolio-item-info { 
                    padding: 15px; 
                }
                .portfolio-item h3 { 
                    margin: 0 0 10px 0; 
                    color: #ff6b35; 
                    font-size: 16px; 
                }
                .portfolio-item p { 
                    margin: 0 0 15px 0; 
                    color: #ccc; 
                    font-size: 14px; 
                    line-height: 1.4; 
                }
                .categories { 
                    margin-bottom: 15px; 
                }
                .category-tag { 
                    background: #ff6b35; 
                    color: white; 
                    padding: 4px 8px; 
                    border-radius: 12px; 
                    font-size: 12px; 
                    margin-right: 5px; 
                    margin-bottom: 5px; 
                    display: inline-block; 
                }
                .set-featured-btn { 
                    background: #28a745; 
                    color: white; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    font-size: 12px; 
                    width: 100%; 
                }
                .set-featured-btn:hover { 
                    background: #218838; 
                }
                .message { 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-bottom: 20px; 
                }
                .message.success { 
                    background: #d4edda; 
                    color: #155724; 
                    border: 1px solid #c3e6cb; 
                }
                .message.error { 
                    background: #f8d7da; 
                    color: #721c24; 
                    border: 1px solid #f5c6cb; 
                }
                .exif-info { 
                    background: #2a2a2a; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin-top: 15px; 
                }
                .exif-grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 10px; 
                    margin-top: 10px; 
                }
                .exif-item { 
                    background: #3a3a3a; 
                    padding: 10px; 
                    border-radius: 5px; 
                }
                .exif-label { 
                    color: #ff6b35; 
                    font-weight: bold; 
                    font-size: 12px; 
                    text-transform: uppercase; 
                }
                .exif-value { 
                    color: #fff; 
                    font-size: 14px; 
                    margin-top: 5px; 
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Featured Image Management</h1>
                <a href="/admin" class="btn">Back to Admin Dashboard</a>
            </div>

            {% if message %}
                <div class="message {{ message_type }}">{{ message }}</div>
            {% endif %}

            {% if featured_data %}
                <div class="current-featured">
                    <h2 style="color: #ff6b35; margin-bottom: 15px;">Current Featured Image</h2>
                    <div style="display: flex; gap: 20px; align-items: flex-start;">
                        <img src="/static/assets/{{ featured_data.image }}" 
                             alt="{{ featured_data.title }}" 
                             style="width: 300px; height: 200px; object-fit: cover; border-radius: 8px;">
                        <div style="flex: 1;">
                            <h3 style="color: #fff; margin: 0 0 10px 0;">{{ featured_data.title }}</h3>
                            <p style="color: #ccc; margin: 0 0 15px 0;">{{ featured_data.description }}</p>
                            <div class="categories">
                                {% for category in featured_data.categories %}
                                    <span class="category-tag">{{ category }}</span>
                                {% endfor %}
                            </div>
                            {% if featured_data.story %}
                                <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; margin-top: 15px;">
                                    <h4 style="color: #ff6b35; margin: 0 0 10px 0;">Story Behind the Shot</h4>
                                    <p style="color: #fff; margin: 0; line-height: 1.5;">{{ featured_data.story }}</p>
                                </div>
                            {% endif %}
                            <p style="color: #888; font-size: 12px; margin-top: 15px;">
                                Set on: {{ featured_data.set_date }}
                            </p>
                        </div>
                    </div>
                </div>
            {% else %}
                <div class="current-featured">
                    <h2 style="color: #ff6b35; margin-bottom: 15px;">No Featured Image Set</h2>
                    <p style="color: #ccc;">Select an image from the portfolio below to set as featured.</p>
                </div>
            {% endif %}

            <h2 style="color: #ff6b35; margin-bottom: 20px;">Portfolio Images</h2>
            <div class="portfolio-grid">
                {% for image in portfolio_data %}
                    <div class="portfolio-item">
                        <img src="/static/assets/{{ image.image }}" alt="{{ image.title }}">
                        <div class="portfolio-item-info">
                            <h3>{{ image.title }}</h3>
                            <p>{{ image.description }}</p>
                            <div class="categories">
                                {% for category in image.categories %}
                                    <span class="category-tag">{{ category }}</span>
                                {% endfor %}
                            </div>
                            <form method="POST" action="/admin/featured/set" style="margin: 0;">
                                <input type="hidden" name="image_id" value="{{ image.id }}">
                                <div style="margin-bottom: 10px;">
                                    <label style="display: block; color: #ff6b35; font-size: 14px; margin-bottom: 5px;">Story Behind the Shot:</label>
                                    <textarea name="featured_story" placeholder="Enter the story behind this image..." 
                                              style="width: 100%; height: 80px; padding: 8px; border: 1px solid #555; border-radius: 5px; background: #333; color: #fff; font-size: 12px; resize: vertical;">{{ image.featured_story or '' }}</textarea>
                                </div>
                                <button type="submit" class="set-featured-btn">Set as Featured</button>
                            </form>
                        </div>
                    </div>
                {% endfor %}
            </div>
        </body>
        </html>
        '''
        
        return render_template_string(admin_html, 
                                    portfolio_data=portfolio_data,
                                    featured_data=featured_data,
                                    message=request.args.get('message'),
                                    message_type=request.args.get('message_type', 'success'))
        
    except Exception as e:
        return f"Error loading featured admin: {str(e)}"

@featured_bp.route('/admin/featured/set', methods=['POST'])
def set_featured_image():
    """Set an image as featured and save story to SQL database"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        image_id = request.form.get('image_id')
        featured_story = request.form.get('featured_story', '')
        
        # Update the image in SQL database
        from ..models import Image, db
        
        # First, clear any existing featured image
        Image.query.filter_by(is_featured=True).update({'is_featured': False})
        
        # Set the new featured image and save story
        image = Image.query.get(image_id)
        if image:
            image.is_featured = True
            image.featured_story = featured_story
            db.session.commit()
            
            return redirect(url_for('featured.featured_admin') + '?success=Featured image and story saved successfully!')
        else:
            return redirect(url_for('featured.featured_admin') + '?error=Image not found')
            
    except Exception as e:
        return redirect(url_for('featured.featured_admin') + f'?error=Error setting featured image: {str(e)}')

