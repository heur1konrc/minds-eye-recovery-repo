from flask import Blueprint, jsonify
from src.models import db, Image, Category, migrate_existing_images
import os
from src.config import PHOTOGRAPHY_ASSETS_DIR

debug_migration_bp = Blueprint('debug_migration', __name__)

@debug_migration_bp.route('/debug/force-migration')
def force_migration():
    """Force run migration and show detailed debug info"""
    
    # Get current state
    image_count_before = Image.query.count()
    category_count = Category.query.count()
    
    # Check volume files
    volume_files = []
    if os.path.exists(PHOTOGRAPHY_ASSETS_DIR):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        for file in os.listdir(PHOTOGRAPHY_ASSETS_DIR):
            file_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file.lower())
                if ext in image_extensions:
                    volume_files.append(file)
    
    # Force run migration
    try:
        migrate_existing_images()
        migration_success = True
        migration_error = None
    except Exception as e:
        migration_success = False
        migration_error = str(e)
    
    # Get state after migration
    image_count_after = Image.query.count()
    
    # Get sample of migrated images
    sample_images = []
    for image in Image.query.limit(5).all():
        sample_images.append({
            'id': image.id,
            'filename': image.filename,
            'title': image.title,
            'categories': [cat.category.name for cat in image.categories]
        })
    
    return jsonify({
        'volume_directory': PHOTOGRAPHY_ASSETS_DIR,
        'volume_files_count': len(volume_files),
        'volume_files': volume_files[:10],  # First 10 files
        'categories_available': category_count,
        'images_before_migration': image_count_before,
        'images_after_migration': image_count_after,
        'migration_success': migration_success,
        'migration_error': migration_error,
        'sample_migrated_images': sample_images,
        'images_created': image_count_after - image_count_before
    })

@debug_migration_bp.route('/debug/clear-images')
def clear_images():
    """Clear all image records (for testing)"""
    try:
        # Delete all image-category relationships first
        from src.models import ImageCategory
        ImageCategory.query.delete()
        
        # Delete all images
        Image.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All image records cleared',
            'remaining_images': Image.query.count()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        })

