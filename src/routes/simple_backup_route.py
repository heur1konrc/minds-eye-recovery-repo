"""
Simple backup route that actually works
"""

from flask import Blueprint, send_file, jsonify
import os
import shutil
import tarfile
import tempfile
from datetime import datetime

simple_backup_bp = Blueprint('simple_backup', __name__)

@simple_backup_bp.route('/simple-backup/download')
def simple_backup_download():
    """Simple backup that actually works"""
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"working_backup_{timestamp}"
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        backup_dir = os.path.join(temp_dir, backup_name)
        os.makedirs(backup_dir)
        
        # Copy database file
        db_source = "/data/mindseye.db"
        if os.path.exists(db_source):
            shutil.copy2(db_source, backup_dir)
        
        # Copy all image files
        data_dir = "/data"
        image_count = 0
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    source_path = os.path.join(data_dir, file)
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, backup_dir)
                        image_count += 1
        
        # Create backup info
        info_content = f"""WORKING BACKUP CREATED: {datetime.now()}
Database: {'✅ Included' if os.path.exists(db_source) else '❌ Not found'}
Images: {image_count} files
"""
        with open(os.path.join(backup_dir, "backup_info.txt"), 'w') as f:
            f.write(info_content)
        
        # Create tar.gz file
        tar_path = os.path.join(temp_dir, f"{backup_name}.tar.gz")
        
        with tarfile.open(tar_path, 'w:gz') as tar:
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                tar.add(item_path, arcname=item)
        
        # Return the file
        return send_file(tar_path, 
                        as_attachment=True, 
                        download_name=f"{backup_name}.tar.gz",
                        mimetype='application/gzip')
        
    except Exception as e:
        return jsonify({'error': f'Backup failed: {str(e)}'}), 500

@simple_backup_bp.route('/simple-backup')
def simple_backup_page():
    """Simple backup page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Working Backup System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: white; }
            .container { max-width: 600px; margin: 0 auto; }
            .button { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
            .button:hover { background: #45a049; }
            .warning { background: #ff4444; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 WORKING BACKUP SYSTEM</h1>
            
            <div class="warning">
                <strong>⚠️ EMERGENCY BACKUP</strong><br>
                This is a replacement for the broken backup system.
            </div>
            
            <h2>📥 Download Working Backup</h2>
            <p>This backup includes:</p>
            <ul>
                <li>✅ Database file (mindseye.db)</li>
                <li>✅ All image files</li>
                <li>✅ Backup information</li>
            </ul>
            
            <a href="/simple-backup/download" class="button">📥 Download Working Backup</a>
            
            <h2>📋 What's Included</h2>
            <p>The backup contains everything needed to restore your site:</p>
            <ul>
                <li><strong>mindseye.db</strong> - Complete database with all image metadata</li>
                <li><strong>Image files</strong> - All your photography images</li>
                <li><strong>backup_info.txt</strong> - Information about the backup</li>
            </ul>
            
            <p><a href="/admin">← Back to Admin</a></p>
        </div>
    </body>
    </html>
    """
    return html

