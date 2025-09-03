import os
import json
import uuid
import os
from datetime import datetime
from flask import Blueprint, request, render_template_string, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from ..config import PHOTOGRAPHY_ASSETS_DIR, PORTFOLIO_DATA_FILE, CATEGORIES_CONFIG_FILE, get_image_url

admin_bp = Blueprint('admin', __name__)

# Admin password
ADMIN_PASSWORD = "mindseye2025"

def load_categories_config():
    """Load categories configuration"""
    try:
        if os.path.exists(CATEGORIES_CONFIG_FILE):
            with open(CATEGORIES_CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading categories config: {e}")
    
    # Default configuration
    return {
        'categories': ['Wildlife', 'Landscapes', 'Portraits', 'Events', 'Nature', 'Miscellaneous'],
        'default_category': 'All',
        'category_order': ['Wildlife', 'Landscapes', 'Portraits', 'Events', 'Nature', 'Miscellaneous']
    }

def load_portfolio_data():
    """Load portfolio data from JSON file"""
    try:
        if os.path.exists(PORTFOLIO_DATA_FILE):
            with open(PORTFOLIO_DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading portfolio data: {e}")
    return []

def save_portfolio_data(data):
    """Save portfolio data to both JSON files for frontend compatibility"""
    try:
        # Ensure directories exist
        os.makedirs(os.path.dirname(PORTFOLIO_DATA_FILE), exist_ok=True)
        
        # Save to multicategory file (admin uses this)
        with open(PORTFOLIO_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Admin saved portfolio data to multicategory file: {PORTFOLIO_DATA_FILE}")
        
        # Also save to regular portfolio-data.json (frontend uses this)
        regular_portfolio_file = os.path.join(os.path.dirname(PORTFOLIO_DATA_FILE), 'portfolio-data.json')
        with open(regular_portfolio_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Admin saved portfolio data to regular file: {regular_portfolio_file}")
        
        return True
    except Exception as e:
        print(f"❌ Admin error saving portfolio data: {e}")
        return False

@admin_bp.route('/admin')
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_dashboard'))
    
    login_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #000; 
                color: #fff; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
            }
            .login-container { 
                background: #222; 
                padding: 30px; 
                border-radius: 10px; 
                text-align: center; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            }
            h1 { color: #ff6b35; margin-bottom: 10px; }
            h2 { margin-bottom: 20px; }
            input { 
                width: 200px; 
                padding: 10px; 
                margin: 10px 0; 
                border: 1px solid #555; 
                border-radius: 5px; 
                background: #333; 
                color: #fff; 
            }
            button { 
                width: 220px; 
                padding: 10px; 
                background: #ff6b35; 
                color: #fff; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 16px;
            }
            .error { color: #ff4444; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>Mind's Eye Photography</h1>
            <h2>Admin Login</h2>
            <form method="POST" action="/admin/login">
                <div>
                    <input type="password" name="password" placeholder="Enter password" required>
                </div>
                <div>
                    <button type="submit">Login</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    '''
    
    return login_html

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Handle admin login"""
    password = request.form.get('password')
    if password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin.admin_dashboard'))
    else:
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin/logout')
def admin_logout():
    """Handle admin logout"""
    session.pop('admin_logged_in', None)
    return redirect('/')  # Redirect to main site

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Load data from SQL database instead of JSON files
    from ..models import Image, Category
    
    # Get all images from database - sorted by upload_date newest to oldest
    images = Image.query.order_by(Image.upload_date.desc()).all()
    portfolio_data = []
    
    for image in images:
        # Get categories for this image
        image_categories = [cat.category.name for cat in image.categories]
        
        portfolio_data.append({
            'id': image.id,
            'filename': image.filename,
            'title': image.title,
            'description': image.description,
            'categories': image_categories,
            'upload_date': image.upload_date.isoformat() if image.upload_date else None,
            'file_size': image.file_size,
            'width': image.width,
            'height': image.height,
            'is_slideshow_background': getattr(image, 'is_slideshow_background', False)
        })
    
    # Get categories from database
    categories = Category.query.all()
    available_categories = [cat.name for cat in categories]
    
    return render_template_string(dashboard_html, 
                                portfolio_data=portfolio_data,
                                available_categories=available_categories,
                                message=request.args.get('message'),
                                message_type=request.args.get('message_type', 'success'))

@admin_bp.route('/admin/upload', methods=['POST'])
def admin_upload():
    """Handle image upload (single or multiple) - SAVE TO SQL DATABASE"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        categories = request.form.getlist('categories')
        image_files = request.files.getlist('image')
        
        # Import database models
        from ..models import db, Image, Category, ImageCategory
        
        # Validation
        if not title:
            return redirect(url_for('admin.admin_dashboard') + '?message=Please enter an image title&message_type=error')
        
        # Description is now optional - no validation needed
        
        if not categories:
            return redirect(url_for('admin.admin_dashboard') + '?message=Please select at least one category&message_type=error')
        
        if not image_files or not any(f.filename for f in image_files):
            return redirect(url_for('admin.admin_dashboard') + '?message=Please select at least one image file&message_type=error')
        
        uploaded_count = 0
        
        # Process each image file
        for image_file in image_files:
            if image_file and image_file.filename:
                # Generate filename
                unique_id = str(uuid.uuid4())[:8]
                safe_title = secure_filename(title.lower().replace(' ', '-'))
                if uploaded_count > 0:
                    safe_title = f"{safe_title}-{uploaded_count + 1}"
                
                file_extension = os.path.splitext(image_file.filename)[1].lower()
                if not file_extension:
                    file_extension = '.jpg'
                
                filename = f"{safe_title}-{unique_id}{file_extension}"
                
                # Save file to photography assets directory
                os.makedirs(PHOTOGRAPHY_ASSETS_DIR, exist_ok=True)
                final_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, filename)
                image_file.save(final_path)
                
                # Get file size and dimensions
                file_size = os.path.getsize(final_path)
                # PIL temporarily disabled - set dimensions to None
                width, height = None, None
                
                # Create new image in database
                final_title = f"{title} {uploaded_count + 1}" if len([f for f in image_files if f.filename]) > 1 else title
                new_image = Image(
                    filename=filename,
                    title=final_title,
                    description=description,
                    file_size=file_size,
                    width=width,
                    height=height,
                    upload_date=datetime.now()
                )
                
                # Add to database
                db.session.add(new_image)
                db.session.flush()  # Get the ID
                
                # Add category associations
                for category_name in categories:
                    category = Category.query.filter_by(name=category_name).first()
                    if category:
                        image_category = ImageCategory(image_id=new_image.id, category_id=category.id)
                        db.session.add(image_category)
                
                uploaded_count += 1
        
        # Commit all changes
        db.session.commit()
        
        # Redirect with success message
        message = f"{uploaded_count} image(s) uploaded successfully!" if uploaded_count > 1 else "Image uploaded successfully!"
        return redirect(url_for('admin.admin_dashboard') + f'?message={message}&message_type=success')
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {e}")
        print(f"Full traceback: {error_details}")
        return redirect(url_for('admin.admin_dashboard') + f'?message=Upload failed: {str(e)}&message_type=error')

@admin_bp.route('/admin/bulk-delete', methods=['POST'])
def bulk_delete():
    """Handle bulk deletion of multiple images"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin.admin_login'))
    
    try:
        from ..models import Image, ImageCategory, db
        
        # Get list of image IDs to delete
        image_ids = request.form.getlist('image_ids')
        
        if not image_ids:
            return redirect(url_for('admin.admin_dashboard') + '?message=No images selected for deletion&message_type=error')
        
        deleted_count = 0
        
        # Delete each image from database and filesystem
        for image_id in image_ids:
            image = Image.query.get(image_id)
            if image:
                # Delete image file from filesystem
                image_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, image.filename)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        print(f"✅ Deleted image file: {image_path}")
                    except Exception as e:
                        print(f"❌ Error deleting image file {image_path}: {e}")
                
                # Delete image categories relationships
                ImageCategory.query.filter_by(image_id=image_id).delete()
                
                # Delete image from database
                db.session.delete(image)
                deleted_count += 1
        
        # Commit all changes
        db.session.commit()
        
        return redirect(url_for('admin.admin_dashboard') + f'?message={deleted_count} image(s) deleted successfully!&message_type=success')
        
    except Exception as e:
        print(f"Bulk delete error: {e}")
        flash(f'Error deleting images: {str(e)}', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/bulk-update-categories', methods=['POST'])
def bulk_update_categories():
    """Handle bulk category updates for multiple images"""
    if 'admin_logged_in' not in session:
        return {'success': False, 'message': 'Not authenticated'}, 401
    
    try:
        from ..models import Image, Category, ImageCategory, db
        
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        categories = data.get('categories', [])
        
        if not image_ids:
            return {'success': False, 'message': 'No images selected'}
        
        if not categories:
            return {'success': False, 'message': 'No categories selected'}
        
        # Get category objects from database
        category_objects = Category.query.filter(Category.name.in_(categories)).all()
        if len(category_objects) != len(categories):
            return {'success': False, 'message': 'Some categories not found'}
        
        # Update categories for selected images
        updated_count = 0
        for image_id in image_ids:
            image = Image.query.get(image_id)
            if image:
                # Clear existing categories for this image
                ImageCategory.query.filter_by(image_id=image_id).delete()
                
                # Add new categories
                for category in category_objects:
                    image_category = ImageCategory(image_id=image_id, category_id=category.id)
                    db.session.add(image_category)
                
                updated_count += 1
        
        # Commit all changes
        db.session.commit()
        
        return {
            'success': True, 
            'message': f'Updated {updated_count} image(s) with {len(categories)} categories'
        }
        
    except Exception as e:
        db.session.rollback()
        print(f"Bulk update error: {e}")
        return {'success': False, 'message': f'Update failed: {str(e)}'}, 500

@admin_bp.route('/admin/delete', methods=['POST'])
def admin_delete():
    """Delete individual image"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        from ..models import Image, ImageCategory, db
        
        image_id = request.form.get('image_id')
        if not image_id:
            return redirect(url_for('admin.admin_dashboard') + '?message=No image ID provided&message_type=error')
        
        # Find the image in the database
        image = Image.query.get(image_id)
        if not image:
            return redirect(url_for('admin.admin_dashboard') + '?message=Image not found&message_type=error')
        
        # Delete the image file from photography assets directory
        image_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, image.filename)
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Delete associated category relationships
        ImageCategory.query.filter_by(image_id=image_id).delete()
        
        # Delete the image record from database
        db.session.delete(image)
        db.session.commit()
        
        return redirect(url_for('admin.admin_dashboard') + '?message=Image deleted successfully!&message_type=success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete error: {e}")
        return redirect(url_for('admin.admin_dashboard') + f'?message=Delete failed: {str(e)}&message_type=error')

@admin_bp.route('/admin/edit-image', methods=['POST'])
def edit_image():
    """Edit individual image title and description"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        from ..models import Image, db
        
        image_id = request.form.get('image_id')
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not image_id:
            return redirect(url_for('admin.admin_dashboard') + '?message=No image ID provided&message_type=error')
        
        # Find the image in the database
        image = Image.query.get(image_id)
        if not image:
            return redirect(url_for('admin.admin_dashboard') + '?message=Image not found&message_type=error')
        
        # Update the image details
        if title:  # Only update title if provided
            image.title = title
        image.description = description  # Always update description (allow blank)
        
        db.session.commit()
        
        return redirect(url_for('admin.admin_dashboard') + '?message=Image updated successfully!&message_type=success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Edit error: {e}")
        return redirect(url_for('admin.admin_dashboard') + f'?message=Update failed: {str(e)}&message_type=error')

@admin_bp.route('/admin/slideshow-toggle', methods=['POST'])
def slideshow_toggle():
    """Toggle slideshow background status for an image"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        from ..models import db, Image
        
        data = request.get_json()
        image_id = data.get('image_id')
        is_slideshow = data.get('is_slideshow', False)
        
        # Find the image
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'success': False, 'message': 'Image not found'}), 404
        
        # Check slideshow limit (max 5 images)
        if is_slideshow:
            current_slideshow_count = Image.query.filter_by(is_slideshow_background=True).count()
            if current_slideshow_count >= 5:
                return jsonify({'success': False, 'message': 'Maximum 5 images allowed in slideshow'}), 400
        
        # Update the image
        image.is_slideshow_background = is_slideshow
        db.session.commit()
        
        action = "added to" if is_slideshow else "removed from"
        return jsonify({'success': True, 'message': f'Image {action} slideshow successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Slideshow toggle error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Dashboard HTML template with dynamic categories and multi-image upload
dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
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
            border-bottom: 2px solid #333; 
        }
        h1 { color: #ff6b35; margin: 0; }
        .logout-btn { 
            background: #ff4444; 
            color: #fff; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
        }
        .form-container { 
            background: #222; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
        }
        .form-group { margin-bottom: 15px; }
        .form-group label { 
            display: block; 
            margin-bottom: 5px; 
            color: #ff6b35; 
            font-weight: bold; 
        }
        .form-group input, .form-group textarea { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #555; 
            border-radius: 4px; 
            background: #333; 
            color: #fff; 
            box-sizing: border-box;
        }
        .checkbox-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 5px;
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #fff;
            cursor: pointer;
            padding: 8px;
            background: #333;
            border-radius: 4px;
            border: 1px solid #555;
        }
        .checkbox-label:hover {
            background: #444;
        }
        .checkbox-label input[type="checkbox"] {
            width: auto;
            margin: 0;
        }
        button { 
            background: #ff6b35; 
            color: #fff; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .portfolio-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-top: 20px; 
        }
        .portfolio-item { 
            background: #222; 
            border-radius: 10px; 
            overflow: hidden; 
            position: relative;
        }
        .portfolio-item img { 
            width: 100%; 
            height: 200px; 
            object-fit: cover; 
        }
        .portfolio-info { padding: 15px; }
        .portfolio-info h3 { 
            margin: 0 0 10px 0; 
            color: #ff6b35; 
        }
        .portfolio-checkbox {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 20px;
            height: 20px;
            z-index: 10;
        }
        .bulk-controls {
            background: #333;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .bulk-selection {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .bulk-category-section {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .bulk-category-checkboxes {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .bulk-category-label {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #fff;
            cursor: pointer;
            padding: 8px 12px;
            background: #444;
            border-radius: 4px;
            border: 1px solid #555;
        }
        .bulk-category-label:hover {
            background: #555;
        }
        .bulk-category-label input[type="checkbox"] {
            width: auto;
            margin: 0;
        }
        .bulk-actions {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .bulk-controls button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        .select-all-btn { background: #4CAF50; color: white; }
        .select-none-btn { background: #757575; color: white; }
        .bulk-update-btn { background: #ff6b35; color: white; }
        .bulk-delete-btn { background: #f44336; color: white; }
        .backup-quick-btn { 
            background: #4CAF50; 
            color: white; 
            padding: 10px 15px; 
            text-decoration: none; 
            border-radius: 5px; 
            margin-left: 10px; 
            display: inline-block;
        }
        .backup-quick-btn:hover { background: #45a049; }
        .bulk-update-btn:disabled, .bulk-delete-btn:disabled { 
            background: #666; 
            cursor: not-allowed; 
        }
        .selected-count { 
            color: #ff6b35; 
            font-weight: bold; 
            font-size: 16px;
        }
        .delete-btn { 
            background: #ff4444; 
            color: #fff; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        .edit-btn { 
            background: #4CAF50; 
            color: #fff; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        .edit-btn:hover { 
            background: #45a049; 
        }
        .slideshow-btn {
            background: #666;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .slideshow-btn:hover {
            background: #777;
        }
        .slideshow-btn.active {
            background: #ff6b35;
            color: #fff;
        }
        .slideshow-btn.active:hover {
            background: #e55a2b;
        }
        .about-btn {
            background: #666;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .about-btn:hover {
            background: #777;
        }
        .about-btn.active {
            background: #ff6b35;
            color: #fff;
        }
        .about-btn.active:hover {
            background: #e55a2b;
        }
        .message { 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        .success-message { 
            background: #2d5a2d; 
            color: #90ee90; 
        }
        .error-message { 
            background: #5a2d2d; 
            color: #ff9090; 
        }
        .admin-links {
            margin-bottom: 20px;
        }
        .admin-links a {
            display: inline-block;
            background: #444;
            color: #fff;
            padding: 10px 15px;
            text-decoration: none;
            border-radius: 5px;
            margin-right: 10px;
        }
        .multi-upload-info {
            background: #1a4d1a;
            color: #90ee90;
            padding: 10px;
            border-radius: 4px;
            margin-top: 5px;
            font-size: 14px;
        }
        .category-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
            margin-bottom: 8px;
        }
        .category-badge {
            background: #ff6b35;
            color: #fff;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Mind's Eye Photography - Admin</h1>
        <a href="/admin/logout" class="logout-btn">Logout</a>
    </div>
    
    <div class="admin-links">
        <a href="/admin">🖼️ Portfolio Management</a>
        <a href="/admin/featured-image">⭐ Featured Image</a>
        <a href="/admin/about-management">📖 About Page Management</a>
        <a href="/admin/category-management">🏷️ Category Management</a>
        <a href="/admin/backup-system">🛡️ Backup System</a>
    </div>
    
    {% if message %}
    <div class="message {{ message_type }}-message">
        {{ message }}
    </div>
    {% endif %}
    
    <div class="form-container">
        <h2>Manage Your Portfolio</h2>
        <form method="POST" action="/admin/upload" enctype="multipart/form-data">
            <div class="form-group">
                <label for="image">Image Files (JPG/PNG) - Select Multiple</label>
                <input type="file" id="image" name="image" accept="image/*" multiple required>
                <div class="multi-upload-info">
                    ✨ <strong>Multi-Upload:</strong> Hold Ctrl (Windows) or Cmd (Mac) to select multiple images at once!
                </div>
                <small style="color: #999;">Please add watermark before upload: "© 2025 Mind's Eye Photography"</small>
            </div>
            
            <div class="form-group">
                <label for="title">Base Title</label>
                <input type="text" id="title" name="title" placeholder="e.g., Sunset Over Lake" required>
                <small style="color: #999;">For multiple images, numbers will be added automatically (e.g., "Sunset Over Lake 1", "Sunset Over Lake 2")</small>
            </div>
            
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" rows="3" placeholder="Brief description (applies to all uploaded images - optional)"></textarea>
            </div>
            
            <div class="form-group">
                <label for="categories">Categories (Select multiple)</label>
                <div class="checkbox-group">
                    {% for category in available_categories %}
                    <label class="checkbox-label">
                        <input type="checkbox" name="categories" value="{{ category }}"> {{ category }}
                    </label>
                    {% endfor %}
                </div>
                <small style="color: #999;">All uploaded images will be assigned to the selected categories</small>
            </div>
            
            <button type="submit">Upload Image(s)</button>
        </form>
    </div>
    
    <div>
        <h2>Current Portfolio ({{ portfolio_data|length }} images)</h2>
        
        <!-- Unified Bulk Operations -->
        <div class="bulk-controls">
            <div class="bulk-selection">
                <button type="button" class="select-all-btn" onclick="selectAll()">Select All</button>
                <button type="button" class="select-none-btn" onclick="selectNone()">Select None</button>
                <span class="selected-count">Selected: <span id="selectedCount">0</span></span>
            </div>
            
            <div class="bulk-category-section">
                <span style="color: #ccc; font-size: 14px;">Set categories for selected images:</span>
                <div class="bulk-category-checkboxes">
                    {% for category in available_categories %}
                    <label class="bulk-category-label">
                        <input type="checkbox" name="bulk_categories" value="{{ category }}" id="bulk_{{ category }}">
                        {{ category }}
                    </label>
                    {% endfor %}
                </div>
                <button type="button" class="bulk-update-btn" id="bulkUpdateBtn" onclick="bulkUpdateCategories()" disabled>
                    Update Categories
                </button>
            </div>
            
            <div class="bulk-actions">
                <button type="button" class="bulk-delete-btn" id="bulkDeleteBtn" onclick="bulkDelete()" disabled>
                    Delete Selected
                </button>
                <a href="/admin/backup-system" class="backup-quick-btn">🛡️ Backup System</a>
            </div>
        </div>
        
        <div class="portfolio-grid">
            {% for item in portfolio_data %}
            <div class="portfolio-item">
                <input type="checkbox" class="portfolio-checkbox" name="selected_images" value="{{ item.id }}" onchange="updateSelectedCount()">
                <img src="/static/assets/{{ item.filename }}" alt="{{ item.title }}">
                <div class="portfolio-info">
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.description }}</p>
                    <div class="category-badges">
                        {% for category in item.categories %}
                        <span class="category-badge">{{ category }}</span>
                        {% endfor %}
                    </div>
                    <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap;">
                        <button type="button" class="edit-btn" onclick="openEditModal('{{ item.id }}', '{{ item.title|replace("'", "\\'") }}', '{{ item.description|replace("'", "\\'") }}')">Edit</button>
                        <button type="button" class="slideshow-btn {{ 'active' if item.is_slideshow_background else '' }}" onclick="toggleSlideshow('{{ item.id }}', {{ 'true' if item.is_slideshow_background else 'false' }})">
                            {{ '★ In Slideshow' if item.is_slideshow_background else '☆ Add to Slideshow' }}
                        </button>
                        <form method="POST" action="/admin/delete" style="display: inline;">
                            <input type="hidden" name="image_id" value="{{ item.id }}">
                            <button type="submit" class="delete-btn" onclick="return confirm('Delete this image?')">Delete</button>
                        </form>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Edit Modal -->
    <div id="editModal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);">
        <div style="background-color: #2a2a2a; margin: 10% auto; padding: 20px; border-radius: 8px; width: 500px; max-width: 90%;">
            <h3 style="color: #ff6b35; margin-top: 0;">Edit Image Details</h3>
            <form id="editForm" method="POST" action="/admin/edit-image">
                <input type="hidden" id="editImageId" name="image_id">
                
                <div style="margin-bottom: 15px;">
                    <label for="editTitle" style="display: block; color: #fff; margin-bottom: 5px;">Title:</label>
                    <input type="text" id="editTitle" name="title" style="width: 100%; padding: 8px; border: 1px solid #555; background: #333; color: #fff; border-radius: 4px;">
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label for="editDescription" style="display: block; color: #fff; margin-bottom: 5px;">Description:</label>
                    <textarea id="editDescription" name="description" rows="4" style="width: 100%; padding: 8px; border: 1px solid #555; background: #333; color: #fff; border-radius: 4px; resize: vertical;"></textarea>
                </div>
                
                <div style="text-align: right;">
                    <button type="button" onclick="closeEditModal()" style="background: #666; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px; cursor: pointer;">Cancel</button>
                    <button type="submit" style="background: #4CAF50; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Save Changes</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function selectAll() {
            const checkboxes = document.querySelectorAll('.portfolio-checkbox');
            checkboxes.forEach(cb => cb.checked = true);
            updateSelectedCount();
        }
        
        function selectNone() {
            const checkboxes = document.querySelectorAll('.portfolio-checkbox');
            checkboxes.forEach(cb => cb.checked = false);
            updateSelectedCount();
        }
        
        function updateSelectedCount() {
            const checkboxes = document.querySelectorAll('.portfolio-checkbox:checked');
            const count = checkboxes.length;
            document.getElementById('selectedCount').textContent = count;
            document.getElementById('bulkDeleteBtn').disabled = count === 0;
            document.getElementById('bulkUpdateBtn').disabled = count === 0;
        }
        
        function bulkUpdateCategories() {
            const selectedImages = Array.from(document.querySelectorAll('.portfolio-checkbox:checked')).map(cb => cb.value);
            const selectedCategories = Array.from(document.querySelectorAll('input[name="bulk_categories"]:checked')).map(cb => cb.value);
            
            if (selectedImages.length === 0) {
                alert('Please select at least one image');
                return;
            }
            
            if (selectedCategories.length === 0) {
                alert('Please select at least one category');
                return;
            }
            
            const confirmMessage = `Update ${selectedImages.length} image(s) with categories: ${selectedCategories.join(', ')}?`;
            if (!confirm(confirmMessage)) {
                return;
            }
            
            fetch('/admin/bulk-update-categories', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_ids: selectedImages,
                    categories: selectedCategories
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error updating categories: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error updating categories: ' + error);
            });
        }
        
        function bulkDelete() {
            const checkboxes = document.querySelectorAll('.portfolio-checkbox:checked');
            const selectedIds = Array.from(checkboxes).map(cb => cb.value);
            
            if (selectedIds.length === 0) {
                alert('Please select images to delete.');
                return;
            }
            
            const confirmMessage = `Are you sure you want to delete ${selectedIds.length} selected image(s)? This action cannot be undone.`;
            if (!confirm(confirmMessage)) {
                return;
            }
            
            // Create form and submit
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/admin/bulk-delete';
            
            selectedIds.forEach(id => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'image_ids';
                input.value = id;
                form.appendChild(input);
            });
            
            document.body.appendChild(form);
            form.submit();
        }
        
        function openEditModal(imageId, title, description) {
            document.getElementById('editImageId').value = imageId;
            document.getElementById('editTitle').value = title;
            document.getElementById('editDescription').value = description;
            document.getElementById('editModal').style.display = 'block';
        }
        
        function closeEditModal() {
            document.getElementById('editModal').style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('editModal');
            if (event.target == modal) {
                closeEditModal();
            }
        }
        
        // Slideshow toggle functionality
        async function toggleSlideshow(imageId, currentStatus) {
            try {
                const response = await fetch('/admin/slideshow-toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image_id: imageId,
                        is_slideshow: !currentStatus
                    })
                });
                
                // Check if the HTTP response is ok first
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status}, step: ${errorData.step || 'unknown'}, error: ${errorData.error || 'Unknown error'}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`Success: ${result.message} (Step: ${result.step})`);
                    // Reload the page to update the button states
                    location.reload();
                } else {
                    alert(`Error: ${result.error} (Step: ${result.step || 'unknown'})`);
                }
            } catch (error) {
                console.error('Error toggling slideshow:', error);
                alert('Error updating slideshow status: ' + error.message);
            }
        }
        
        // About toggle functionality
        async function toggleAbout(imageId, currentStatus) {
            try {
                const response = await fetch('/admin/about-toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image_id: imageId,
                        is_about: !currentStatus
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status}, error: ${errorData.error || 'Unknown error'}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`Success: ${result.message}`);
                    location.reload();
                } else {
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                console.error('Error toggling about status:', error);
                alert('Error updating about status: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''






# About Page Management Routes
@admin_bp.route('/admin/about-management')
def about_management():
    """About page management interface"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin.admin_login'))
    
    # Load current about content
    about_content = load_about_content()
    
    # Get current about-minds-eye image
    current_image = get_about_minds_eye_image()
    
    message = request.args.get('message', '')
    message_type = request.args.get('message_type', 'info')
    
    return render_template_string(ABOUT_MANAGEMENT_TEMPLATE, 
                                about_content=about_content,
                                current_image=current_image,
                                message=message,
                                message_type=message_type)

@admin_bp.route('/admin/update-about-content', methods=['POST'])
def update_about_content():
    """Update about-minds-eye page content"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin.admin_login'))
    
    try:
        content = {
            'main_content': request.form.get('main_content', ''),
            'signature': request.form.get('signature', 'Rick Corey')
        }
        
        save_about_content(content)
        
        return redirect(url_for('admin.about_management') + '?message=About content updated successfully!&message_type=success')
    except Exception as e:
        return redirect(url_for('admin.about_management') + f'?message=Update failed: {str(e)}&message_type=error')

@admin_bp.route('/admin/upload-about-image', methods=['POST'])
def upload_about_image():
    """Upload image for about-minds-eye page (replaces current image like Featured)"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin.admin_login'))
    
    try:
        print("🔍 DEBUG: Starting about image upload")
        if 'image' not in request.files:
            print("🔍 DEBUG: No image in request.files")
            return redirect(url_for('admin.about_management') + '?message=No image file selected&message_type=error')
        
        file = request.files['image']
        print(f"🔍 DEBUG: File received: {file.filename}")
        if file.filename == '':
            print("🔍 DEBUG: Empty filename")
            return redirect(url_for('admin.about_management') + '?message=No image file selected&message_type=error')
        
        if file:
            # Generate unique filename
            filename = f"about-minds-eye-{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(PHOTOGRAPHY_ASSETS_DIR, filename)
            print(f"🔍 DEBUG: Saving to: {filepath}")
            
            # Save file
            file.save(filepath)
            print(f"🔍 DEBUG: File saved successfully")
            
            # Replace the about-minds-eye image (like Featured Image does)
            set_about_minds_eye_image(filename)
            print(f"🔍 DEBUG: Filename set in JSON: {filename}")
            
            return redirect(url_for('admin.about_management') + '?message=About image updated successfully!&message_type=success')
    except Exception as e:
        print(f"🔍 DEBUG: Upload error: {str(e)}")
        return redirect(url_for('admin.about_management') + f'?message=Upload failed: {str(e)}&message_type=error')

@admin_bp.route('/admin/delete-about-image', methods=['POST'])
def delete_about_image():
    """Delete about page image"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin.admin_login'))
    
    try:
        filename = request.form.get('filename')
        if not filename:
            return redirect(url_for('admin.about_management') + '?message=No filename provided&message_type=error')
        
        # Remove from filesystem
        filepath = os.path.join(PHOTOGRAPHY_ASSETS_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remove from about images list
        remove_about_image(filename)
        
        return redirect(url_for('admin.about_management') + '?message=Image deleted successfully!&message_type=success')
    except Exception as e:
        return redirect(url_for('admin.about_management') + f'?message=Delete failed: {str(e)}&message_type=error')

# About page helper functions
def load_about_content():
    """Load about page content"""
    about_file = '/data/about_content.json'
    try:
        if os.path.exists(about_file):
            with open(about_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading about content: {e}")
    
    # Default content
    return {
        'title': 'About Mind\'s Eye Photography',
        'subtitle': 'Where Moments Meet Imagination',
        'section_title': 'On Location',
        'main_content': 'Born and raised right here in Madison, Wisconsin, I\'m a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a musician/songwriter, a Teacher, a REALTOR, and a Small Business Owner. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.',
        'bottom_content': 'At the heart of Mind\'s Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.\n\nFor me, client satisfaction isn\'t just a goal – it\'s the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It\'s truly rewarding to see clients transform into lifelong friends, and that\'s the kind of connection I strive to build with everyone I work with.',
        'signature': 'Rick Corey'
    }

def save_about_content(content):
    """Save about page content"""
    about_file = '/data/about_content.json'
    os.makedirs(os.path.dirname(about_file), exist_ok=True)
    with open(about_file, 'w') as f:
        json.dump(content, f, indent=2)

def get_about_images():
    """Get list of about page images"""
    about_images_file = os.path.join(os.path.dirname(PHOTOGRAPHY_ASSETS_DIR), 'about_images.json')
    try:
        if os.path.exists(about_images_file):
            with open(about_images_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading about images: {e}")
    return []

def set_about_minds_eye_image(filename):
    """Set the about-minds-eye image (replaces current like Featured Image)"""
    about_image_file = '/data/about_minds_eye_image.json'
    os.makedirs(os.path.dirname(about_image_file), exist_ok=True)
    with open(about_image_file, 'w') as f:
        json.dump({'filename': filename}, f, indent=2)

def get_about_minds_eye_image():
    """Get the current about-minds-eye image"""
    about_image_file = '/data/about_minds_eye_image.json'
    try:
        if os.path.exists(about_image_file):
            with open(about_image_file, 'r') as f:
                data = json.load(f)
                return data.get('filename')
    except Exception as e:
        print(f"Error loading about-minds-eye image: {e}")
    return None

def add_about_image(filename):
    """Add image to about page images list"""
    images = get_about_images()
    if filename not in images:
        images.append(filename)
        save_about_images(images)

def remove_about_image(filename):
    """Remove image from about page images list"""
    images = get_about_images()
    if filename in images:
        images.remove(filename)
        save_about_images(images)

def save_about_images(images):
    """Save about page images list"""
    about_images_file = os.path.join(os.path.dirname(PHOTOGRAPHY_ASSETS_DIR), 'about_images.json')
    os.makedirs(os.path.dirname(about_images_file), exist_ok=True)
    with open(about_images_file, 'w') as f:
        json.dump(images, f, indent=2)

# About Management Template
ABOUT_MANAGEMENT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>About Page Management</title>
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
            border-bottom: 2px solid #333; 
        }
        h1 { color: #ff6b35; margin: 0; }
        h2 { color: #ff6b35; margin-top: 30px; margin-bottom: 15px; }
        .back-btn { 
            background: #666; 
            color: #fff; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
        }
        .back-btn:hover { background: #777; }
        .preview-btn { 
            background: #007bff; 
            color: #fff; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            margin-left: 10px; 
        }
        .preview-btn:hover { background: #0056b3; }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            color: #ff6b35; 
            font-weight: bold; 
        }
        input[type="text"], textarea, input[type="file"] { 
            width: 100%; 
            padding: 10px; 
            background: #333; 
            border: 1px solid #555; 
            color: #fff; 
            border-radius: 5px; 
        }
        textarea { 
            height: 200px; 
            resize: vertical; 
        }
        .btn { 
            background: #ff6b35; 
            color: #fff; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .btn:hover { background: #e55a2b; }
        .message { 
            padding: 15px; 
            margin: 20px 0; 
            border-radius: 5px; 
        }
        .success-message { 
            background: #28a745; 
            color: #fff; 
        }
        .error-message { 
            background: #dc3545; 
            color: #fff; 
        }
        .current-image { 
            max-width: 400px; 
            border-radius: 5px; 
            margin-top: 10px; 
            border: 2px solid #ff6b35;
            box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
        }
        
        /* Rich Text Editor Styles */
        .editor-toolbar {
            background: #444;
            border: 1px solid #555;
            border-bottom: none;
            padding: 8px;
            border-radius: 5px 5px 0 0;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        .editor-btn {
            background: #555;
            color: #fff;
            border: 1px solid #666;
            padding: 6px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            min-width: 30px;
            text-align: center;
        }
        .editor-btn:hover {
            background: #666;
        }
        .editor-btn.active {
            background: #ff6b35;
            border-color: #ff6b35;
        }
        .editor-content {
            background: #333;
            border: 1px solid #555;
            border-radius: 0 0 5px 5px;
            padding: 15px;
            min-height: 300px;
            color: #fff;
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            outline: none;
        }
        .editor-content:focus {
            border-color: #ff6b35;
        }
        #main_content {
            display: none;
        }
        .editor-separator {
            width: 1px;
            background: #666;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>About Page Management</h1>
        <div>
            <a href="/admin/dashboard" class="back-btn">← Back to Admin</a>
            <a href="/about-minds-eye" class="preview-btn" target="_blank">👁️ Preview About Page</a>
        </div>
    </div>

    {% if message %}
        <div class="message {{ 'success-message' if message_type == 'success' else 'error-message' }}">
            {{ message }}
        </div>
    {% endif %}

    <h2>Content Management</h2>
    <form method="POST" action="/admin/update-about-content">
        <div class="form-group">
            <label for="main_content">Main Content:</label>
            <div class="editor-toolbar">
                <button type="button" class="editor-btn" onclick="formatText('bold')" title="Bold"><b>B</b></button>
                <button type="button" class="editor-btn" onclick="formatText('italic')" title="Italic"><i>I</i></button>
                <button type="button" class="editor-btn" onclick="formatText('underline')" title="Underline"><u>U</u></button>
                <div class="editor-separator"></div>
                <button type="button" class="editor-btn" onclick="formatHeading('h1')" title="Heading 1">H1</button>
                <button type="button" class="editor-btn" onclick="formatHeading('h2')" title="Heading 2">H2</button>
                <button type="button" class="editor-btn" onclick="formatHeading('h3')" title="Heading 3">H3</button>
                <div class="editor-separator"></div>
                <button type="button" class="editor-btn" onclick="formatText('insertUnorderedList')" title="Bullet List">• List</button>
                <button type="button" class="editor-btn" onclick="formatText('insertOrderedList')" title="Numbered List">1. List</button>
                <div class="editor-separator"></div>
                <button type="button" class="editor-btn" onclick="formatText('justifyLeft')" title="Align Left">←</button>
                <button type="button" class="editor-btn" onclick="formatText('justifyCenter')" title="Align Center">↔</button>
                <button type="button" class="editor-btn" onclick="formatText('justifyRight')" title="Align Right">→</button>
            </div>
            <div id="editor-content" class="editor-content" contenteditable="true"></div>
            <textarea name="main_content" id="main_content" required>{{ about_content.main_content }}</textarea>
        </div>
        
        <div class="form-group">
            <label for="signature">Signature:</label>
            <input type="text" name="signature" id="signature" value="{{ about_content.signature }}" required>
        </div>
        
        <button type="submit" class="btn">Update Content</button>
    </form>

    <h2>Image Management</h2>
    <p>Upload a single image for the About page. This will replace the current image.</p>
    
    {% if current_image %}
        <div>
            <p><strong>Current Image:</strong></p>
            <img src="/data/{{ current_image }}" alt="Current About Image" class="current-image">
        </div>
    {% endif %}
    
    <form method="POST" action="/admin/upload-about-image" enctype="multipart/form-data">
        <div class="form-group">
            <label for="image">Upload New Image:</label>
            <input type="file" name="image" id="image" accept="image/*" required>
        </div>
        
        <button type="submit" class="btn">Upload Image</button>
    </form>

    <script>
        // Initialize the editor
        const editor = document.getElementById('editor-content');
        const textarea = document.getElementById('main_content');
        
        // Load initial content
        editor.innerHTML = textarea.value || '';
        
        // Format text function
        function formatText(command) {
            document.execCommand(command, false, null);
            editor.focus();
            updateTextarea();
        }
        
        // Format heading function
        function formatHeading(tag) {
            document.execCommand('formatBlock', false, tag);
            editor.focus();
            updateTextarea();
        }
        
        // Update textarea with editor content
        function updateTextarea() {
            textarea.value = editor.innerHTML;
        }
        
        // Update textarea on content change
        editor.addEventListener('input', updateTextarea);
        editor.addEventListener('paste', function() {
            setTimeout(updateTextarea, 10);
        });
        
        // Update textarea before form submission
        document.querySelector('form').addEventListener('submit', function() {
            updateTextarea();
        });
        
        // Focus editor on load
        editor.focus();
    </script>
</body>
</html>
'''
