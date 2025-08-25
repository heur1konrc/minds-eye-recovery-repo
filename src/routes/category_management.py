import os
import json
from flask import Blueprint, request, render_template_string, redirect, url_for, session, jsonify

category_mgmt_bp = Blueprint('category_mgmt', __name__)

# File paths
PORTFOLIO_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'portfolio-data-multicategory.json')
CATEGORIES_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'categories-config.json')
STATIC_ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets')

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
    """Save portfolio data to JSON file"""
    try:
        os.makedirs(os.path.dirname(PORTFOLIO_DATA_FILE), exist_ok=True)
        with open(PORTFOLIO_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving portfolio data: {e}")
        return False

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
        'categories': ['Wildlife', 'Landscapes', 'Portraits', 'Events', 'Nature', 'Commercial'],
        'default_category': 'All',
        'category_order': ['Wildlife', 'Landscapes', 'Portraits', 'Events', 'Nature', 'Commercial']
    }

def save_categories_config(config):
    """Save categories configuration"""
    try:
        print(f"=== SAVING CATEGORIES CONFIG ===")
        print(f"Config to save: {config}")
        print(f"File path: {CATEGORIES_CONFIG_FILE}")
        
        os.makedirs(os.path.dirname(CATEGORIES_CONFIG_FILE), exist_ok=True)
        with open(CATEGORIES_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Categories config saved successfully")
        return True
    except Exception as e:
        print(f"Error saving categories config: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_category_usage():
    """Get usage count for each category"""
    portfolio_data = load_portfolio_data()
    usage = {}
    
    for item in portfolio_data:
        categories = item.get('categories', [item.get('category', '')])
        if isinstance(categories, str):
            categories = [categories]
        
        for category in categories:
            if category:
                usage[category] = usage.get(category, 0) + 1
    
    return usage

@category_mgmt_bp.route('/admin/category-management')
def category_management():
    """Category management admin interface"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get categories from database instead of JSON
    from ..models import Category, Image, ImageCategory
    
    categories = Category.query.all()
    
    # Get usage counts from database
    usage = {}
    for category in categories:
        count = ImageCategory.query.filter_by(category_id=category.id).count()
        usage[category.name] = count
    
    # Create config structure for template compatibility
    config = {
        'categories': [cat.name for cat in categories],
        'default_category': 'All'  # This could be made dynamic later
    }
    
    admin_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Category Management</title>
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
            .back-btn { 
                background: #444; 
                color: #fff; 
                padding: 10px 20px; 
                text-decoration: none; 
                border-radius: 5px; 
            }
            .management-sections {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            .section {
                background: #222;
                border-radius: 10px;
                padding: 20px;
            }
            .section h2 {
                color: #ff6b35;
                margin: 0 0 20px 0;
                font-size: 20px;
            }
            .current-categories {
                background: #333;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 30px;
            }
            .category-list {
                display: grid;
                gap: 15px;
            }
            .category-item {
                background: #444;
                border-radius: 8px;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .category-info {
                flex: 1;
            }
            .category-name {
                color: #ff6b35;
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 5px;
            }
            .category-usage {
                color: #ccc;
                font-size: 14px;
            }
            .category-actions {
                display: flex;
                gap: 10px;
            }
            .default-indicator {
                background: #28a745;
                color: #fff;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #ff6b35;
                font-weight: bold;
            }
            .form-group input, .form-group select {
                width: 100%;
                padding: 12px;
                background: #333;
                border: 1px solid #555;
                border-radius: 5px;
                color: #fff;
                font-size: 14px;
            }
            .btn {
                background: #ff6b35;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover {
                background: #e55a2b;
            }
            .btn-danger {
                background: #dc3545;
            }
            .btn-danger:hover {
                background: #c82333;
            }
            .btn-success {
                background: #28a745;
            }
            .btn-success:hover {
                background: #218838;
            }
            .btn-small {
                padding: 6px 12px;
                font-size: 12px;
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
            .warning-box {
                background: #5a4d2d;
                color: #ffd700;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 4px solid #ffd700;
            }
            .rename-form {
                display: none;
                margin-top: 10px;
                padding: 15px;
                background: #333;
                border-radius: 5px;
            }
            .rename-form.active {
                display: block;
            }
            .inline-form {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            .inline-form input {
                flex: 1;
                margin: 0;
            }
        </style>
        <script>
            function showRenameForm(categoryName) {
                // Hide all rename forms
                document.querySelectorAll('.rename-form').forEach(form => {
                    form.classList.remove('active');
                });
                
                // Show the specific rename form
                const form = document.getElementById('rename_' + categoryName.replace(/[^a-zA-Z0-9]/g, '_'));
                if (form) {
                    form.classList.add('active');
                }
            }
            
            function hideRenameForm(categoryName) {
                const form = document.getElementById('rename_' + categoryName.replace(/[^a-zA-Z0-9]/g, '_'));
                if (form) {
                    form.classList.remove('active');
                }
            }
            
            function deleteCategory(categoryName, imageCount) {
                if (imageCount > 0) {
                    if (!confirm(`This category contains ${imageCount} images. Deleting it will remove the category from all images. Are you sure?`)) {
                        return;
                    }
                } else {
                    if (!confirm(`Delete the category "${categoryName}"?`)) {
                        return;
                    }
                }
                
                fetch('/admin/category-management/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({category_name: categoryName})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error deleting category: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error deleting category: ' + error);
                });
            }
            
            function setDefaultCategory(categoryName) {
                fetch('/admin/category-management/set-default', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({category_name: categoryName})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error setting default category: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error setting default category: ' + error);
                });
            }
        </script>
    </head>
    <body>
        <div class="header">
            <h1>Category Management</h1>
            <a href="/admin/dashboard" class="back-btn">← Back to Dashboard</a>
        </div>
        
        {% if message %}
        <div class="message {{ message_type }}-message">
            {{ message }}
        </div>
        {% endif %}
        
        <!-- Current Categories -->
        <div class="current-categories">
            <h2>Current Categories</h2>
            <div class="warning-box">
                <strong>⚠️ Important:</strong> Renaming or deleting categories will affect all images using those categories. 
                Changes are permanent and will update your live website immediately.
            </div>
            
            <div class="category-list">
                {% for category in config.categories %}
                <div class="category-item">
                    <div class="category-info">
                        <div class="category-name">
                            {{ category }}
                            {% if category == config.default_category %}
                            <span class="default-indicator">DEFAULT</span>
                            {% endif %}
                        </div>
                        <div class="category-usage">
                            {{ usage.get(category, 0) }} images
                        </div>
                    </div>
                    
                    <div class="category-actions">
                        {% if category != config.default_category %}
                        <button onclick="setDefaultCategory('{{ category }}')" class="btn btn-success btn-small">
                            Set Default
                        </button>
                        {% endif %}
                        
                        <button onclick="showRenameForm('{{ category }}')" class="btn btn-small">
                            Rename
                        </button>
                        
                        <button onclick="deleteCategory('{{ category }}', {{ usage.get(category, 0) }})" class="btn btn-danger btn-small">
                            Delete
                        </button>
                    </div>
                </div>
                
                <!-- Rename Form -->
                <div id="rename_{{ category.replace(' ', '_') }}" class="rename-form">
                    <form method="POST" action="/admin/category-management/rename">
                        <input type="hidden" name="old_name" value="{{ category }}">
                        <div class="inline-form">
                            <input type="text" name="new_name" value="{{ category }}" required>
                            <button type="submit" class="btn btn-small">Save</button>
                            <button type="button" onclick="hideRenameForm('{{ category }}')" class="btn btn-small" style="background: #666;">Cancel</button>
                        </div>
                    </form>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Management Sections -->
        <div class="management-sections">
            <!-- Add New Category -->
            <div class="section">
                <h2>Add New Category</h2>
                <form method="POST" action="/admin/category-management/add">
                    <div class="form-group">
                        <label for="category_name">Category Name</label>
                        <input type="text" id="category_name" name="category_name" placeholder="e.g., Architecture" required>
                    </div>
                    <button type="submit" class="btn">Add Category</button>
                </form>
            </div>
            
            <!-- Default Category Settings -->
            <div class="section">
                <h2>Default Category Settings</h2>
                <p style="color: #ccc; margin-bottom: 20px;">
                    Choose which category visitors see first when they visit your portfolio. 
                    Currently: <strong style="color: #ff6b35;">{{ config.default_category }}</strong>
                </p>
                
                <form method="POST" action="/admin/category-management/set-default">
                    <div class="form-group">
                        <label for="default_category">Default Category</label>
                        <select id="default_category" name="category_name" required>
                            <option value="All" {% if config.default_category == 'All' %}selected{% endif %}>All (Show all images)</option>
                            {% for category in config.categories %}
                            <option value="{{ category }}" {% if config.default_category == category %}selected{% endif %}>{{ category }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button type="submit" class="btn">Set Default</button>
                </form>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="section">
            <h2>Quick Actions</h2>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <form method="POST" action="/admin/category-management/rename" style="display: inline;">
                    <input type="hidden" name="old_name" value="Commercial">
                    <input type="hidden" name="new_name" value="Miscellaneous">
                    <button type="submit" class="btn">Change "Commercial" to "Miscellaneous"</button>
                </form>
                
                <a href="/admin/portfolio-management" class="btn" style="background: #666;">
                    📁 Manage Portfolio Images
                </a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(admin_html, 
                                config=config,
                                usage=usage,
                                message=request.args.get('message'),
                                message_type=request.args.get('message_type', 'success'))

@category_mgmt_bp.route('/admin/category-management/add', methods=['POST'])
def add_category():
    """Add a new category"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        from ..models import Category, db
        
        # Ensure database tables exist
        db.create_all()
        
        category_name = request.form.get('category_name', '').strip()
        print(f"=== ADD CATEGORY REQUEST ===")
        print(f"Category name: '{category_name}'")
        
        if not category_name:
            print("Error: Category name is empty")
            return redirect(url_for('category_mgmt.category_management', 
                                  message='Category name is required', 
                                  message_type='error'))
        
        # Check if category already exists in database
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            print(f"Error: Category '{category_name}' already exists")
            return redirect(url_for('category_mgmt.category_management', 
                                  message=f'Category "{category_name}" already exists', 
                                  message_type='error'))
        
        # Create new category in database
        new_category = Category(
            name=category_name,
            display_name=category_name,  # Set display_name as well
            color='#ff6b35',  # Default color
            display_order=0
        )
        db.session.add(new_category)
        db.session.commit()
        
        print(f"Category '{category_name}' added successfully to database")
        return redirect(url_for('category_mgmt.category_management', 
                              message=f'Category "{category_name}" added successfully', 
                              message_type='success'))
            
    except Exception as e:
        db.session.rollback()
        print(f"Add category error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('category_mgmt.category_management', 
                              message=f'Server error: {str(e)}', 
                              message_type='error'))

@category_mgmt_bp.route('/admin/category-management/rename', methods=['POST'])
def rename_category():
    """Rename an existing category"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        from ..models import Category, db
        
        old_name = request.form.get('old_name', '').strip()
        new_name = request.form.get('new_name', '').strip()
        
        if not old_name or not new_name:
            return redirect(url_for('category_mgmt.category_management', 
                                  message='Both old and new category names are required', 
                                  message_type='error'))
        
        if old_name == new_name:
            return redirect(url_for('category_mgmt.category_management', 
                                  message='New name must be different from old name', 
                                  message_type='error'))
        
        # Find the category in database
        category = Category.query.filter_by(name=old_name).first()
        if not category:
            return redirect(url_for('category_mgmt.category_management', 
                                  message=f'Category "{old_name}" not found', 
                                  message_type='error'))
        
        # Check if new name already exists
        existing_category = Category.query.filter_by(name=new_name).first()
        if existing_category:
            return redirect(url_for('category_mgmt.category_management', 
                                  message=f'Category "{new_name}" already exists', 
                                  message_type='error'))
        
        # Update the category name in database
        category.name = new_name
        db.session.commit()
        
        return redirect(url_for('category_mgmt.category_management', 
                              message=f'Category renamed from "{old_name}" to "{new_name}"', 
                              message_type='success'))
            
    except Exception as e:
        db.session.rollback()
        print(f"Rename category error: {e}")
        return redirect(url_for('category_mgmt.category_management', 
                              message='Server error occurred', 
                              message_type='error'))

@category_mgmt_bp.route('/admin/category-management/delete', methods=['POST'])
def delete_category():
    """Delete a category"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        from ..models import Category, ImageCategory, db
        
        data = request.get_json()
        category_name = data.get('category_name', '').strip()
        
        if not category_name:
            return jsonify({'success': False, 'message': 'Category name is required'})
        
        # Find the category in database
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            return jsonify({'success': False, 'message': f'Category "{category_name}" not found'})
        
        # Check if category is being used by images
        usage_count = ImageCategory.query.filter_by(category_id=category.id).count()
        
        # Delete all image-category relationships first
        ImageCategory.query.filter_by(category_id=category.id).delete()
        
        # Delete the category itself
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Category "{category_name}" deleted successfully. {usage_count} image associations removed.'
        })
            
    except Exception as e:
        db.session.rollback()
        print(f"Delete category error: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@category_mgmt_bp.route('/admin/category-management/set-default', methods=['POST'])
def set_default_category():
    """Set the default category"""
    if not session.get('admin_logged_in'):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Not authenticated'})
        else:
            return redirect(url_for('admin.admin_login'))
    
    try:
        if request.is_json:
            data = request.get_json()
            category_name = data.get('category_name', '').strip()
        else:
            category_name = request.form.get('category_name', '').strip()
        
        if not category_name:
            message = 'Category name is required'
            if request.is_json:
                return jsonify({'success': False, 'message': message})
            else:
                return redirect(url_for('category_mgmt.category_management', 
                                      message=message, message_type='error'))
        
        config = load_categories_config()
        
        # Allow "All" or any existing category
        if category_name != 'All' and category_name not in config['categories']:
            message = f'Category "{category_name}" not found'
            if request.is_json:
                return jsonify({'success': False, 'message': message})
            else:
                return redirect(url_for('category_mgmt.category_management', 
                                      message=message, message_type='error'))
        
        config['default_category'] = category_name
        
        if save_categories_config(config):
            message = f'Default category set to "{category_name}"'
            if request.is_json:
                return jsonify({'success': True, 'message': message})
            else:
                return redirect(url_for('category_mgmt.category_management', 
                                      message=message, message_type='success'))
        else:
            message = 'Failed to save default category'
            if request.is_json:
                return jsonify({'success': False, 'message': message})
            else:
                return redirect(url_for('category_mgmt.category_management', 
                                      message=message, message_type='error'))
            
    except Exception as e:
        print(f"Set default category error: {e}")
        message = 'Server error occurred'
        if request.is_json:
            return jsonify({'success': False, 'message': message})
        else:
            return redirect(url_for('category_mgmt.category_management', 
                                  message=message, message_type='error'))

@category_mgmt_bp.route('/api/categories-config')
def get_categories_config():
    """API endpoint to get categories configuration for frontend"""
    try:
        config = load_categories_config()
        return jsonify(config)
    except Exception as e:
        print(f"Get categories config error: {e}")
        return jsonify({'error': 'Failed to load categories configuration'}), 500

