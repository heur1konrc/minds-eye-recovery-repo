"""
About Content and Images Management Routes
"""

import os
from flask import Blueprint, request, redirect, url_for, render_template_string, session, jsonify
from werkzeug.utils import secure_filename
from PIL import Image as PILImage
from ..models import db, AboutContent, AboutImage
from ..config import PHOTOGRAPHY_ASSETS_DIR

about_mgmt_bp = Blueprint('about_mgmt', __name__)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@about_mgmt_bp.route('/admin/about-management')
def about_management():
    """About content and images management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get current about content
    about_content = AboutContent.query.first()
    if not about_content:
        # Create default content if none exists
        about_content = AboutContent(content="""
# About Mind's Eye Photography

Welcome to Mind's Eye Photography, where passion meets precision in capturing the world's most stunning moments.

## My Story

With over a decade of experience in professional photography, I specialize in wildlife, landscape, and event photography. My journey began with a simple love for nature and has evolved into a dedicated pursuit of visual storytelling.

## My Approach

Every photograph tells a story. Whether it's the raw power of wildlife in their natural habitat, the serene beauty of landscapes at golden hour, or the candid emotions of special events, I strive to capture authentic moments that resonate with viewers.

## Equipment & Expertise

I use professional-grade equipment including Canon EOS systems with a range of specialized lenses for different shooting conditions. My technical expertise combined with an artistic eye ensures every shot meets the highest standards.

## Let's Create Together

I'm always excited to work on new projects and collaborate with clients who share a passion for exceptional photography. Whether you need professional event coverage, stunning landscape prints, or custom photography services, let's discuss how we can bring your vision to life.
        """.strip())
        db.session.add(about_content)
        db.session.commit()
    
    # Get about images
    about_images = AboutImage.query.order_by(AboutImage.display_order, AboutImage.upload_date).all()
    
    return render_template_string(about_management_html, 
                                about_content=about_content,
                                about_images=about_images,
                                message=request.args.get('message'),
                                message_type=request.args.get('message_type', 'success'))

@about_mgmt_bp.route('/admin/about-content/update', methods=['POST'])
def update_about_content():
    """Update about page content"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        content = request.form.get('content', '').strip()
        
        # Get or create about content record
        about_content = AboutContent.query.first()
        if not about_content:
            about_content = AboutContent(content=content)
            db.session.add(about_content)
        else:
            about_content.content = content
        
        db.session.commit()
        
        return redirect(url_for('about_mgmt.about_management') + '?message=About content updated successfully!&message_type=success')
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('about_mgmt.about_management') + f'?message=Error updating content: {str(e)}&message_type=error')

@about_mgmt_bp.route('/admin/about-images/upload', methods=['POST'])
def upload_about_image():
    """Upload new about image"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        if 'image' not in request.files:
            return redirect(url_for('about_mgmt.about_management') + '?message=No image file provided&message_type=error')
        
        file = request.files['image']
        if file.filename == '':
            return redirect(url_for('about_mgmt.about_management') + '?message=No image selected&message_type=error')
        
        if not allowed_file(file.filename):
            return redirect(url_for('about_mgmt.about_management') + '?message=Invalid file type. Please use PNG, JPG, JPEG, GIF, or WEBP&message_type=error')
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title:
            return redirect(url_for('about_mgmt.about_management') + '?message=Image title is required&message_type=error')
        
        # Create about images directory if it doesn't exist
        about_images_dir = os.path.join(PHOTOGRAPHY_ASSETS_DIR, 'about')
        os.makedirs(about_images_dir, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(about_images_dir, filename)):
            filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        # Save file
        file_path = os.path.join(about_images_dir, filename)
        file.save(file_path)
        
        # Get next display order
        max_order = db.session.query(db.func.max(AboutImage.display_order)).scalar() or 0
        
        # Create database record
        about_image = AboutImage(
            filename=filename,
            title=title,
            description=description,
            display_order=max_order + 1
        )
        
        db.session.add(about_image)
        db.session.commit()
        
        return redirect(url_for('about_mgmt.about_management') + f'?message=About image "{title}" uploaded successfully!&message_type=success')
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('about_mgmt.about_management') + f'?message=Upload failed: {str(e)}&message_type=error')

@about_mgmt_bp.route('/admin/about-images/delete/<int:image_id>', methods=['POST'])
def delete_about_image(image_id):
    """Delete about image"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        about_image = AboutImage.query.get_or_404(image_id)
        
        # Delete file
        file_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, 'about', about_image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.session.delete(about_image)
        db.session.commit()
        
        return redirect(url_for('about_mgmt.about_management') + f'?message=About image deleted successfully!&message_type=success')
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('about_mgmt.about_management') + f'?message=Delete failed: {str(e)}&message_type=error')

@about_mgmt_bp.route('/api/about-content')
def get_about_content():
    """API endpoint to get about content"""
    try:
        about_content = AboutContent.query.first()
        about_images = AboutImage.query.order_by(AboutImage.display_order, AboutImage.upload_date).all()
        
        return jsonify({
            'success': True,
            'content': about_content.content if about_content else '',
            'images': [{
                'id': img.id,
                'filename': img.filename,
                'title': img.title,
                'description': img.description,
                'image_url': img.image_url,
                'display_order': img.display_order
            } for img in about_images]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# HTML Template for About Management
about_management_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Management - Mind's Eye Photography Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #fff;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: rgba(0,0,0,0.3); 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 30px;
            border: 1px solid #374151;
        }
        .header h1 { color: #ff6b35; font-size: 2rem; margin-bottom: 10px; }
        .nav-links { display: flex; gap: 15px; margin-top: 15px; }
        .nav-links a { 
            color: #94a3b8; 
            text-decoration: none; 
            padding: 8px 16px; 
            border-radius: 5px; 
            transition: all 0.3s;
        }
        .nav-links a:hover { background: rgba(255,107,53,0.2); color: #ff6b35; }
        
        .section { 
            background: rgba(0,0,0,0.2); 
            padding: 25px; 
            border-radius: 10px; 
            margin-bottom: 30px;
            border: 1px solid #374151;
        }
        .section h2 { color: #ff6b35; margin-bottom: 20px; font-size: 1.5rem; }
        
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            color: #e2e8f0; 
            font-weight: 500;
        }
        .form-group input, .form-group textarea { 
            width: 100%; 
            padding: 12px; 
            border: 1px solid #4a5568; 
            border-radius: 5px; 
            background: #2d3748; 
            color: #fff;
            font-size: 14px;
        }
        .form-group textarea { 
            min-height: 300px; 
            font-family: 'Courier New', monospace;
            resize: vertical;
        }
        
        .btn { 
            background: #ff6b35; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .btn:hover { background: #e55a2b; transform: translateY(-1px); }
        .btn-danger { background: #dc2626; }
        .btn-danger:hover { background: #b91c1c; }
        
        .message { 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px;
            font-weight: 500;
        }
        .message.success { background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; color: #22c55e; }
        .message.error { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #ef4444; }
        
        .image-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-top: 20px;
        }
        .image-card { 
            background: rgba(0,0,0,0.3); 
            border-radius: 10px; 
            overflow: hidden;
            border: 1px solid #374151;
        }
        .image-card img { 
            width: 100%; 
            height: 200px; 
            object-fit: cover;
        }
        .image-card-content { padding: 15px; }
        .image-card h3 { color: #ff6b35; margin-bottom: 8px; }
        .image-card p { color: #94a3b8; font-size: 14px; margin-bottom: 15px; }
        
        .upload-form { 
            background: rgba(0,0,0,0.2); 
            padding: 20px; 
            border-radius: 8px; 
            border: 1px solid #374151;
            margin-bottom: 20px;
        }
        
        .preview-note {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid #3b82f6;
            color: #60a5fa;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 About Content & Images Management</h1>
            <p>Manage your About page content and photo gallery</p>
            <div class="nav-links">
                <a href="/admin">← Back to Dashboard</a>
                <a href="/about" target="_blank">View About Page</a>
            </div>
        </div>

        {% if message %}
            <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}

        <!-- About Content Editor -->
        <div class="section">
            <h2>📄 About Page Content</h2>
            <div class="preview-note">
                <strong>Markdown Support:</strong> You can use Markdown formatting (# for headers, ** for bold, * for italic, etc.)
            </div>
            
            <form method="POST" action="/admin/about-content/update">
                <div class="form-group">
                    <label for="content">About Page Content (Markdown)</label>
                    <textarea name="content" id="content" placeholder="Write your about page content here...">{{ about_content.content }}</textarea>
                </div>
                <button type="submit" class="btn">💾 Update About Content</button>
            </form>
        </div>

        <!-- About Images Management -->
        <div class="section">
            <h2>📸 About Images Gallery</h2>
            <p style="color: #94a3b8; margin-bottom: 20px;">Upload images of yourself in the field, behind-the-scenes shots, and equipment photos.</p>
            
            <!-- Upload Form -->
            <div class="upload-form">
                <h3 style="color: #ff6b35; margin-bottom: 15px;">Upload New About Image</h3>
                <form method="POST" action="/admin/about-images/upload" enctype="multipart/form-data">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div class="form-group">
                            <label for="image">Select Image</label>
                            <input type="file" name="image" id="image" accept="image/*" required>
                        </div>
                        <div class="form-group">
                            <label for="title">Image Title</label>
                            <input type="text" name="title" id="title" placeholder="e.g., Photographing Wildlife at Sunset" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="description">Description (Optional)</label>
                        <input type="text" name="description" id="description" placeholder="Brief description of the photo...">
                    </div>
                    <button type="submit" class="btn">📤 Upload About Image</button>
                </form>
            </div>

            <!-- Current Images -->
            {% if about_images %}
                <h3 style="color: #ff6b35; margin-bottom: 15px;">Current About Images ({{ about_images|length }})</h3>
                <div class="image-grid">
                    {% for image in about_images %}
                        <div class="image-card">
                            <img src="{{ image.image_url }}" alt="{{ image.title }}" loading="lazy">
                            <div class="image-card-content">
                                <h3>{{ image.title }}</h3>
                                {% if image.description %}
                                    <p>{{ image.description }}</p>
                                {% endif %}
                                <p style="font-size: 12px; color: #64748b;">
                                    Uploaded: {{ image.upload_date.strftime('%m/%d/%Y') }}
                                </p>
                                <form method="POST" action="/admin/about-images/delete/{{ image.id }}" style="margin-top: 10px;" 
                                      onsubmit="return confirm('Are you sure you want to delete this image?')">
                                    <button type="submit" class="btn btn-danger">🗑️ Delete</button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div style="text-align: center; padding: 40px; color: #64748b;">
                    <p>No about images uploaded yet. Upload your first image above!</p>
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

