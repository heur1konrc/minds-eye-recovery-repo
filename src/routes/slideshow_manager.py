"""
Enhanced Slideshow Background Manager
Allows multiple image selection, reordering, and timing controls
"""

import os
from flask import Blueprint, request, render_template_string, redirect, url_for, session, jsonify
from ..models import db, Image, SlideshowBackground, SlideshowSettings

slideshow_bp = Blueprint('slideshow_manager', __name__)

@slideshow_bp.route('/admin/slideshow-manager')
def slideshow_manager():
    """Enhanced slideshow background management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get current slideshow images
    slideshow_images = SlideshowBackground.query.join(Image)\
        .filter(SlideshowBackground.is_active == True)\
        .order_by(SlideshowBackground.display_order)\
        .all()
    
    # Get slideshow settings
    settings = SlideshowSettings.query.first()
    if not settings:
        # Create default settings
        settings = SlideshowSettings()
        db.session.add(settings)
        db.session.commit()
    
    # Get all portfolio images for selection - sorted by capture date newest to oldest
    portfolio_images = Image.query.order_by(
        Image.upload_date.desc()
    ).all()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Slideshow Background Manager - Mind's Eye Photography</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: #1a1a1a; 
                color: #fff; 
            }
            .header { 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 30px; 
                padding-bottom: 20px; 
                border-bottom: 2px solid #333; 
            }
            .header h1 { color: #ff6b35; margin: 0; }
            .nav-links { display: flex; gap: 15px; }
            .nav-links a { 
                color: #fff; 
                text-decoration: none; 
                padding: 8px 16px; 
                background: #333; 
                border-radius: 4px; 
            }
            .nav-links a:hover { background: #555; }
            .section { 
                background: #2a2a2a; 
                padding: 20px; 
                border-radius: 8px; 
                margin-bottom: 20px; 
            }
            .section h2 { color: #ff6b35; margin-top: 0; }
            .form-group { margin-bottom: 15px; }
            .form-group label { 
                display: block; 
                margin-bottom: 5px; 
                color: #ff6b35; 
                font-weight: bold; 
            }
            .form-group input, .form-group select { 
                width: 100%; 
                padding: 10px; 
                border: 1px solid #555; 
                border-radius: 4px; 
                background: #333; 
                color: #fff; 
                max-width: 300px;
            }
            button { 
                background: #ff6b35; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px; 
                margin-right: 10px;
            }
            button:hover { background: #e55a2b; }
            .btn-danger { background: #dc3545; }
            .btn-danger:hover { background: #c82333; }
            .btn-success { background: #28a745; }
            .btn-success:hover { background: #218838; }
            .current-slideshow { 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
                gap: 15px; 
                margin-top: 20px; 
            }
            .slideshow-item { 
                background: #333; 
                border-radius: 8px; 
                overflow: hidden; 
                position: relative;
                border: 2px solid #ff6b35;
            }
            .slideshow-item img { 
                width: 100%; 
                height: 150px; 
                object-fit: cover; 
            }
            .slideshow-item .info { 
                padding: 10px; 
            }
            .slideshow-item h4 { 
                margin: 0 0 5px 0; 
                color: #ff6b35; 
                font-size: 14px;
            }
            .slideshow-item .order { 
                position: absolute; 
                top: 5px; 
                left: 5px; 
                background: #ff6b35; 
                color: white; 
                padding: 2px 6px; 
                border-radius: 3px; 
                font-size: 12px; 
                font-weight: bold;
            }
            .portfolio-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
                gap: 15px; 
                margin-top: 20px; 
            }
            .portfolio-item { 
                background: #333; 
                border-radius: 8px; 
                overflow: hidden; 
                position: relative;
            }
            .portfolio-item img { 
                width: 100%; 
                height: 150px; 
                object-fit: cover; 
            }
            .portfolio-item .info { 
                padding: 10px; 
            }
            .portfolio-item h4 { 
                margin: 0 0 5px 0; 
                color: #ff6b35; 
                font-size: 14px;
            }
            .portfolio-item .categories {
                font-size: 12px;
                color: #999;
                margin-bottom: 10px;
            }
            .add-btn {
                background: #28a745;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
                width: 100%;
            }
            .add-btn:hover { background: #218838; }
            .add-btn:disabled { 
                background: #666; 
                cursor: not-allowed; 
            }
            .in-slideshow {
                position: absolute;
                top: 5px;
                right: 5px;
                background: #ff6b35;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            .settings-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            .preview-btn {
                background: #17a2b8;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
            }
            .preview-btn:hover { background: #138496; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎬 Slideshow Background Manager</h1>
            <div class="nav-links">
                <a href="/admin/dashboard">← Back to Dashboard</a>
                <a href="/admin/logout">Logout</a>
            </div>
        </div>
        
        <!-- Current Slideshow -->
        <div class="section">
            <h2>Current Slideshow ({{ slideshow_images|length }} images)</h2>
            {% if slideshow_images %}
                <div class="current-slideshow">
                    {% for bg in slideshow_images %}
                    <div class="slideshow-item">
                        <div class="order">{{ bg.display_order }}</div>
                        <img src="/static/assets/{{ bg.image.filename }}" alt="{{ bg.image.title }}">
                        <div class="info">
                            <h4>{{ bg.image.title }}</h4>
                            <form method="POST" action="/admin/slideshow-manager/remove" style="margin: 5px 0;">
                                <input type="hidden" name="slideshow_id" value="{{ bg.id }}">
                                <button type="submit" class="btn-danger" style="font-size: 12px; padding: 4px 8px;">Remove</button>
                            </form>
                            <form method="POST" action="/admin/slideshow-manager/reorder" style="margin: 5px 0;">
                                <input type="hidden" name="slideshow_id" value="{{ bg.id }}">
                                <input type="number" name="new_order" value="{{ bg.display_order }}" min="1" max="{{ slideshow_images|length }}" style="width: 60px; padding: 2px;">
                                <button type="submit" style="font-size: 12px; padding: 4px 8px;">Reorder</button>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                <button class="preview-btn" onclick="window.open('/', '_blank')">🎬 Preview Slideshow</button>
            {% else %}
                <p style="color: #999;">No images in slideshow. Add images from your portfolio below.</p>
            {% endif %}
        </div>
        
        <!-- Slideshow Settings -->
        <div class="section">
            <h2>Slideshow Settings</h2>
            <form method="POST" action="/admin/slideshow-manager/settings">
                <div class="settings-grid">
                    <div class="form-group">
                        <label for="transition_duration">Transition Duration (seconds)</label>
                        <select id="transition_duration" name="transition_duration">
                            <option value="3000" {% if settings.transition_duration == 3000 %}selected{% endif %}>3 seconds</option>
                            <option value="5000" {% if settings.transition_duration == 5000 %}selected{% endif %}>5 seconds</option>
                            <option value="7000" {% if settings.transition_duration == 7000 %}selected{% endif %}>7 seconds</option>
                            <option value="10000" {% if settings.transition_duration == 10000 %}selected{% endif %}>10 seconds</option>
                            <option value="15000" {% if settings.transition_duration == 15000 %}selected{% endif %}>15 seconds</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="fade_duration">Fade Duration (milliseconds)</label>
                        <select id="fade_duration" name="fade_duration">
                            <option value="500" {% if settings.fade_duration == 500 %}selected{% endif %}>0.5 seconds</option>
                            <option value="1000" {% if settings.fade_duration == 1000 %}selected{% endif %}>1 second</option>
                            <option value="1500" {% if settings.fade_duration == 1500 %}selected{% endif %}>1.5 seconds</option>
                            <option value="2000" {% if settings.fade_duration == 2000 %}selected{% endif %}>2 seconds</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="auto_play" {% if settings.auto_play %}checked{% endif %}> Auto Play
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="pause_on_hover" {% if settings.pause_on_hover %}checked{% endif %}> Pause on Hover
                        </label>
                    </div>
                </div>
                <button type="submit">Save Settings</button>
            </form>
        </div>
        
        <!-- Add Images to Slideshow -->
        <div class="section">
            <h2>Add Images to Slideshow</h2>
            <p style="color: #999; margin-bottom: 20px;">Select images from your portfolio to add to the slideshow rotation</p>
            
            <div class="portfolio-grid">
                {% for image in portfolio_images %}
                {% set in_slideshow = slideshow_images|selectattr('image_id', 'equalto', image.id)|list|length > 0 %}
                <div class="portfolio-item">
                    {% if in_slideshow %}
                    <div class="in-slideshow">IN SLIDESHOW</div>
                    {% endif %}
                    <img src="/static/assets/{{ image.filename }}" alt="{{ image.title }}">
                    <div class="info">
                        <h4>{{ image.title }}</h4>
                        <div class="categories">
                            {% for cat in image.categories %}
                                {{ cat.category.name }}{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </div>
                        <form method="POST" action="/admin/slideshow-manager/add" style="margin: 0;">
                            <input type="hidden" name="image_id" value="{{ image.id }}">
                            <button type="submit" class="add-btn" 
                                    {% if in_slideshow %}disabled{% endif %}>
                                {% if in_slideshow %}Already in Slideshow{% else %}Add to Slideshow{% endif %}
                            </button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, 
                                slideshow_images=slideshow_images, 
                                settings=settings, 
                                portfolio_images=portfolio_images)

@slideshow_bp.route('/admin/slideshow-manager/add', methods=['POST'])
def add_to_slideshow():
    """Add image to slideshow"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        image_id = request.form.get('image_id')
        
        # Check if already in slideshow
        existing = SlideshowBackground.query.filter_by(image_id=image_id, is_active=True).first()
        if existing:
            return redirect(url_for('slideshow_manager.slideshow_manager'))
        
        # Get next display order
        max_order = db.session.query(db.func.max(SlideshowBackground.display_order)).scalar() or 0
        
        # Add to slideshow
        slideshow_bg = SlideshowBackground(
            image_id=image_id,
            display_order=max_order + 1,
            is_active=True
        )
        db.session.add(slideshow_bg)
        db.session.commit()
        
        return redirect(url_for('slideshow_manager.slideshow_manager'))
        
    except Exception as e:
        print(f"❌ Error adding to slideshow: {e}")
        return redirect(url_for('slideshow_manager.slideshow_manager'))

@slideshow_bp.route('/admin/slideshow-manager/remove', methods=['POST'])
def remove_from_slideshow():
    """Remove image from slideshow"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        slideshow_id = request.form.get('slideshow_id')
        
        # Remove from slideshow
        slideshow_bg = SlideshowBackground.query.get(slideshow_id)
        if slideshow_bg:
            db.session.delete(slideshow_bg)
            db.session.commit()
        
        return redirect(url_for('slideshow_manager.slideshow_manager'))
        
    except Exception as e:
        print(f"❌ Error removing from slideshow: {e}")
        return redirect(url_for('slideshow_manager.slideshow_manager'))

@slideshow_bp.route('/admin/slideshow-manager/reorder', methods=['POST'])
def reorder_slideshow():
    """Reorder slideshow images"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        slideshow_id = request.form.get('slideshow_id')
        new_order = int(request.form.get('new_order'))
        
        # Update display order
        slideshow_bg = SlideshowBackground.query.get(slideshow_id)
        if slideshow_bg:
            slideshow_bg.display_order = new_order
            db.session.commit()
        
        return redirect(url_for('slideshow_manager.slideshow_manager'))
        
    except Exception as e:
        print(f"❌ Error reordering slideshow: {e}")
        return redirect(url_for('slideshow_manager.slideshow_manager'))

@slideshow_bp.route('/admin/slideshow-manager/settings', methods=['POST'])
def update_slideshow_settings():
    """Update slideshow settings"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    try:
        # Get or create settings
        settings = SlideshowSettings.query.first()
        if not settings:
            settings = SlideshowSettings()
            db.session.add(settings)
        
        # Update settings
        settings.transition_duration = int(request.form.get('transition_duration', 5000))
        settings.fade_duration = int(request.form.get('fade_duration', 1000))
        settings.auto_play = 'auto_play' in request.form
        settings.pause_on_hover = 'pause_on_hover' in request.form
        
        db.session.commit()
        
        return redirect(url_for('slideshow_manager.slideshow_manager'))
        
    except Exception as e:
        print(f"❌ Error updating slideshow settings: {e}")
        return redirect(url_for('slideshow_manager.slideshow_manager'))

# API Endpoints for Frontend
@slideshow_bp.route('/api/slideshow/backgrounds')
def get_slideshow_backgrounds():
    """API endpoint to get slideshow background images"""
    try:
        backgrounds = SlideshowBackground.query.join(Image)\
            .filter(SlideshowBackground.is_active == True)\
            .order_by(SlideshowBackground.display_order)\
            .all()
        
        background_data = []
        for bg in backgrounds:
            if bg.image:
                background_data.append({
                    'id': bg.id,
                    'filename': bg.image.filename,
                    'title': bg.image.title,
                    'url': f'https://minds-eye-master-production.up.railway.app/static/assets/{bg.image.filename}',
                    'display_order': bg.display_order
                })
        
        return jsonify({
            'success': True,
            'backgrounds': background_data
        })
        
    except Exception as e:
        print(f"❌ Error getting slideshow backgrounds: {e}")
        return jsonify({
            'success': False,
            'backgrounds': []
        })

@slideshow_bp.route('/api/slideshow/settings')
def get_slideshow_settings():
    """API endpoint to get slideshow settings"""
    try:
        settings = SlideshowSettings.query.first()
        if not settings:
            # Create default settings
            settings = SlideshowSettings()
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error getting slideshow settings: {e}")
        return jsonify({
            'success': False,
            'settings': {
                'transition_duration': 5000,
                'fade_duration': 1000,
                'auto_play': True,
                'pause_on_hover': True
            }
        })

