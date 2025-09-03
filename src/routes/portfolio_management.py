import os
import json
from flask import Blueprint, request, render_template_string, redirect, url_for, session, jsonify

portfolio_mgmt_bp = Blueprint('portfolio_mgmt', __name__)

# File paths
PORTFOLIO_DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'portfolio-data-multicategory.json')
CATEGORIES_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'categories-config.json')
STATIC_ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets')

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
        print(f"✅ Saved portfolio data to multicategory file: {PORTFOLIO_DATA_FILE}")
        
        # Also save to regular portfolio-data.json (frontend uses this)
        regular_portfolio_file = os.path.join(os.path.dirname(PORTFOLIO_DATA_FILE), 'portfolio-data.json')
        with open(regular_portfolio_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved portfolio data to regular file: {regular_portfolio_file}")
        
        return True
    except Exception as e:
        print(f"❌ Error saving portfolio data: {e}")
        return False

@portfolio_mgmt_bp.route('/admin/portfolio-management')
def portfolio_management():
    """Portfolio management admin interface - USING DATABASE"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Load data from SQL database instead of JSON files
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
            'filename': image.filename,
            'title': image.title,
            'description': image.description,
            'categories': image_categories,
            'is_slideshow_background': getattr(image, 'is_slideshow_background', False)
        })
    
    # Get categories from database
    categories = Category.query.all()
    available_categories = [cat.name for cat in categories]
    
    admin_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio Management</title>
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
            .management-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
                gap: 20px; 
                margin-top: 20px; 
            }
            .image-card { 
                background: #222; 
                border-radius: 10px; 
                overflow: hidden; 
                padding: 15px;
            }
            .image-card img { 
                width: 100%; 
                height: 150px; 
                object-fit: cover; 
                border-radius: 8px;
                margin-bottom: 15px;
            }
            .image-info h3 { 
                margin: 0 0 10px 0; 
                color: #ff6b35; 
                font-size: 16px;
            }
            .image-info p { 
                margin: 0 0 15px 0; 
                color: #ccc; 
                font-size: 14px;
                line-height: 1.4;
            }
            .current-categories {
                margin-bottom: 15px;
            }
            .current-categories h4 {
                margin: 0 0 8px 0;
                color: #ff6b35;
                font-size: 14px;
            }
            .category-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }
            .category-tag {
                background: #ff6b35;
                color: #fff;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            .category-checkboxes {
                margin-bottom: 15px;
            }
            .category-checkboxes h4 {
                margin: 0 0 10px 0;
                color: #ff6b35;
                font-size: 14px;
            }
            .checkbox-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }
            .checkbox-item {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .checkbox-item input[type="checkbox"] {
                width: 16px;
                height: 16px;
            }
            .checkbox-item label {
                font-size: 13px;
                color: #ccc;
                cursor: pointer;
            }
            .action-buttons {
                display: flex;
                gap: 10px;
                margin-top: 15px;
                flex-wrap: wrap;
            }
            .update-btn, .edit-btn {
                background: #ff6b35;
                color: #fff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                flex: 1;
                min-width: 120px;
            }
            .delete-btn {
                background: #dc3545;
                color: #fff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                min-width: 80px;
            }
            .update-btn:hover, .edit-btn:hover {
                background: #e55a2b;
            }
            .delete-btn:hover {
                background: #c82333;
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
            .bulk-actions {
                background: #333;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .bulk-actions h3 {
                margin: 0 0 15px 0;
                color: #ff6b35;
            }
            .bulk-select {
                display: flex;
                gap: 15px;
                align-items: center;
                margin-bottom: 15px;
            }
            .select-all-btn, .clear-all-btn {
                background: #666;
                color: #fff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
            }
            .bulk-category-update {
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }
            .bulk-update-btn {
                background: #ff6b35;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            
            /* Edit Modal Styles */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
            }
            .modal-content {
                background-color: #222;
                margin: 5% auto;
                padding: 30px;
                border-radius: 10px;
                width: 90%;
                max-width: 600px;
                position: relative;
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                position: absolute;
                right: 20px;
                top: 15px;
                cursor: pointer;
            }
            .close:hover {
                color: #fff;
            }
            .edit-form {
                margin-top: 20px;
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
            .form-group input, .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #555;
                border-radius: 4px;
                background: #333;
                color: #fff;
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }
            .form-group textarea {
                resize: vertical;
                min-height: 80px;
            }
            .save-btn, .cancel-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin-right: 10px;
            }
            .save-btn {
                background: #ff6b35;
                color: #fff;
            }
            .cancel-btn {
                background: #666;
                color: #fff;
            }
            .save-btn:hover {
                background: #e55a2b;
            }
            .cancel-btn:hover {
                background: #555;
            }
        </style>
        <script>
            function selectAllImages() {
                const checkboxes = document.querySelectorAll('input[name="selected_images"]');
                checkboxes.forEach(cb => cb.checked = true);
            }
            
            function clearAllImages() {
                const checkboxes = document.querySelectorAll('input[name="selected_images"]');
                checkboxes.forEach(cb => cb.checked = false);
            }
            
            function updateImageCategories(imageId) {
                const form = document.getElementById('form_' + imageId);
                const formData = new FormData(form);
                
                fetch('/admin/portfolio-management/update', {
                    method: 'POST',
                    body: formData
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
            
            function deleteImage(imageId) {
                if (confirm('Are you sure you want to delete this image? This action cannot be undone.')) {
                    fetch('/admin/portfolio-management/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({image_id: imageId})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error deleting image: ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('Error deleting image: ' + error);
                    });
                }
            }
            
            function bulkUpdateCategories() {
                const selectedImages = Array.from(document.querySelectorAll('input[name="selected_images"]:checked')).map(cb => cb.value);
                const selectedCategories = Array.from(document.querySelectorAll('input[name="bulk_categories"]:checked')).map(cb => cb.value);
                
                if (selectedImages.length === 0) {
                    alert('Please select at least one image');
                    return;
                }
                
                if (selectedCategories.length === 0) {
                    alert('Please select at least one category');
                    return;
                }
                
                if (confirm(`Update ${selectedImages.length} images with categories: ${selectedCategories.join(', ')}?`)) {
                    fetch('/admin/portfolio-management/bulk-update', {
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
                            alert('Error updating images: ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('Error updating images: ' + error);
                    });
                }
            }
            
            // Edit Modal Functions
            function openEditModal(imageId, currentTitle, currentDescription) {
                document.getElementById('editModal').style.display = 'block';
                document.getElementById('editImageId').value = imageId;
                document.getElementById('editTitle').value = currentTitle;
                document.getElementById('editDescription').value = currentDescription;
                document.getElementById('modalTitle').textContent = 'Edit: ' + currentTitle;
            }
            
            function closeEditModal() {
                document.getElementById('editModal').style.display = 'none';
            }
            
            function saveImageEdit() {
                const imageId = document.getElementById('editImageId').value;
                const newTitle = document.getElementById('editTitle').value.trim();
                const newDescription = document.getElementById('editDescription').value.trim();
                
                if (!newTitle) {
                    alert('Title is required');
                    return;
                }
                
                if (!newDescription) {
                    alert('Description is required');
                    return;
                }
                
                fetch('/admin/portfolio-management/edit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        image_id: imageId,
                        title: newTitle,
                        description: newDescription
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        closeEditModal();
                        location.reload();
                    } else {
                        alert('Error updating image: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error updating image: ' + error);
                });
            }
            
            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('editModal');
                if (event.target == modal) {
                    closeEditModal();
                }
            }
        </script>
    </head>
    <body>
        <div class="header">
            <h1>Portfolio Management</h1>
            <a href="/admin/dashboard" class="back-btn">← Back to Dashboard</a>
        </div>
        
        {% if message %}
        <div class="message {{ message_type }}-message">
            {{ message }}
        </div>
        {% endif %}
        
        <!-- Bulk Actions -->
        <div class="bulk-actions">
            <h3>Bulk Operations</h3>
            <div class="bulk-select">
                <button onclick="selectAllImages()" class="select-all-btn">Select All</button>
                <button onclick="clearAllImages()" class="clear-all-btn">Clear All</button>
                <span style="color: #ccc; font-size: 14px;">Select multiple images to update their categories at once</span>
            </div>
            <div class="bulk-category-update">
                <span style="color: #ccc; font-size: 14px;">Set categories for selected images:</span>
                {% for category in available_categories %}
                <div class="checkbox-item">
                    <input type="checkbox" name="bulk_categories" value="{{ category }}" id="bulk_{{ category }}">
                    <label for="bulk_{{ category }}">{{ category }}</label>
                </div>
                {% endfor %}
                <button onclick="bulkUpdateCategories()" class="bulk-update-btn">Update Selected Images</button>
                <button onclick="bulkDeleteImages()" class="bulk-delete-btn">Delete Selected</button>
            </div>
        </div>
        
        <!-- Portfolio Management Grid -->
        <div class="management-grid">
            {% for item in portfolio_data %}
            <div class="image-card">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                    <input type="checkbox" name="selected_images" value="{{ item.id }}" style="width: 18px; height: 18px;">
                    <span style="color: #ccc; font-size: 14px;">Select for bulk operations</span>
                </div>
                
                <img src="/static/assets/{{ item.image }}" alt="{{ item.title }}">
                
                <div class="image-info">
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.description }}</p>
                    
                    <div class="current-categories">
                        <h4>Current Categories:</h4>
                        <div class="category-tags">
                            {% for category in item.get('categories', [item.get('category', '')]) %}
                            {% if category %}
                            <span class="category-tag">{{ category }}</span>
                            {% endif %}
                            {% endfor %}
                        </div>
                    </div>
                    
                    <form id="form_{{ item.id }}">
                        <input type="hidden" name="image_id" value="{{ item.id }}">
                        
                        <div class="category-checkboxes">
                            <h4>Update Categories:</h4>
                            <div class="checkbox-grid">
                                {% for category in available_categories %}
                                <div class="checkbox-item">
                                    <input type="checkbox" 
                                           name="categories" 
                                           value="{{ category }}" 
                                           id="{{ item.id }}_{{ category }}"
                                           {% if category in item.get('categories', [item.get('category', '')]) %}checked{% endif %}>
                                    <label for="{{ item.id }}_{{ category }}">{{ category }}</label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <div class="action-buttons">
                            <button type="button" 
                                    onclick="openEditModal('{{ item.id }}', '{{ item.title|replace("'", "\\'") }}', '{{ item.description|replace("'", "\\'") }}')" 
                                    class="edit-btn">
                                ✏️ Edit Title/Description
                            </button>
                            <button type="button" onclick="updateImageCategories('{{ item.id }}')" class="update-btn">
                                Update Categories
                            </button>
                            <button type="button" onclick="deleteImage('{{ item.id }}')" class="delete-btn">
                                Delete
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if not portfolio_data %}
        <div style="text-align: center; color: #666; margin-top: 50px;">
            <h3>No images in portfolio</h3>
            <p>Upload some images first to manage them here.</p>
        </div>
        {% endif %}
        
        <!-- Edit Modal -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeEditModal()">&times;</span>
                <h2 id="modalTitle" style="color: #ff6b35; margin-top: 0;">Edit Image</h2>
                
                <div class="edit-form">
                    <input type="hidden" id="editImageId">
                    
                    <div class="form-group">
                        <label for="editTitle">Image Title:</label>
                        <input type="text" id="editTitle" placeholder="Enter image title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="editDescription">Description:</label>
                        <textarea id="editDescription" placeholder="Enter image description" required></textarea>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <button onclick="saveImageEdit()" class="save-btn">💾 Save Changes</button>
                        <button onclick="closeEditModal()" class="cancel-btn">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(admin_html, 
                                portfolio_data=portfolio_data,
                                available_categories=available_categories,
                                message=request.args.get('message'),
                                message_type=request.args.get('message_type', 'success'))

@portfolio_mgmt_bp.route('/admin/portfolio-management/edit', methods=['POST'])
def edit_image():
    """Edit title and description for an image"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        new_title = data.get('title', '').strip()
        new_description = data.get('description', '').strip()
        
        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID required'})
        
        if not new_title:
            return jsonify({'success': False, 'message': 'Title is required'})
        
        if not new_description:
            return jsonify({'success': False, 'message': 'Description is required'})
        
        # Load portfolio data
        portfolio_data = load_portfolio_data()
        
        # Find and update the image
        image_found = False
        for item in portfolio_data:
            if item.get('id') == image_id:
                item['title'] = new_title
                item['description'] = new_description
                image_found = True
                break
        
        if not image_found:
            return jsonify({'success': False, 'message': 'Image not found'})
        
        # Save updated data
        if save_portfolio_data(portfolio_data):
            return jsonify({'success': True, 'message': 'Image updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save changes'})
            
    except Exception as e:
        print(f"Edit image error: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@portfolio_mgmt_bp.route('/admin/portfolio-management/update', methods=['POST'])
def update_image_categories():
    """Update categories for a single image"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        image_id = request.form.get('image_id')
        new_categories = request.form.getlist('categories')
        
        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID required'})
        
        if not new_categories:
            return jsonify({'success': False, 'message': 'At least one category must be selected'})
        
        # Load portfolio data
        portfolio_data = load_portfolio_data()
        
        # Find and update the image
        image_found = False
        for item in portfolio_data:
            if item.get('id') == image_id:
                item['categories'] = new_categories
                # Remove old single category field if it exists
                if 'category' in item:
                    del item['category']
                image_found = True
                break
        
        if not image_found:
            return jsonify({'success': False, 'message': 'Image not found'})
        
        # Save updated data
        if save_portfolio_data(portfolio_data):
            return jsonify({'success': True, 'message': 'Categories updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save changes'})
            
    except Exception as e:
        print(f"Update categories error: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@portfolio_mgmt_bp.route('/admin/portfolio-management/delete', methods=['POST'])
def delete_image():
    """Delete an image from the portfolio"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        
        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID required'})
        
        # Load portfolio data
        portfolio_data = load_portfolio_data()
        
        # Find and remove the image
        image_found = False
        image_filename = None
        for i, item in enumerate(portfolio_data):
            if item.get('id') == image_id:
                image_filename = item.get('image')
                portfolio_data.pop(i)
                image_found = True
                break
        
        if not image_found:
            return jsonify({'success': False, 'message': 'Image not found'})
        
        # Delete the physical file
        if image_filename:
            try:
                image_path = os.path.join(STATIC_ASSETS_DIR, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
                # Continue even if file deletion fails
        
        # Save updated data
        if save_portfolio_data(portfolio_data):
            return jsonify({'success': True, 'message': 'Image deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save changes'})
            
    except Exception as e:
        print(f"Delete image error: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@portfolio_mgmt_bp.route('/admin/portfolio-management/bulk-update', methods=['POST'])
def bulk_update_categories():
    """Update categories for multiple images"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        new_categories = data.get('categories', [])
        
        if not image_ids:
            return jsonify({'success': False, 'message': 'No images selected'})
        
        if not new_categories:
            return jsonify({'success': False, 'message': 'At least one category must be selected'})
        
        # Load portfolio data
        portfolio_data = load_portfolio_data()
        
        # Update selected images
        updated_count = 0
        for item in portfolio_data:
            if item.get('id') in image_ids:
                item['categories'] = new_categories
                # Remove old single category field if it exists
                if 'category' in item:
                    del item['category']
                updated_count += 1
        
        if updated_count == 0:
            return jsonify({'success': False, 'message': 'No images found to update'})
        
        # Save updated data
        if save_portfolio_data(portfolio_data):
            return jsonify({'success': True, 'message': f'Updated {updated_count} images successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save changes'})
            
    except Exception as e:
        print(f"Bulk update error: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

