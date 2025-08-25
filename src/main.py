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
from src.routes.about_management import about_mgmt_bp
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
app.register_blueprint(about_mgmt_bp)
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
    
    # Only migrate images if no images exist in database
    if Image.query.count() == 0:
        print("🔄 No images in database - running migration...")
        migrate_existing_images()
    else:
        print(f"✅ Database has {Image.query.count()} images - skipping migration")
    
    print("✅ SQL Database initialization complete")

@app.route('/assets/about/<filename>')
def serve_about_image(filename):
    """Serve about images from the about directory"""
    about_dir = os.path.join(PHOTOGRAPHY_ASSETS_DIR, 'about')
    return send_from_directory(about_dir, filename)

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

@app.route('/test-portfolio')
def test_portfolio():
    """Test portfolio page to debug image display"""
    return send_from_directory('static', 'test-portfolio.html')

@app.route('/api/simple-portfolio')
def get_simple_portfolio():
    """Simple portfolio endpoint using same pattern as working debug endpoint"""
    try:
        print("🔍 Simple Portfolio API called")
        from src.models import Image
        
        # Get all images - same as debug endpoint
        all_images = Image.query.all()
        print(f"📊 Found {len(all_images)} images in database")
        
        portfolio_data = []
        
        for image in all_images:
            print(f"📷 Processing image: {image.filename}")
            # Simple portfolio item without complex relationships
            portfolio_item = {
                'id': str(image.id),
                'title': image.title or f"Image {image.id}",
                'description': image.description or "",
                'filename': image.filename,
                'image': image.filename,  # Frontend expects 'image' field
                'categories': ['Photography'],  # Simple default category
                'metadata': {
                    'created_at': image.created_at.isoformat() if image.created_at else None
                }
            }
            portfolio_data.append(portfolio_item)
        
        print(f"✅ Returning {len(portfolio_data)} portfolio items")
        return jsonify(portfolio_data)
        
    except Exception as e:
        print(f"❌ Error in simple portfolio: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

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
    """API endpoint to get featured image"""
    try:
        from src.models import SystemConfig, Image
        
        # Get featured image from system config
        featured_config = SystemConfig.query.filter_by(key='featured_image').first()
        if featured_config:
            return jsonify({'image': featured_config.value})
        else:
            # Return first image as default
            first_image = Image.query.first()
            if first_image:
                return jsonify({'image': first_image.filename})
            else:
                return jsonify({'image': None})
        
    except Exception as e:
        print(f"Error loading featured image from database: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'image': None}), 500

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
        
        # Test getting all images - EXACT SAME AS DEBUG
        all_images = Image.query.all()
        
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
        
        # Test getting all images - EXACT SAME AS DEBUG
        all_images = Image.query.all()
        print(f"PORTFOLIO API: Total images retrieved = {len(all_images)}")
        
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


# Flask About Page with Floating Layout (bypassing React cache issues)
@app.route('/api/about-floating-page')
def about_floating():
    """Serve Flask-based About page with floating image layout"""
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Mind's Eye Photography</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .floating-image {
            float: left;
            margin-right: 2rem;
            margin-bottom: 1.5rem;
            width: 320px;
        }
        @media (min-width: 1024px) {
            .floating-image {
                width: 384px;
            }
        }
        .clear-float {
            clear: both;
        }
        body {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: #e2e8f0;
            font-family: system-ui, -apple-system, sans-serif;
        }
    </style>
</head>
<body class="min-h-screen">
    <!-- Navigation -->
    <nav class="bg-slate-900 shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <a href="/" class="text-orange-400 text-xl font-bold">Mind's Eye Photography</a>
                <div class="flex space-x-6">
                    <a href="/" class="text-slate-300 hover:text-orange-400">Home</a>
                    <a href="/portfolio" class="text-slate-300 hover:text-orange-400">Portfolio</a>
                    <a href="/featured" class="text-slate-300 hover:text-orange-400">Featured</a>
                    <a href="/about" class="text-orange-400">About</a>
                    <a href="/contact" class="text-slate-300 hover:text-orange-400">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900">
        <!-- Header -->
        <div class="text-center py-16">
            <h1 class="text-4xl lg:text-5xl font-light text-orange-400 mb-4">
                About Mind's Eye Photography
            </h1>
            <p class="text-xl text-slate-300">
                Where Moments Meet Imagination
            </p>
        </div>

        <!-- Content with Floating Image -->
        <div class="max-w-4xl mx-auto px-6 py-16">
            <div class="prose prose-lg prose-invert max-w-none">
                <div class="text-slate-300 leading-relaxed text-lg">
                    
                    <!-- Floating Behind the Lens Image -->
                    <div class="floating-image">
                        <div class="bg-slate-800 rounded-lg overflow-hidden shadow-2xl" style="aspect-ratio: 3/2;">
                            <div class="w-full h-full bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center">
                                <p class="text-white text-center font-semibold">Behind the Lens Image<br/>Will appear here once uploaded</p>
                            </div>
                        </div>
                        <p class="text-center text-orange-400 text-sm mt-3 font-light">
                            Behind the Lens
                        </p>
                    </div>
                    
                    <!-- Text content that wraps around the floating image -->
                    <div>
                        <p class="mb-6">
                            Born and raised right here in Madison, Wisconsin, I'm a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a <strong>musician/songwriter</strong>, a <strong>Teacher</strong>, a <strong>REALTOR</strong>, and a <strong>Small Business Owner</strong>. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.
                        </p>
                        
                        <p class="mb-6">
                            At the heart of Mind's Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.
                        </p>
                        
                        <p class="mb-6">
                            For me, client satisfaction isn't just a goal – it's the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It's truly rewarding to see clients transform into lifelong friends, and that's the kind of connection I strive to build with everyone I work with.
                        </p>
                        
                        <p class="font-semibold text-lg">
                            Rick Corey
                        </p>
                    </div>
                    
                    <!-- Clear float -->
                    <div class="clear-float"></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''
    return html_content

# DIAGNOSTIC TEST ROUTE
@app.route('/flask-test-12345')
def flask_diagnostic():
    """Test if Flask is running at all"""
    return "FLASK IS WORKING! If you see this, Flask routes work but /about is being hijacked by React routing."

# SPECIAL ABOUT PAGE HANDLER - Bypasses React entirely
@app.route('/about')
def about_page_override():
    """Serve floating layout About page directly from Flask - BYPASSES REACT CACHE"""
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Mind's Eye Photography</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .floating-image {
            float: left;
            margin-right: 2rem;
            margin-bottom: 1.5rem;
            width: 320px;
        }
        @media (min-width: 1024px) {
            .floating-image {
                width: 384px;
            }
        }
        .clear-float {
            clear: both;
        }
        body {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: #e2e8f0;
            font-family: system-ui, -apple-system, sans-serif;
        }
    </style>
</head>
<body class="min-h-screen">
    <!-- Navigation -->
    <nav class="bg-slate-900 shadow-lg">
        <div class="max-w-7xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <a href="/" class="text-orange-400 text-xl font-bold">Mind's Eye Photography</a>
                <div class="flex space-x-6">
                    <a href="/" class="text-slate-300 hover:text-orange-400">Home</a>
                    <a href="/portfolio" class="text-slate-300 hover:text-orange-400">Portfolio</a>
                    <a href="/featured" class="text-slate-300 hover:text-orange-400">Featured</a>
                    <a href="/about" class="text-orange-400">About</a>
                    <a href="/contact" class="text-slate-300 hover:text-orange-400">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="min-h-screen bg-gradient-to-br from-slate-800 to-slate-900">
        <!-- Header -->
        <div class="text-center py-16">
            <h1 class="text-4xl lg:text-5xl font-light text-orange-400 mb-4">
                About Mind's Eye Photography
            </h1>
            <p class="text-xl text-slate-300">
                Where Moments Meet Imagination
            </p>
        </div>

        <!-- FLOATING IMAGE LAYOUT - EXACTLY LIKE REFERENCE -->
        <div class="max-w-4xl mx-auto px-6 py-16">
            <div class="text-slate-300 leading-relaxed text-lg">
                
                <!-- Floating Behind the Lens Image -->
                <div class="floating-image">
                    <div class="bg-slate-800 rounded-lg overflow-hidden shadow-2xl" style="aspect-ratio: 3/2;">
                        <div class="w-full h-full bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center">
                            <p class="text-white text-center font-semibold">Behind the Lens Image<br/>Will appear here once uploaded</p>
                        </div>
                    </div>
                    <p class="text-center text-orange-400 text-sm mt-3 font-light">
                        Behind the Lens
                    </p>
                </div>
                
                <!-- Text content that wraps around the floating image -->
                <div>
                    <p class="mb-6">
                        Born and raised right here in Madison, Wisconsin, I'm a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a <strong>musician/songwriter</strong>, a <strong>Teacher</strong>, a <strong>REALTOR</strong>, and a <strong>Small Business Owner</strong>. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.
                    </p>
                    
                    <p class="mb-6">
                        At the heart of Mind's Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.
                    </p>
                    
                    <p class="mb-6">
                        For me, client satisfaction isn't just a goal – it's the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It's truly rewarding to see clients transform into lifelong friends, and that's the kind of connection I strive to build with everyone I work with.
                    </p>
                    
                    <p class="font-semibold text-lg">
                        Rick Corey
                    </p>
                </div>
                
                <!-- Clear float -->
                <div class="clear-float"></div>
            </div>
        </div>
    </div>
</body>
</html>
    '''
    return html_content

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

