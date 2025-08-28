"""
Mind's Eye Photography - Main Flask Application
PERSISTENCE TEST: Testing if images survive deployment with /data volume
"""
import os
import sys
import json
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models import db, Image, Category, ImageCategory, SystemConfig, init_default_categories, init_system_config, migrate_existing_images
from src.routes.user import user_bp
from src.routes.contact import contact_bp
from src.routes.admin import admin_bp
from src.routes.background import background_bp
from src.routes.featured_image import featured_bp
from src.routes.portfolio_management import portfolio_mgmt_bp
from src.routes.category_management import category_mgmt_bp
from src.routes.debug_migration import debug_migration_bp
from src.routes.backup_system import backup_system_bp
from src.routes.og_image import og_bp
from src.routes.cleanup_api import cleanup_bp
from src.routes.slideshow_api import slideshow_api_bp  # Simple slideshow API (Option 1)
from src.routes.enhanced_background import enhanced_bg_bp
# from src.routes.slideshow_manager import slideshow_bp as slideshow_manager_bp  # Temporarily disabled for deployment fix
# from src.routes.contact_form import contact_bp  # Temporarily disabled

# Import configuration
from src.config import PHOTOGRAPHY_ASSETS_DIR

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes and origins
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"])

# Ensure photography assets directory exists
os.makedirs(PHOTOGRAPHY_ASSETS_DIR, exist_ok=True)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(contact_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(background_bp)
app.register_blueprint(featured_bp)
app.register_blueprint(category_mgmt_bp)
app.register_blueprint(debug_migration_bp)
app.register_blueprint(backup_system_bp)
app.register_blueprint(og_bp)
app.register_blueprint(cleanup_bp)

app.register_blueprint(slideshow_api_bp)  # Simple slideshow API (Option 1)
app.register_blueprint(enhanced_bg_bp)
# Import and register the slideshow fix blueprint
from src.routes.slideshow_fix import slideshow_fix_bp
app.register_blueprint(slideshow_fix_bp)  # New slideshow fix
# app.register_blueprint(slideshow_manager_bp)  # Temporarily disabled for deployment fix
# app.register_blueprint(portfolio_mgmt_bp)  # Removed - redundant with admin dashboard
# app.register_blueprint(contact_bp)  # Temporarily disabled

# Database configuration - Use persistent volume for database
database_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, 'mindseye.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()
    
    # Only initialize defaults if database is empty (first run)
    if Category.query.count() == 0:
        print("🔄 Empty database detected - initializing default categories...")
        init_default_categories()
    else:
        print(f"✅ Database has {Category.query.count()} categories - skipping initialization")
    
    # Only initialize system config if empty
    if SystemConfig.query.count() == 0:
        print("🔄 Initializing system configuration...")
        init_system_config()
    else:
        print(f"✅ System config exists - skipping initialization")
    
    # Add slideshow column if it doesn't exist
    try:
        # Test if the column exists by trying to query it
        db.session.execute(db.text("SELECT is_slideshow_background FROM images LIMIT 1"))
        print("✅ Slideshow column already exists")
    except Exception as e:
        print("🔄 Adding slideshow column to images table...")
        try:
            db.session.execute(db.text("ALTER TABLE images ADD COLUMN is_slideshow_background BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            print("✅ Slideshow column added successfully")
        except Exception as alter_error:
            print(f"❌ Failed to add slideshow column: {alter_error}")
            db.session.rollback()
    
    # Add is_about column if it doesn't exist
    try:
        # Check if is_about column exists using correct SQLAlchemy syntax
        with db.engine.connect() as conn:
            conn.execute(db.text("SELECT is_about FROM images LIMIT 1"))
        print("✅ is_about column already exists")
    except Exception:
        try:
            # Add the is_about column to existing database using correct syntax
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE images ADD COLUMN is_about BOOLEAN DEFAULT 0"))
                conn.commit()
            print("✅ Added is_about column to existing database")
        except Exception as alter_error:
            print(f"❌ Failed to add is_about column: {alter_error}")
    
    # Add EXIF columns if they don't exist
    try:
        with db.engine.connect() as conn:
            # Check if EXIF columns exist, if not add them
            exif_columns = [
                'camera_make', 'camera_model', 'lens_model', 'focal_length',
                'aperture', 'shutter_speed', 'iso', 'flash', 'exposure_mode', 'white_balance'
            ]
            
            for column in exif_columns:
                try:
                    conn.execute(db.text(f"ALTER TABLE images ADD COLUMN {column} VARCHAR(100)"))
                    print(f"✅ Added {column} column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"ℹ️  {column} column already exists")
                    else:
                        print(f"⚠️  Error adding {column} column: {e}")
            
            conn.commit()
    except Exception as e:
        print(f"⚠️  EXIF column migration error: {e}")
    
    print("✅ EXIF columns migration complete")
    
    # Try creating the table with the new schema
    try:
        db.create_all()
        print("✅ Created tables with new schema")
    except Exception as create_error:
        print(f"❌ Failed to create tables: {create_error}")
    
    # Only migrate images if no images exist in database
    try:
        if Image.query.count() == 0:
            print("🔄 No images in database - running migration...")
            migrate_existing_images()
        else:
            print(f"✅ Database has {Image.query.count()} images - skipping migration")
    except Exception as e:
        print(f"⚠️ Database query issue: {e}")
        # Don't create fresh database - just continue
    
    print("✅ SQL Database initialization complete")

@app.route('/data/<filename>')
def serve_data_image(filename):
    """Serve images from the data directory (portfolio and about images)"""
    # Use Railway volume mount path
    data_dir = '/data'
    return send_from_directory(data_dir, filename)

@app.route('/debug/database-info')
def debug_database_info():
    """Debug route to check database content"""
    try:
        from src.routes.admin import load_portfolio_data
        portfolio_data = load_portfolio_data()
        
        info = {
            'portfolio_count': len(portfolio_data),
            'portfolio_items': portfolio_data[:5],  # First 5 items
            'sample_image_paths': [item.get('image', 'NO_IMAGE') for item in portfolio_data[:10]]
        }
        
        return f"<pre>{json.dumps(info, indent=2)}</pre>"
    except Exception as e:
        return f"<pre>Database error: {str(e)}</pre>"

@app.route('/debug/volume-info')
def debug_volume_info():
    """Debug route to check volume path detection"""
    import os
    from src.config import PHOTOGRAPHY_ASSETS_DIR
    
    info = {
        'PHOTOGRAPHY_ASSETS_DIR': PHOTOGRAPHY_ASSETS_DIR,
        'RAILWAY_VOLUME_MOUNT_PATH': os.environ.get('RAILWAY_VOLUME_MOUNT_PATH'),
        'directory_exists': os.path.exists(PHOTOGRAPHY_ASSETS_DIR),
        'directory_contents': [],
        'environment_vars': {k: v for k, v in os.environ.items() if 'RAILWAY' in k or 'VOLUME' in k}
    }
    
    try:
        if os.path.exists(PHOTOGRAPHY_ASSETS_DIR):
            info['directory_contents'] = os.listdir(PHOTOGRAPHY_ASSETS_DIR)[:10]  # First 10 files
    except Exception as e:
        info['directory_error'] = str(e)
    
    return f"<pre>{json.dumps(info, indent=2)}</pre>"

@app.route('/static/assets/<path:filename>')
def serve_photography_assets(filename):
    """Serve images from the separate photography assets directory"""
    try:
        return send_from_directory(PHOTOGRAPHY_ASSETS_DIR, filename)
    except FileNotFoundError:
        # Fallback to old location for backward compatibility during migration
        old_assets_dir = os.path.join(app.static_folder, 'assets')
        if os.path.exists(os.path.join(old_assets_dir, filename)):
            return send_from_directory(old_assets_dir, filename)
        return f"Image not found. Checked: {PHOTOGRAPHY_ASSETS_DIR}/{filename} and {old_assets_dir}/{filename}", 404

@app.route('/api/slideshow')
def get_slideshow():
    """Get slideshow images from admin system"""
    try:
        from src.models import Image
        
        # Get images marked for slideshow from admin - FIXED COLUMN NAME
        slideshow_images = Image.query.filter(Image.is_slideshow_background == True).all()
        print(f"📊 Found {len(slideshow_images)} slideshow images")
        
        slideshow_data = []
        
        for image in slideshow_images:
            print(f"🎬 Processing slideshow image: {image.filename}")
            slideshow_item = {
                'id': image.id,
                'filename': image.filename,
                'title': image.title,
                'description': image.description
            }
            slideshow_data.append(slideshow_item)
        
        print(f"✅ Returning {len(slideshow_data)} slideshow images")
        return jsonify(slideshow_data)
        
    except Exception as e:
        print(f"❌ Error in slideshow API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 200

@app.route('/api/slideshow-images')
def get_slideshow_images():
    """Alternative slideshow endpoint for compatibility"""
    try:
        slideshow_data = []
        
        slideshow_images = Image.query.filter(Image.is_slideshow_background == True).all()
        
        for image in slideshow_images:
            slideshow_item = {
                'id': image.id,
                'filename': image.filename,
                'title': image.title,
                'description': image.description
            }
            slideshow_data.append(slideshow_item)
        
        return jsonify({
            'success': True,
            'images': slideshow_data
        })
        
    except Exception as e:
        print(f"❌ Error in slideshow-images API: {e}")
        return jsonify({'success': False, 'images': []}), 200

@app.route('/api/simple-portfolio')
def get_simple_portfolio():
    """Bulletproof portfolio endpoint - always returns admin data"""
    try:
        print("🔍 Simple Portfolio API called")
        
        # Get all images from admin database (excluding About images)
        all_images = Image.query.filter(Image.is_about != True).all()
        print(f"📊 Found {len(all_images)} portfolio images in database (excluding About images)")
        
        portfolio_data = []
        
        for image in all_images:
            print(f"📷 Processing image: {image.filename}")
            try:
                # Create portfolio item with error handling for each field
                portfolio_item = {
                    'id': str(image.id) if image.id else 'unknown',
                    'title': image.title if image.title else f"Image {image.id}",
                    'description': image.description if image.description else "",
                    'filename': image.filename if image.filename else "unknown.jpg",
                    'image': image.filename if image.filename else "unknown.jpg",
                    'categories': ['Photography'],  # Simple default
                    'metadata': {
                        'created_at': image.created_at.isoformat() if hasattr(image, 'created_at') and image.created_at else None
                    }
                }
                portfolio_data.append(portfolio_item)
                print(f"✅ Added image: {portfolio_item['filename']}")
            except Exception as img_error:
                print(f"⚠️ Error processing image {image.id}: {img_error}")
                continue
        
        print(f"✅ Returning {len(portfolio_data)} portfolio items")
        return jsonify(portfolio_data)
        
    except Exception as e:
        print(f"❌ Error in simple portfolio: {e}")
        import traceback
        traceback.print_exc()
        
        # Return empty array instead of 500 error
        print("🔄 Returning empty array as fallback")
        return jsonify([]), 200

@app.route('/api/categories')
def get_categories():
    """API endpoint to get all categories"""
    try:
        from src.models import Category
        
        categories = Category.query.all()
        categories_data = []
        
        for category in categories:
            category_item = {
                'id': str(category.id),
                'name': category.name,
                'image_count': len(category.image_categories)
            }
            categories_data.append(category_item)
        
        return jsonify(categories_data)
        
    except Exception as e:
        print(f"Error loading categories from database: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

@app.route('/api/featured-image')
def get_featured_image():
    """API endpoint to get featured image with complete data"""
    try:
        from src.models import SystemConfig, Image
        from PIL import Image as PILImage
        from PIL.ExifTags import TAGS
        import os
        
        # Get featured image from database using is_featured flag
        featured_image = Image.query.filter(Image.is_featured == True).first()
        
        if featured_image:
            # Extract EXIF data from actual image file
            image_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, featured_image.filename)
            exif_data = {}
            
            if os.path.exists(image_path):
                try:
                    with PILImage.open(image_path) as pil_image:
                        exif = pil_image._getexif()
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
                                if tag == 'DateTime':
                                    exif_data['capture_date'] = str(value)
                                elif tag == 'Make':
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
                                        # Handle decimal values like 0.001333333
                                        if isinstance(value, (int, float)) and value < 1:
                                            # Convert decimal to fraction (e.g., 0.00133 -> 1/750)
                                            fraction_denominator = int(round(1 / value))
                                            exif_data['shutter_speed'] = f"1/{fraction_denominator}"
                                        else:
                                            exif_data['shutter_speed'] = f"{value}s"
                                elif tag == 'ISOSpeedRatings':
                                    exif_data['iso'] = f"ISO {value}"
                                elif tag == 'Flash':
                                    flash_fired = value & 1
                                    exif_data['flash'] = "Yes" if flash_fired else "No"
                                    
                except Exception as e:
                    print(f"Error extracting EXIF from {image_path}: {e}")
            
            return jsonify({
                'image': featured_image.filename,
                'title': featured_image.title,
                'description': featured_image.description,
                'story': featured_image.featured_story,
                'filename': featured_image.filename,
                'upload_date': featured_image.upload_date.isoformat() if featured_image.upload_date else None,
                'file_size': featured_image.file_size,
                'width': featured_image.width,
                'height': featured_image.height,
                'exif_data': exif_data
            })
        else:
            # No featured image set
            return jsonify({'error': 'No featured image set'}), 404
        
    except Exception as e:
        print(f"Error loading featured image from database: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load featured image'}), 500

@app.route('/api/all-images')
def get_all_images():
    """API endpoint to list all images in /data directory and database"""
    try:
        from src.models import Image
        import os
        
        # Get all images from database
        db_images = Image.query.all()
        
        # Get all image files from /data directory
        data_dir = '/data'
        file_images = []
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_path = os.path.join(data_dir, filename)
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    file_images.append({
                        'filename': filename,
                        'file_size': file_size,
                        'in_database': any(img.filename == filename for img in db_images)
                    })
        
        # Format database images
        db_image_list = []
        for img in db_images:
            db_image_list.append({
                'id': img.id,
                'filename': img.filename,
                'title': img.title,
                'is_featured': img.is_featured,
                'is_about': img.is_about,
                'file_size': img.file_size,
                'width': img.width,
                'height': img.height,
                'upload_date': img.upload_date.isoformat() if img.upload_date else None
            })
        
        return jsonify({
            'status': 'success',
            'data_directory': data_dir,
            'total_files_in_data': len(file_images),
            'total_images_in_database': len(db_images),
            'files_in_data': file_images,
            'images_in_database': db_image_list
        })
        
    except Exception as e:
        print(f"Error listing images: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/test')
def api_test():
    """Simple test API endpoint without database queries"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'API is working!',
            'test_data': [
                {'id': 1, 'name': 'Test Item 1'},
                {'id': 2, 'name': 'Test Item 2'},
                {'id': 3, 'name': 'Test Item 3'}
            ]
        })
    except Exception as e:
        print(f"Error in test API: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/debug-query')
def debug_query():
    """Debug API to understand database query differences"""
    try:
        from src.models import Image, Category, ImageCategory, db
        
        debug_info = {
            'step1_import_success': True,
            'step2_image_count_query': None,
            'step3_image_count_session': None,
            'step4_first_image': None,
            'step5_categories_count': None,
            'step6_sample_images': []
        }
        
        # Step 2: Try Image.query.count()
        try:
            debug_info['step2_image_count_query'] = Image.query.count()
        except Exception as e:
            debug_info['step2_image_count_query'] = f"Error: {e}"
        
        # Step 3: Try db.session.query(Image).count()
        try:
            debug_info['step3_image_count_session'] = db.session.query(Image).count()
        except Exception as e:
            debug_info['step3_image_count_session'] = f"Error: {e}"
        
        # Step 4: Try to get first image
        try:
            first_image = Image.query.first()
            if first_image:
                debug_info['step4_first_image'] = {
                    'id': str(first_image.id),
                    'filename': first_image.filename,
                    'title': first_image.title
                }
            else:
                debug_info['step4_first_image'] = "No images found"
        except Exception as e:
            debug_info['step4_first_image'] = f"Error: {e}"
        
        # Step 5: Check categories
        try:
            debug_info['step5_categories_count'] = Category.query.count()
        except Exception as e:
            debug_info['step5_categories_count'] = f"Error: {e}"
        
        # Step 6: Try to get sample images
        try:
            sample_images = Image.query.limit(3).all()
            for img in sample_images:
                debug_info['step6_sample_images'].append({
                    'id': str(img.id),
                    'filename': img.filename,
                    'title': img.title
                })
        except Exception as e:
            debug_info['step6_sample_images'] = f"Error: {e}"
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': str(e)}), 500

@app.route('/api/debug-db')
def debug_database():
    """Debug endpoint to test database connection step by step"""
    debug_info = []
    
    try:
        debug_info.append("Step 1: Starting debug")
        
        # Test database connection
        from src.models import db
        debug_info.append("Step 2: Imported db")
        
        # Test Image model import
        from src.models import Image
        debug_info.append("Step 3: Imported Image model")
        
        # Test basic query
        image_count = Image.query.count()
        debug_info.append(f"Step 4: Image count = {image_count}")
        
        # Test getting first image
        first_image = Image.query.first()
        if first_image:
            debug_info.append(f"Step 5: First image = {first_image.filename}")
        else:
            debug_info.append("Step 5: No images found")
        
        # Test getting all images
        all_images = Image.query.all()
        debug_info.append(f"Step 6: Total images retrieved = {len(all_images)}")
        
        if all_images:
            debug_info.append(f"Step 7: Sample filenames = {[img.filename for img in all_images[:3]]}")
        
        return jsonify({
            'status': 'success',
            'debug_steps': debug_info,
            'image_count': image_count
        })
        
    except Exception as e:
        debug_info.append(f"ERROR: {str(e)}")
        import traceback
        debug_info.append(f"TRACEBACK: {traceback.format_exc()}")
        
        return jsonify({
            'status': 'error',
            'debug_steps': debug_info,
            'error': str(e)
        }), 500

@app.route('/api/portfolio-new')
def get_portfolio_new():
    """BRAND NEW portfolio endpoint - exact copy of working debug code"""
    try:
        # EXACT SAME CODE AS WORKING DEBUG ENDPOINT
        from src.models import Image
        
        # Test getting all images - EXACT SAME AS DEBUG (excluding About images)
        all_images = Image.query.filter(Image.is_about != True).all()
        
        portfolio_data = []
        
        for image in all_images:
            try:
                # Get actual categories for this image - SAME AS ADMIN
                image_categories = []
                try:
                    image_categories = [cat.category.name for cat in image.categories]
                except Exception as cat_error:
                    print(f"Category error for image {image.id}: {cat_error}")
                    image_categories = ['Miscellaneous']
                
                # If no categories assigned, use Miscellaneous
                if not image_categories:
                    image_categories = ['Miscellaneous']
                
                # Create portfolio item with React-expected format
                portfolio_item = {
                    'id': str(image.id),
                    'title': image.title or f"Image {image.id}",
                    'description': image.description or "",
                    'filename': image.filename,
                    'url': f"https://minds-eye-master-production.up.railway.app/static/assets/{image.filename}",  # PERSISTENT VOLUME!
                    'categories': image_categories,  # ACTUAL CATEGORIES FROM DATABASE
                    'metadata': {
                        'created_at': image.upload_date.isoformat() if image.upload_date else None
                    }
                }
                portfolio_data.append(portfolio_item)
                
            except Exception as img_error:
                continue
        
        # Create response with CORS headers
        response = jsonify(portfolio_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response
        
    except Exception as e:
        # Return empty array with CORS headers on error
        response = jsonify([])
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response, 500

@app.route('/assets/portfolio-data')
def get_portfolio_data():
    """API endpoint that React frontend actually calls - USING EXACT DEBUG CODE"""
    try:
        # EXACT SAME CODE AS DEBUG ENDPOINT THAT WORKS
        from src.models import Image
        
        # Test getting all images - EXACT SAME AS DEBUG (excluding About images)
        all_images = Image.query.filter(Image.is_about != True).all()
        print(f"PORTFOLIO API: Total portfolio images retrieved = {len(all_images)} (excluding About images)")
        
        portfolio_data = []
        
        for image in all_images:
            try:
                # Get actual categories for this image - SAME AS ADMIN
                image_categories = []
                try:
                    image_categories = [cat.category.name for cat in image.categories]
                except Exception as cat_error:
                    print(f"Category error for image {image.id}: {cat_error}")
                    image_categories = ['Miscellaneous']
                
                # If no categories assigned, use Miscellaneous
                if not image_categories:
                    image_categories = ['Miscellaneous']
                
                # Create portfolio item with React-expected format
                portfolio_item = {
                    'id': str(image.id),
                    'title': image.title or f"Image {image.id}",
                    'description': image.description or "",
                    'filename': image.filename,
                    'url': f"https://minds-eye-master-production.up.railway.app/static/assets/{image.filename}",  # PERSISTENT VOLUME!
                    'categories': image_categories,  # ACTUAL CATEGORIES FROM DATABASE
                    'metadata': {
                        'created_at': image.upload_date.isoformat() if image.upload_date else None
                    }
                }
                portfolio_data.append(portfolio_item)
                print(f"PORTFOLIO API: Added image {image.filename}")
                
            except Exception as img_error:
                print(f"PORTFOLIO API: Error processing image {image.id}: {img_error}")
                continue
        
        print(f"PORTFOLIO API: Returning {len(portfolio_data)} portfolio items")
        
        # Create response with CORS headers
        response = jsonify(portfolio_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response
        
    except Exception as e:
        print(f"PORTFOLIO API ERROR: {e}")
        import traceback
        print(f"PORTFOLIO API TRACEBACK: {traceback.format_exc()}")
        
        # Return empty array with CORS headers on error
        response = jsonify([])
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        return response, 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Only exclude API routes from catch-all, allow assets to be served
    if path.startswith('api/'):
        return "Endpoint not found", 404
    
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


@app.route('/api/background')
def get_current_background_api():
    """API endpoint to get current background image - ONLY FROM DATABASE"""
    try:
        from src.models import Image
        
        # Get the current background image from database
        background_image = Image.query.filter_by(is_background=True).first()
        
        if background_image:
            return jsonify({
                'background_url': f"https://minds-eye-master-production.up.railway.app/static/assets/{background_image.filename}",
                'filename': background_image.filename,
                'title': background_image.title
            })
        else:
            # If no background set, use the first image from database as fallback
            first_image = Image.query.first()
            if first_image:
                return jsonify({
                    'background_url': f"https://minds-eye-master-production.up.railway.app/static/assets/{first_image.filename}",
                    'filename': first_image.filename,
                    'title': first_image.title
                })
            else:
                # No images in database at all
                return jsonify({
                    'background_url': None,
                    'filename': None,
                    'title': 'No images available'
                }), 404
            
    except Exception as e:
        print(f"Error getting background: {e}")
        return jsonify({
            'background_url': None,
            'filename': None,
            'title': 'Error loading background'
        }), 500


# DIAGNOSTIC TEST ROUTE
@app.route('/flask-test-12345')
def flask_diagnostic():
    """Test if Flask is running at all"""
    return "FLASK IS WORKING! If you see this, Flask routes work but /about is being hijacked by React routing."

# SPECIAL ABOUT PAGE HANDLER - Bypasses React entirely
@app.route('/data/<filename>')
def serve_data_file(filename):
    """Serve files from the data directory (persistent storage)"""
    try:
        # In production, images are stored in /data (persistent volume)
        data_dir = '/data' if os.path.exists('/data') else os.path.join(os.path.dirname(__file__), '..', 'data')
        return send_from_directory(data_dir, filename)
    except Exception as e:
        print(f"Error serving data file {filename}: {e}")
        return "File not found", 404



# React Frontend Routes
@app.route('/assets/<path:filename>')
def serve_react_assets(filename):
    """Serve React build assets (CSS, JS, etc.)"""
    static_assets = os.path.join(os.path.dirname(__file__), 'static', 'assets')
    if os.path.exists(os.path.join(static_assets, filename)):
        return send_from_directory(static_assets, filename)
    return f"React asset not found: {filename}", 404

@app.route('/')
def serve_react_root():
    """Serve React frontend for root route"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.exists(os.path.join(static_dir, 'index.html')):
        return send_from_directory(static_dir, 'index.html')
    return "React frontend not found", 404

@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React frontend for all non-API routes (SPA routing)"""
    # CRITICAL FIX: Properly exclude API routes, admin routes, and static assets
    # These should be handled by Flask, not React
    if (path.startswith('api/') or 
        path.startswith('admin/') or 
        path.startswith('static/') or
        path.startswith('flask-test-') or
        path == 'about'):
        # Return 404 to let Flask continue to other route handlers
        from flask import abort
        abort(404)
    
    # Check if it's a specific file request
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if '.' in path and os.path.exists(os.path.join(static_dir, path)):
        return send_from_directory(static_dir, path)
    
    # For all other routes (React SPA routes), serve React index.html
    if os.path.exists(os.path.join(static_dir, 'index.html')):
        return send_from_directory(static_dir, 'index.html')
    return "React frontend not found", 404

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


@app.route("/api/database-inspect")
def database_inspect():
    """Inspect what is actually in the database"""
    try:
        result = {
            "images_table": [],
            "about_images_table": [],
            "image_count": 0,
            "about_image_count": 0,
            "categories_count": 0
        }
        
        # Check categories
        categories = Category.query.all()
        result["categories_count"] = len(categories)
        result["categories"] = [cat.name for cat in categories]
        
        # Check main images table
        images = Image.query.all()
        result["image_count"] = len(images)
        for img in images:
            result["images_table"].append({
                "id": img.id,
                "filename": img.filename,
                "title": img.title,
                "description": img.description
            })
        
        # Check about images table  
        try:
            from src.models import AboutImage
            about_images = AboutImage.query.all()
            result["about_image_count"] = len(about_images)
            for img in about_images:
                result["about_images_table"].append({
                    "id": img.id,
                    "filename": img.filename,
                    "title": img.title,
                    "description": img.description
                })
        except:
            result["about_images_table"] = ["AboutImage table not found"]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/init-database")
def init_database():
    """Manually initialize database with default categories"""
    try:
        # Force initialize categories
        init_default_categories()
        
        # Force initialize system config
        init_system_config()
        
        return jsonify({
            "success": True,
            "message": "Database initialized successfully",
            "categories_count": Category.query.count()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test-upload-path")
def test_upload_path():
    """Test if upload path is accessible"""
    try:
        import os
        from src.config import PHOTOGRAPHY_ASSETS_DIR
        
        result = {
            "photography_assets_dir": PHOTOGRAPHY_ASSETS_DIR,
            "path_exists": os.path.exists(PHOTOGRAPHY_ASSETS_DIR),
            "is_writable": False,
            "can_create_dir": False
        }
        
        # Test if we can create the directory
        try:
            os.makedirs(PHOTOGRAPHY_ASSETS_DIR, exist_ok=True)
            result["can_create_dir"] = True
        except Exception as e:
            result["create_dir_error"] = str(e)
        
        # Test if we can write to it
        try:
            test_file = os.path.join(PHOTOGRAPHY_ASSETS_DIR, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            result["is_writable"] = True
        except Exception as e:
            result["write_error"] = str(e)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test-minimal-upload", methods=['POST'])
def test_minimal_upload():
    """Minimal upload test to isolate the issue"""
    try:
        import os
        import uuid
        from werkzeug.utils import secure_filename
        from src.config import PHOTOGRAPHY_ASSETS_DIR
        from src.models import db, Image, Category
        from datetime import datetime
        
        # Get a test file
        image_files = request.files.getlist('image')
        if not image_files or not image_files[0].filename:
            return jsonify({"error": "No file provided"}), 400
        
        image_file = image_files[0]
        
        # Generate filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"test-{unique_id}.jpg"
        
        # Save file
        os.makedirs(PHOTOGRAPHY_ASSETS_DIR, exist_ok=True)
        final_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, filename)
        image_file.save(final_path)
        
        # Get file size
        file_size = os.path.getsize(final_path)
        
        # Create database entry
        new_image = Image(
            filename=filename,
            title="Test Image",
            description="Test upload",
            file_size=file_size,
            width=None,
            height=None,
            upload_date=datetime.now()
        )
        
        db.session.add(new_image)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "filename": filename,
            "file_size": file_size,
            "image_id": new_image.id
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_details
        }), 500

