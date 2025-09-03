from flask import Blueprint, jsonify, send_file, render_template_string, request, redirect, url_for, session
import os
import json
import tarfile
import shutil
import subprocess
from datetime import datetime
from src.models import db, Image, Category, ImageCategory, SystemConfig
from src.config import PHOTOGRAPHY_ASSETS_DIR
import tempfile

backup_system_bp = Blueprint('backup_system', __name__)

# Emergency backup routes - NO ADMIN LOGIN REQUIRED for disaster recovery
@backup_system_bp.route('/emergency-backup')
def emergency_backup_portal():
    """Emergency backup portal - accessible even if admin is broken"""
    return render_template_string(emergency_backup_html)

@backup_system_bp.route('/emergency-backup/download')
def emergency_backup_download():
    """Emergency backup download - NO LOGIN REQUIRED"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"emergency_backup_{timestamp}"
        
        # Create temporary directory for backup
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = os.path.join(temp_dir, backup_name)
            os.makedirs(backup_dir)
            
            # Emergency backup - just essentials
            # 1. Database file
            db_file = os.path.join(PHOTOGRAPHY_ASSETS_DIR, 'mindseye.db')
            if os.path.exists(db_file):
                shutil.copy2(db_file, backup_dir)
            
            # 2. All images
            if os.path.exists(PHOTOGRAPHY_ASSETS_DIR):
                for file in os.listdir(PHOTOGRAPHY_ASSETS_DIR):
                    file_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, file)
                    if os.path.isfile(file_path) and not file.endswith('.db'):
                        shutil.copy2(file_path, backup_dir)
            
            # 3. Emergency restore instructions
            emergency_instructions = create_emergency_restore_instructions()
            with open(os.path.join(backup_dir, 'EMERGENCY_RESTORE.txt'), 'w') as f:
                f.write(emergency_instructions)
            
            # 4. Create TAR.GZ file
            tar_path = os.path.join(temp_dir, f"{backup_name}.tar.gz")
            with tarfile.open(tar_path, 'w:gz') as tar:
                # Add each item in backup_dir individually to avoid path issues
                for item in os.listdir(backup_dir):
                    item_path = os.path.join(backup_dir, item)
                    tar.add(item_path, arcname=item)
            
            # Return the TAR.GZ file for download
            return send_file(tar_path, 
                           as_attachment=True, 
                           download_name=f"{backup_name}.tar.gz",
                           mimetype='application/gzip')
    
    except Exception as e:
        return f"Emergency backup failed: {str(e)}", 500

@backup_system_bp.route('/emergency-restore-guide')
def emergency_restore_guide():
    """Emergency restore guide - accessible without login"""
    instructions = create_emergency_restore_instructions()
    return render_template_string(emergency_restore_guide_html, instructions=instructions)

@backup_system_bp.route('/admin/backup-system')
def backup_system_dashboard():
    """Backup system management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get system status
    image_count = Image.query.count()
    category_count = Category.query.count()
    
    # Check volume usage
    volume_files = []
    volume_size = 0
    if os.path.exists(PHOTOGRAPHY_ASSETS_DIR):
        for file in os.listdir(PHOTOGRAPHY_ASSETS_DIR):
            file_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                volume_size += size
                volume_files.append({
                    'name': file,
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                })
    
    # Format volume size
    volume_size_mb = round(volume_size / (1024 * 1024), 2)
    
    return render_template_string(backup_dashboard_html,
                                image_count=image_count,
                                category_count=category_count,
                                volume_files_count=len(volume_files),
                                volume_size_mb=volume_size_mb,
                                message=request.args.get('message'),
                                message_type=request.args.get('message_type', 'success'))

@backup_system_bp.route('/admin/backup/create-manual', methods=['POST'])
def create_manual_backup():
    """Create COMPLETE backup (GitHub source code + Railway volume data)"""
    try:
        # Get custom backup name from form
        custom_name = request.form.get('backup_name', '').strip()
        if not custom_name:
            return redirect(url_for('backup_system.backup_system_dashboard') + '?message=Backup name is required&message_type=error')
        
        # Sanitize filename
        import re
        custom_name = re.sub(r'[^\w\-_\.]', '_', custom_name)
        if not custom_name.endswith('.tar.gz'):
            if custom_name.endswith('.tar') or custom_name.endswith('.gz'):
                custom_name = custom_name.rsplit('.', 1)[0] + '.tar.gz'
            else:
                custom_name = custom_name + '.tar.gz'
        
        backup_name = custom_name.replace('.tar.gz', '')
        
        # Create temporary directory for backup
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = os.path.join(temp_dir, backup_name)
            os.makedirs(backup_dir)
            
            # STEP 1: CLONE ACTUAL DEPLOYED SOURCE CODE FROM GITHUB
            github_repo_path = os.path.join(temp_dir, 'github_source')
            source_files_count = 0
            
            try:
                # Clone with timeout and better error handling
                result = subprocess.run([
                    'git', 'clone', 
                    'https://github.com/heur1konrc/minds-eye-recovery-repo.git', 
                    github_repo_path
                ], check=True, capture_output=True, text=True, timeout=300)
                
                # Verify clone was successful
                if not os.path.exists(github_repo_path) or not os.path.exists(os.path.join(github_repo_path, '.git')):
                    raise Exception("GitHub repository clone verification failed")
                
                # Create source code directory in backup
                source_backup_dir = os.path.join(backup_dir, 'DEPLOYED_SOURCE_CODE')
                os.makedirs(source_backup_dir)
                
                # Copy all source code files (excluding .git)
                for item in os.listdir(github_repo_path):
                    if item != '.git':
                        source_path = os.path.join(github_repo_path, item)
                        dest_path = os.path.join(source_backup_dir, item)
                        
                        if os.path.isdir(source_path):
                            shutil.copytree(source_path, dest_path, 
                                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules', '.git'))
                            for root, dirs, files in os.walk(dest_path):
                                source_files_count += len(files)
                        else:
                            shutil.copy2(source_path, dest_path)
                            source_files_count += 1
                            
            except subprocess.TimeoutExpired:
                return redirect(url_for('backup_system.backup_system_dashboard') + 
                              '?message=GitHub clone timeout - repository too large&message_type=error')
            except subprocess.CalledProcessError as e:
                error_msg = f"Git clone failed: {e.stderr if e.stderr else str(e)}"
                return redirect(url_for('backup_system.backup_system_dashboard') + 
                              f'?message={error_msg}&message_type=error')
            except Exception as e:
                return redirect(url_for('backup_system.backup_system_dashboard') + 
                              f'?message=Source code backup failed: {str(e)}&message_type=error')
            
            # STEP 2: BACKUP RAILWAY VOLUME DATA
            railway_data_dir = PHOTOGRAPHY_ASSETS_DIR  # This is /data
            data_files_count = 0
            
            if os.path.exists(railway_data_dir):
                # Create Railway data directory in backup
                data_backup_dir = os.path.join(backup_dir, 'RAILWAY_VOLUME_DATA')
                os.makedirs(data_backup_dir)
                
                # Copy all files from Railway volume
                for file in os.listdir(railway_data_dir):
                    source_path = os.path.join(railway_data_dir, file)
                    dest_path = os.path.join(data_backup_dir, file)
                    
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, dest_path)
                        data_files_count += 1
            
            # STEP 3: CREATE BACKUP INFO
            backup_info = f"""
🎯 COMPLETE DEPLOYED BACKUP CREATED: {datetime.now()}
Backup Name: {custom_name}

🚀 DEPLOYED SOURCE CODE: ✅ {source_files_count} files
   - FROM: GitHub Repository (heur1konrc/minds-eye-recovery-repo)
   - INCLUDES: Backend Python code, Frontend React code, Configuration files
   - THIS IS THE ACTUAL DEPLOYED SOURCE CODE

🚂 RAILWAY VOLUME DATA: ✅ {data_files_count} files
   - FROM: Railway Volume ({railway_data_dir})
   - INCLUDES: Database (mindseye.db) and all images
   - THIS IS THE ACTUAL DEPLOYED DATA

This backup contains the REAL deployed application:
- Source code that Railway deploys from GitHub
- Data that Railway stores in the volume
            """
            
            with open(os.path.join(backup_dir, 'DEPLOYED_BACKUP_INFO.txt'), 'w') as f:
                f.write(backup_info)
            
            # STEP 4: CREATE TAR.GZ FILE WITH BETTER ERROR HANDLING
            tar_path = os.path.join(temp_dir, custom_name)
            
            try:
                # Create tar file with compression
                with tarfile.open(tar_path, 'w:gz', compresslevel=6) as tar:
                    # Add source code directory
                    if os.path.exists(os.path.join(backup_dir, 'DEPLOYED_SOURCE_CODE')):
                        tar.add(os.path.join(backup_dir, 'DEPLOYED_SOURCE_CODE'), 
                               arcname='DEPLOYED_SOURCE_CODE')
                    
                    # Add Railway data directory  
                    if os.path.exists(os.path.join(backup_dir, 'RAILWAY_VOLUME_DATA')):
                        tar.add(os.path.join(backup_dir, 'RAILWAY_VOLUME_DATA'), 
                               arcname='RAILWAY_VOLUME_DATA')
                    
                    # Add backup info file
                    if os.path.exists(os.path.join(backup_dir, 'DEPLOYED_BACKUP_INFO.txt')):
                        tar.add(os.path.join(backup_dir, 'DEPLOYED_BACKUP_INFO.txt'), 
                               arcname='DEPLOYED_BACKUP_INFO.txt')
                
                # Verify tar file was created successfully
                if not os.path.exists(tar_path) or os.path.getsize(tar_path) == 0:
                    raise Exception("Tar file creation failed or file is empty")
                
                # Return the backup file for download
                from flask import send_file
                return send_file(tar_path, 
                               as_attachment=True, 
                               download_name=custom_name,
                               mimetype='application/gzip')
                               
            except Exception as tar_error:
                raise Exception(f"Tar file creation failed: {str(tar_error)}")
    
    except Exception as e:
        return redirect(url_for('backup_system.backup_system_dashboard') + 
                       f'?message=Backup failed: {str(e)}&message_type=error')
@backup_system_bp.route('/admin/backup/github-push', methods=['POST'])
def github_backup_push():
    """Push current state to GitHub with backup tag"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag_name = f"backup-{timestamp}"
        
        # Get current directory (should be project root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Git commands
        commands = [
            ['git', 'add', '.'],
            ['git', 'commit', '-m', f'🛡️ BACKUP: Automated backup {timestamp}', '--allow-empty'],
            ['git', 'tag', tag_name],
            ['git', 'push', 'origin', 'main', '--tags']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Git command failed: {' '.join(cmd)}\n{result.stderr}")
        
        return redirect(url_for('backup_system.backup_system_dashboard',
                              message=f"GitHub backup created successfully! Tag: {tag_name}",
                              message_type='success'))
    
    except Exception as e:
        return redirect(url_for('backup_system.backup_system_dashboard',
                              message=f"GitHub backup failed: {str(e)}",
                              message_type='error'))

@backup_system_bp.route('/admin/backup/restore-guide')
def restore_guide():
    """Display restore instructions"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    instructions = create_restore_instructions()
    return render_template_string(restore_guide_html, instructions=instructions)

def get_directory_size(directory):
    """Calculate total size of directory"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

def create_restore_instructions():
    """Create comprehensive restore instructions"""
    return """# Mind's Eye Photography - Disaster Recovery Guide

## 🚨 EMERGENCY RESTORE PROCEDURES

### SCENARIO 1: Complete System Restore from Backup TAR.GZ

1. **Download your backup TAR.GZ file** (from manual backup)
2. **Extract the TAR.GZ file** to a temporary location
3. **Stop the current application** (if running)

#### Restore Database:
```bash
# Copy database file
cp backup_folder/database/mindseye.db /data/mindseye.db

# Or restore from JSON data
# Use the backup_data.json file to recreate database
```

#### Restore Images:
```bash
# Copy all images to volume
cp backup_folder/images/* /data/
```

#### Restore Source Code:
```bash
# Replace current source with backup
rm -rf src/
cp -r backup_folder/source_code/src ./
```

### SCENARIO 2: Restore from GitHub Backup

1. **Find your backup tag** in GitHub repository
2. **Clone or checkout the backup tag**:
```bash
git clone https://github.com/your-repo/Minds-eye-master.git
cd Minds-eye-master
git checkout backup-YYYYMMDD_HHMMSS
```

3. **Deploy to Railway** using the backup version

### SCENARIO 3: Database-Only Recovery

If only database is corrupted but images are safe:

1. **Use backup_data.json** from your backup
2. **Run database restore script**:
```python
# Import backup data and recreate database
python restore_database.py backup_data.json
```

### SCENARIO 4: Images-Only Recovery

If database is fine but images are lost:

1. **Copy images from backup**:
```bash
cp backup_folder/images/* /data/
```

2. **Run image migration**:
```bash
# Access admin panel and use force migration
/debug/force-migration
```

## 🛡️ PREVENTION TIPS

- **Regular backups**: Use manual backup weekly
- **GitHub backups**: Push backup tags monthly  
- **Test restores**: Verify backup integrity quarterly
- **Monitor volume**: Check `/data` directory regularly

## 📞 EMERGENCY CONTACTS

- **Railway Support**: For volume/deployment issues
- **GitHub Support**: For repository problems
- **Backup Location**: Store backups in multiple locations

## ⚡ QUICK RECOVERY CHECKLIST

- [ ] Identify what was lost (database, images, code)
- [ ] Locate most recent backup
- [ ] Stop current application
- [ ] Restore from backup
- [ ] Test functionality
- [ ] Create new backup after recovery

**Remember: Your backups are only as good as your last test restore!**
"""

# HTML Templates
backup_dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Backup System - Mind's Eye Photography</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .backup-section { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .status-card { background: #3d3d3d; padding: 15px; border-radius: 8px; text-align: center; }
        .status-number { font-size: 2em; font-weight: bold; color: #4CAF50; }
        .backup-btn { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; font-size: 16px; }
        .backup-btn:hover { background: #45a049; }
        .github-btn { background: #333; }
        .github-btn:hover { background: #555; }
        .restore-btn { background: #ff9800; }
        .restore-btn:hover { background: #e68900; }
        .danger-btn { background: #f44336; }
        .danger-btn:hover { background: #da190b; }
        .message { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #4CAF50; }
        .error { background: #f44336; }
        .nav-link { color: #4CAF50; text-decoration: none; margin-right: 20px; }
        .nav-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Backup System - Mind's Eye Photography</h1>
            <nav>
                <a href="/admin/dashboard" class="nav-link">← Back to Admin Dashboard</a>
                <a href="/admin/backup/restore-guide" class="nav-link">📋 Restore Guide</a>
            </nav>
        </div>

        {% if message %}
        <div class="message {{ message_type }}">
            {{ message }}
        </div>
        {% endif %}

        <div class="backup-section">
            <h2>📊 System Status</h2>
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-number">{{ image_count }}</div>
                    <div>Images in Database</div>
                </div>
                <div class="status-card">
                    <div class="status-number">{{ category_count }}</div>
                    <div>Categories</div>
                </div>
                <div class="status-card">
                    <div class="status-number">{{ volume_files_count }}</div>
                    <div>Files in Volume</div>
                </div>
                <div class="status-card">
                    <div class="status-number">{{ volume_size_mb }}</div>
                    <div>Volume Size (MB)</div>
                </div>
            </div>
        </div>

        <div class="backup-section">
            <h2>💾 Manual Backup</h2>
            <p>Create a complete backup including images, database, and source code.</p>
            <form method="POST" action="/admin/backup/create-manual">
                <div style="margin-bottom: 15px;">
                    <label for="backup_name" style="display: block; margin-bottom: 5px; color: #4CAF50; font-weight: bold;">Custom Backup Name:</label>
                    <input type="text" 
                           id="backup_name" 
                           name="backup_name" 
                           placeholder="Enter backup name (e.g., before_website_update)" 
                           style="width: 100%; max-width: 400px; padding: 8px; border: 1px solid #555; border-radius: 4px; background: #3d3d3d; color: #fff; font-size: 14px;"
                           required>
                    <small style="color: #888; display: block; margin-top: 5px;">Will be saved as: your_name.tar.gz</small>
                </div>
                <button type="submit" class="backup-btn">📥 Create Complete Backup</button>
            </form>
            <small>Downloads a TAR.GZ file with everything needed for disaster recovery.</small>
        </div>

        <div class="backup-section">
            <h2>🔄 GitHub Backup</h2>
            <p>Push current state to GitHub repository with backup tag.</p>
            <form method="POST" action="/admin/backup/github-push">
                <button type="submit" class="backup-btn github-btn">📤 Push to GitHub</button>
            </form>
            <small>Creates a tagged backup in your GitHub repository.</small>
        </div>

        <div class="backup-section">
            <h2>🚨 Disaster Recovery</h2>
            <p>Emergency restore procedures and instructions.</p>
            <a href="/admin/backup/restore-guide" class="backup-btn restore-btn">📋 View Restore Guide</a>
            <small>Step-by-step instructions for emergency recovery.</small>
        </div>

        <div class="backup-section">
            <h2>⚙️ Advanced Options</h2>
            <p>Debug and maintenance tools.</p>
            <a href="/debug/volume-info" class="backup-btn">🔍 Volume Info</a>
            <a href="/debug/database-info" class="backup-btn">📊 Database Info</a>
            <a href="/debug/force-migration" class="backup-btn">🔄 Force Migration</a>
        </div>
    </div>
</body>
</html>
'''

restore_guide_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Restore Guide - Mind's Eye Photography</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; line-height: 1.6; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .content { background: #2d2d2d; padding: 20px; border-radius: 8px; }
        pre { background: #1a1a1a; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #3d3d3d; padding: 2px 5px; border-radius: 3px; }
        h1, h2, h3 { color: #4CAF50; }
        .nav-link { color: #4CAF50; text-decoration: none; margin-right: 20px; }
        .nav-link:hover { text-decoration: underline; }
        .warning { background: #ff9800; color: #000; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .danger { background: #f44336; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Disaster Recovery Guide</h1>
            <nav>
                <a href="/admin/backup-system" class="nav-link">← Back to Backup System</a>
                <a href="/admin/dashboard" class="nav-link">🏠 Admin Dashboard</a>
            </nav>
        </div>

        <div class="content">
            <div class="danger">
                <strong>⚠️ EMERGENCY USE ONLY:</strong> These procedures should only be used in case of data loss or system failure.
            </div>
            
            <pre>{{ instructions }}</pre>
        </div>
    </div>
</body>
</html>
'''


def create_emergency_restore_instructions():
    """Create emergency restore instructions for offline use"""
    return """
🚨 EMERGENCY RESTORE INSTRUCTIONS - Mind's Eye Photography 🚨

CRITICAL: These instructions work even if the website is completely down!

=== SCENARIO 1: COMPLETE SYSTEM FAILURE ===

1. STOP EVERYTHING
   - Don't panic, your data is safe in this backup
   - Stop any running applications

2. RESTORE DATABASE:
   Railway Volume Method:
   - Upload mindseye.db to your Railway volume at /data/mindseye.db
   - Or use Railway CLI: railway volume mount, then copy file

3. RESTORE IMAGES:
   - Upload all image files to Railway volume at /data/
   - Ensure file permissions are correct

4. REDEPLOY APPLICATION:
   - Push any working version to GitHub
   - Railway will automatically redeploy
   - Database and images will be restored

=== SCENARIO 2: ADMIN BROKEN BUT SITE RUNNING ===

1. ACCESS EMERGENCY BACKUP:
   - Go to: https://your-site.railway.app/emergency-backup
   - Download fresh backup
   - This works without admin login!

2. USE FORCE MIGRATION:
   - Go to: https://your-site.railway.app/debug/force-migration
   - This recreates database records from volume files

=== SCENARIO 3: DATABASE CORRUPTED ===

1. REPLACE DATABASE FILE:
   - Use mindseye.db from this backup
   - Upload to /data/mindseye.db in Railway volume

2. RESTART APPLICATION:
   - Push any change to trigger redeploy
   - Database will be restored with all your images

=== RAILWAY VOLUME ACCESS ===

Method 1 - Railway CLI:
```
railway login
railway link [your-project-id]
railway volume mount
# Copy files to mounted directory
```

Method 2 - Railway Dashboard:
- Go to Railway dashboard
- Select your project
- Go to Variables tab
- Add temporary file upload route

=== EMERGENCY CONTACTS ===

- Railway Support: help@railway.app
- GitHub Support: support@github.com
- Emergency Backup URL: /emergency-backup (no login required)

=== PREVENTION ===

- Download backup weekly using /emergency-backup
- Test restore procedures monthly
- Keep backup files in multiple locations
- Document your Railway project details

=== QUICK CHECKLIST ===

□ Stop broken application
□ Identify what's corrupted (database/images/code)
□ Restore from backup files
□ Test functionality
□ Create new backup immediately

Remember: This backup contains everything needed to restore your photography business!

Last Updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Emergency HTML Templates
emergency_backup_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚨 Emergency Backup - Mind's Eye Photography</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 800px; margin: 0 auto; }
        .emergency-header { background: #f44336; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .emergency-section { background: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .emergency-btn { background: #f44336; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; font-size: 18px; text-decoration: none; display: inline-block; }
        .emergency-btn:hover { background: #da190b; }
        .guide-btn { background: #ff9800; }
        .guide-btn:hover { background: #e68900; }
        .warning { background: #ff9800; color: #000; padding: 15px; border-radius: 5px; margin: 15px 0; font-weight: bold; }
        .info { background: #2196F3; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="emergency-header">
            <h1>🚨 EMERGENCY BACKUP PORTAL</h1>
            <p>This page works even if the admin system is broken!</p>
        </div>

        <div class="warning">
            ⚠️ WARNING: This is for emergency use only. Use this if the main admin system is not working.
        </div>

        <div class="emergency-section">
            <h2>📥 Emergency Backup</h2>
            <p>Download a complete backup of your images and database. No login required!</p>
            <a href="/emergency-backup/download" class="emergency-btn">📥 Download Emergency Backup</a>
            <p><small>Downloads: Database file + All images + Restore instructions</small></p>
        </div>

        <div class="emergency-section">
            <h2>📋 Emergency Restore Guide</h2>
            <p>Step-by-step instructions for disaster recovery.</p>
            <a href="/emergency-restore-guide" class="emergency-btn guide-btn">📋 View Restore Guide</a>
            <p><small>Works offline - save this page for emergencies!</small></p>
        </div>

        <div class="info">
            <h3>🔗 Emergency URLs (bookmark these!):</h3>
            <ul>
                <li><strong>Emergency Backup:</strong> /emergency-backup</li>
                <li><strong>Emergency Download:</strong> /emergency-backup/download</li>
                <li><strong>Restore Guide:</strong> /emergency-restore-guide</li>
                <li><strong>Force Migration:</strong> /debug/force-migration</li>
                <li><strong>Volume Info:</strong> /debug/volume-info</li>
            </ul>
        </div>

        <div class="emergency-section">
            <h2>🏠 Return to Normal Operations</h2>
            <p>If the admin system is working, use the regular backup system:</p>
            <a href="/admin/dashboard" class="emergency-btn" style="background: #4CAF50;">🏠 Admin Dashboard</a>
            <a href="/admin/backup-system" class="emergency-btn" style="background: #4CAF50;">🛡️ Backup System</a>
        </div>
    </div>
</body>
</html>
'''

emergency_restore_guide_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚨 Emergency Restore Guide - Mind's Eye Photography</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; line-height: 1.6; }
        .container { max-width: 1000px; margin: 0 auto; }
        .emergency-header { background: #f44336; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .content { background: #2d2d2d; padding: 20px; border-radius: 8px; }
        pre { background: #1a1a1a; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; }
        .emergency-btn { background: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; text-decoration: none; display: inline-block; }
        .emergency-btn:hover { background: #da190b; }
        .warning { background: #ff9800; color: #000; padding: 15px; border-radius: 5px; margin: 15px 0; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="emergency-header">
            <h1>🚨 EMERGENCY RESTORE GUIDE</h1>
            <p>Save this page offline for disaster recovery!</p>
        </div>

        <div class="warning">
            ⚠️ EMERGENCY USE ONLY: These procedures are for when normal admin access is not available.
        </div>

        <div class="content">
            <a href="/emergency-backup" class="emergency-btn">← Back to Emergency Portal</a>
            <a href="/emergency-backup/download" class="emergency-btn">📥 Download Backup</a>
            
            <pre>{{ instructions }}</pre>
        </div>
    </div>
</body>
</html>
'''

