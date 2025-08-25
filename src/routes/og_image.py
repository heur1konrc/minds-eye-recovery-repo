"""
Open Graph Image endpoint for social media sharing
Serves the current featured image for social media previews
"""
import os
from flask import Blueprint, send_file, abort
from ..models import Image

og_bp = Blueprint('og', __name__)

@og_bp.route('/api/featured-image-og')
def featured_image_og():
    """Serve the current featured image for Open Graph social media sharing"""
    try:
        # Get the current featured image from database
        featured_image = Image.query.filter_by(is_featured=True).first()
        
        if not featured_image:
            # If no featured image, return a default image or 404
            abort(404)
        
        # Construct the image path
        from ..config import PHOTOGRAPHY_ASSETS_DIR
        image_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, featured_image.filename)
        
        # Check if file exists in photography assets
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg')
        
        # Try static assets as fallback
        static_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', featured_image.filename)
        if os.path.exists(static_path):
            return send_file(static_path, mimetype='image/jpeg')
        
        # If image file not found, return 404
        abort(404)
        
    except Exception as e:
        print(f"Error serving OG image: {e}")
        abort(404)

