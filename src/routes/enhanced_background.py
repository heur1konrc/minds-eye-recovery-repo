"""
Enhanced Background Manager with Slideshow Support
Replaces the old background manager with slideshow functionality
"""

import os
import json
from flask import Blueprint, request, render_template_string, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import uuid
from ..config import PHOTOGRAPHY_ASSETS_DIR, LEGACY_ASSETS_DIR
from ..models import db, Image, SlideshowBackground, SlideshowSettings

enhanced_bg_bp = Blueprint('enhanced_background', __name__)

@enhanced_bg_bp.route('/admin/slideshow-background')
def slideshow_background_manager():
    """Enhanced slideshow background management page"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get current slideshow backgrounds
    slideshow_backgrounds = SlideshowBackground.query.join(Image)\
        .filter(SlideshowBackground.is_active == True)\
        .order_by(SlideshowBackground.display_order)\
        .all()
    
    # Get slideshow settings
    settings = SlideshowSettings.query.first()
    if not settings:
        settings = SlideshowSettings()
    
    # Get all portfolio images - sorted by capture date newest to oldest
    portfolio_images = Image.query.order_by(
        Image.upload_date.desc()
    ).all()
    
    # Get IDs of images already in slideshow
    slideshow_image_ids = [bg.image_id for bg in slideshow_backgrounds]
    
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
            .settings-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
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
            }
            .btn { 
                background: #ff6b35; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover { background: #e55a2b; }
            .btn-danger { background: #dc3545; }
            .btn-danger:hover { background: #c82333; }
            .slideshow-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .slideshow-item {
                background: #333;
                border-radius: 8px;
                overflow: hidden;
                position: relative;
            }
            .slideshow-item img {
                width: 100%;
                height: 150px;
                object-fit: cover;
            }
            .slideshow-item .info {
                padding: 10px;
            }
            .slideshow-item .info h4 {
                margin: 0 0 5px 0;
                color: #fff;
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
                gap: 20px;
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
            .portfolio-item .info h4 {
                margin: 0 0 5px 0;
                color: #fff;
                font-size: 14px;
            }
            .in-slideshow {
                opacity: 0.5;
                position: relative;
            }
            .in-slideshow::after {
                content: "IN SLIDESHOW";
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 107, 53, 0.9);
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            .preview-section {
                text-align: center;
                padding: 20px;
            }
            .preview-container {
                position: relative;
                max-width: 600px;
                height: 300px;
                margin: 0 auto;
                border-radius: 8px;
                overflow: hidden;
                background: #000;
            }
            .preview-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                position: absolute;
                opacity: 0;
                transition: opacity 1s ease-in-out;
            }
            .preview-image.active {
                opacity: 1;
            }
            .preview-controls {
                margin-top: 15px;
            }
            .preview-controls button {
                margin: 0 5px;
            }
        </style>
        <script>
            let previewInterval;
            let currentPreviewIndex = 0;
            
            function startPreview() {
                const images = document.querySelectorAll('.preview-image');
                if (images.length <= 1) return;
                
                const duration = parseInt(document.getElementById('transition_duration').value) || 5000;
                
                previewInterval = setInterval(() => {
                    images[currentPreviewIndex].classList.remove('active');
                    currentPreviewIndex = (currentPreviewIndex + 1) % images.length;
                    images[currentPreviewIndex].classList.add('active');
                }, duration);
            }
            
            function stopPreview() {
                if (previewInterval) {
                    clearInterval(previewInterval);
                    previewInterval = null;
                }
            }
            
            function updateSettings() {
                const formData = new FormData();
                formData.append('transition_duration', document.getElementById('transition_duration').value);
                formData.append('fade_duration', document.getElementById('fade_duration').value);
                formData.append('auto_play', document.getElementById('auto_play').checked);
                formData.append('pause_on_hover', document.getElementById('pause_on_hover').checked);
                
                fetch('/api/slideshow/settings', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Settings updated successfully!');
                    } else {
                        alert('Error updating settings: ' + data.error);
                    }
                });
            }
            
            function addToSlideshow(imageId) {
                fetch('/api/slideshow/backgrounds', {
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
                        alert('Error adding to slideshow: ' + data.error);
                    }
                });
            }
            
            function removeFromSlideshow(bgId) {
                if (confirm('Remove this image from slideshow?')) {
                    fetch('/api/slideshow/backgrounds/' + bgId, {
                        method: 'DELETE'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error removing from slideshow: ' + data.error);
                        }
                    });
                }
            }
        </script>
    </head>
    <body>
        <div class="header">
            <h1>🎬 Slideshow Background Manager</h1>
            <div class="nav-links">
                <a href="/admin/dashboard">← Back to Dashboard</a>
                <a href="/admin/logout">Logout</a>
            </div>
        </div>
        
        <!-- Slideshow Settings -->
        <div class="section">
            <h2>⚙️ Slideshow Settings</h2>
            <div class="settings-grid">
                <div class="form-group">
                    <label for="transition_duration">Transition Duration (seconds)</label>
                    <select id="transition_duration">
                        <option value="3000" {% if settings.transition_duration == 3000 %}selected{% endif %}>3 seconds</option>
                        <option value="5000" {% if settings.transition_duration == 5000 %}selected{% endif %}>5 seconds</option>
                        <option value="8000" {% if settings.transition_duration == 8000 %}selected{% endif %}>8 seconds</option>
                        <option value="10000" {% if settings.transition_duration == 10000 %}selected{% endif %}>10 seconds</option>
                        <option value="15000" {% if settings.transition_duration == 15000 %}selected{% endif %}>15 seconds</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="fade_duration">Fade Duration (milliseconds)</label>
                    <select id="fade_duration">
                        <option value="500" {% if settings.fade_duration == 500 %}selected{% endif %}>0.5 seconds</option>
                        <option value="1000" {% if settings.fade_duration == 1000 %}selected{% endif %}>1 second</option>
                        <option value="1500" {% if settings.fade_duration == 1500 %}selected{% endif %}>1.5 seconds</option>
                        <option value="2000" {% if settings.fade_duration == 2000 %}selected{% endif %}>2 seconds</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="auto_play" {% if settings.auto_play %}checked{% endif %}> Auto Play
                    </label>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="pause_on_hover" {% if settings.pause_on_hover %}checked{% endif %}> Pause on Hover
                    </label>
                </div>
            </div>
            <button class="btn" onclick="updateSettings()">💾 Update Settings</button>
        </div>
        
        <!-- Preview Section -->
        {% if slideshow_backgrounds %}
        <div class="section">
            <h2>👁️ Slideshow Preview</h2>
            <div class="preview-section">
                <div class="preview-container">
                    {% for bg in slideshow_backgrounds %}
                    <img src="/assets/{{ bg.image.filename }}" alt="{{ bg.image.title }}" 
                         class="preview-image {% if loop.first %}active{% endif %}">
                    {% endfor %}
                </div>
                <div class="preview-controls">
                    <button class="btn" onclick="startPreview()">▶️ Start Preview</button>
                    <button class="btn" onclick="stopPreview()">⏹️ Stop Preview</button>
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Current Slideshow -->
        <div class="section">
            <h2>🎬 Current Slideshow ({{ slideshow_backgrounds|length }} images)</h2>
            {% if slideshow_backgrounds %}
            <div class="slideshow-grid">
                {% for bg in slideshow_backgrounds %}
                <div class="slideshow-item">
                    <div class="order">{{ bg.display_order }}</div>
                    <img src="/assets/{{ bg.image.filename }}" alt="{{ bg.image.title }}">
                    <div class="info">
                        <h4>{{ bg.image.title }}</h4>
                        <button class="btn btn-danger" onclick="removeFromSlideshow({{ bg.id }})">
                            🗑️ Remove
                        </button>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p style="color: #999;">No images in slideshow. Add images from your portfolio below.</p>
            {% endif %}
        </div>
        
        <!-- Add from Portfolio -->
        <div class="section">
            <h2>📸 Add from Portfolio</h2>
            <p style="color: #999; margin-bottom: 20px;">Select images from your portfolio to add to the slideshow</p>
            
            <div class="portfolio-grid">
                {% for image in portfolio_images %}
                <div class="portfolio-item {% if image.id in slideshow_image_ids %}in-slideshow{% endif %}">
                    <img src="/assets/{{ image.filename }}" alt="{{ image.title }}">
                    <div class="info">
                        <h4>{{ image.title }}</h4>
                        {% if image.id not in slideshow_image_ids %}
                        <button class="btn" onclick="addToSlideshow('{{ image.id }}')">
                            ➕ Add to Slideshow
                        </button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, 
                                slideshow_backgrounds=slideshow_backgrounds,
                                settings=settings,
                                portfolio_images=portfolio_images,
                                slideshow_image_ids=slideshow_image_ids)

