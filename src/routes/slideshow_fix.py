"""
New Simplified Slideshow Toggle API
Bypasses potential issues with the existing endpoint
"""

from flask import Blueprint, request, jsonify, session
from ..models import db, Image
from sqlalchemy import text
import traceback

slideshow_fix_bp = Blueprint('slideshow_fix', __name__)

@slideshow_fix_bp.route('/admin/slideshow-toggle-new', methods=['POST'])
def toggle_slideshow_new():
    """New simplified slideshow toggle with step-by-step validation"""
    
    # Step 1: Authentication
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Not authenticated', 'step': 'auth'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': f'Auth check failed: {str(e)}', 'step': 'auth'}), 500
    
    # Step 2: Get request data
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data', 'step': 'data'}), 400
        
        image_id = data.get('image_id')
        is_slideshow = data.get('is_slideshow')
        
        if image_id is None:
            return jsonify({'success': False, 'error': 'Missing image_id', 'step': 'data'}), 400
        if is_slideshow is None:
            return jsonify({'success': False, 'error': 'Missing is_slideshow', 'step': 'data'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Data parsing failed: {str(e)}', 'step': 'data'}), 500
    
    # Step 3: Convert data types
    try:
        # Don't convert image_id to int - it's a UUID string
        # image_id = int(image_id)  # This was causing the error!
        
        if isinstance(is_slideshow, str):
            is_slideshow = is_slideshow.lower() in ('true', '1', 'yes')
        else:
            is_slideshow = bool(is_slideshow)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Type conversion failed: {str(e)}', 'step': 'convert'}), 500
    
    # Step 4: Find image
    try:
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'success': False, 'error': f'Image {image_id} not found', 'step': 'find'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Image lookup failed: {str(e)}', 'step': 'find'}), 500
    
    # Step 5: Check slideshow limit if adding image
    if is_slideshow:
        try:
            current_count = db.session.execute(
                text("SELECT COUNT(*) FROM images WHERE is_slideshow_background = TRUE")
            ).fetchone()[0]
            
            if current_count >= 5:
                return jsonify({
                    'success': False, 
                    'error': f'Slideshow limit reached! You already have {current_count} images in slideshow. Maximum is 5. Please remove an image first.',
                    'step': 'limit_check'
                }), 400
                
        except Exception as e:
            # If count fails, continue anyway
            pass
    
    # Step 6: Check field exists using raw SQL
    try:
        # Test if field exists (use correct table name 'images')
        result = db.session.execute(
            text("SELECT id, is_slideshow_background FROM images WHERE id = :image_id LIMIT 1"),
            {'image_id': image_id}
        ).fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Image not found in raw query', 'step': 'field_check'}), 404
            
        current_status = result[1] if result[1] is not None else False
        
    except Exception as e:
        # Field might not exist, try to add it (use correct table name 'images')
        try:
            db.session.execute(
                text("ALTER TABLE images ADD COLUMN is_slideshow_background BOOLEAN DEFAULT FALSE")
            )
            db.session.commit()
            current_status = False
        except Exception as add_error:
            return jsonify({
                'success': False, 
                'error': f'Field check failed: {str(e)}, Add failed: {str(add_error)}', 
                'step': 'field_check'
            }), 500
    
    # Step 6: Update using raw SQL (use correct table name 'images')
    try:
        db.session.execute(
            text("UPDATE images SET is_slideshow_background = :status WHERE id = :image_id"),
            {'status': is_slideshow, 'image_id': image_id}
        )
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Update failed: {str(e)}', 'step': 'update'}), 500
    
    # Step 7: Get updated count (use correct table name 'images')
    try:
        count_result = db.session.execute(
            text("SELECT COUNT(*) FROM images WHERE is_slideshow_background = TRUE")
        ).fetchone()
        slideshow_count = count_result[0] if count_result else 0
        
    except Exception as e:
        slideshow_count = 0
    
    # Step 8: Return success
    return jsonify({
        'success': True,
        'message': f'Image {"added to" if is_slideshow else "removed from"} slideshow',
        'image_id': image_id,
        'old_status': current_status,
        'new_status': is_slideshow,
        'slideshow_count': slideshow_count,
        'step': 'complete'
    })

@slideshow_fix_bp.route('/admin/slideshow-debug', methods=['GET'])
def slideshow_debug():
    """Debug endpoint to check slideshow status"""
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Check table structure (use correct table name 'images')
        try:
            columns = db.session.execute(text("PRAGMA table_info(images)")).fetchall()
            column_info = [{'name': col[1], 'type': col[2], 'nullable': not col[3]} for col in columns]
        except:
            column_info = "Could not get column info"
        
        # Count slideshow images (use correct table name 'images')
        try:
            slideshow_count = db.session.execute(
                text("SELECT COUNT(*) FROM images WHERE is_slideshow_background = TRUE")
            ).fetchone()[0]
        except Exception as e:
            slideshow_count = f"Error: {str(e)}"
        
        # List all images (use correct table name 'images')
        try:
            all_images = db.session.execute(
                text("SELECT id, title, is_slideshow_background FROM images ORDER BY id")
            ).fetchall()
            image_list = [{'id': img[0], 'title': img[1], 'slideshow': img[2]} for img in all_images]
        except Exception as e:
            image_list = f"Error: {str(e)}"
        
        return jsonify({
            'columns': column_info,
            'slideshow_count': slideshow_count,
            'images': image_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

