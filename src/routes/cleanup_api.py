"""
API endpoint to trigger database cleanup and optimization
"""

import re
from flask import Blueprint, jsonify
from ..models import db, Image

cleanup_bp = Blueprint('cleanup', __name__)

@cleanup_bp.route('/api/cleanup-database', methods=['GET'])
def cleanup_database():
    """API endpoint to clean up database titles and descriptions"""
    try:
        print('🔄 Starting database cleanup via API...')
        
        # Get all images
        images = Image.query.all()
        updated_count = 0
        
        for image in images:
            original_title = image.title
            original_description = image.description
            
            # Remove hex codes from title (pattern: space + 6-8 hex characters at end)
            if image.title:
                clean_title = re.sub(r'\s+[A-F0-9]{6,8}$', '', image.title, flags=re.IGNORECASE)
                image.title = clean_title.strip()
            
            # Remove 'Migrated from volume - ' prefix from description
            if image.description and image.description.startswith('Migrated from volume - '):
                image.description = image.description.replace('Migrated from volume - ', '').strip()
            
            # Check if anything changed
            if original_title != image.title or original_description != image.description:
                updated_count += 1
                print(f'✅ Updated: "{original_title}" -> "{image.title}"')
        
        # Commit changes
        db.session.commit()
        
        # Add database indexes for better performance (if they don't exist)
        try:
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_image_title ON image(title)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_image_upload_date ON image(upload_date)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_image_category_image_id ON image_category(image_id)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_image_category_category_id ON image_category(category_id)')
            optimized = True
        except Exception as e:
            print(f'Index optimization note: {e}')
            optimized = False
        
        print(f'🎉 Database cleanup complete! Updated {updated_count} images')
        
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'total_images': len(images),
            'optimized': optimized,
            'message': f'Successfully cleaned up {updated_count} images'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f'❌ Cleanup error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

