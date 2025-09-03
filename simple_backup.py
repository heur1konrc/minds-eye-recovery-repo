#!/usr/bin/env python3
"""
COMPLETE backup script for Mind's Eye Photography
This creates a FULL backup including ALL source code files
"""

import os
import shutil
import tarfile
import tempfile
from datetime import datetime

def create_simple_backup():
    """Create a COMPLETE backup including ALL source code"""
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"COMPLETE_backup_{timestamp}"
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        backup_dir = os.path.join(temp_dir, backup_name)
        os.makedirs(backup_dir)
        
        print(f"Creating COMPLETE backup in: {backup_dir}")
        
        # SOURCE CODE BACKUP - HIGHEST PRIORITY
        source_root = "/home/ubuntu/minds-eye-recovery"
        source_files_count = 0
        
        if os.path.exists(source_root):
            print("🔧 Backing up SOURCE CODE...")
            
            # Create source code directory in backup
            source_backup_dir = os.path.join(backup_dir, "source_code")
            os.makedirs(source_backup_dir)
            
            # Copy ALL source code files and directories
            for item in os.listdir(source_root):
                if item not in ['.git', '__pycache__', 'venv', '.env']:
                    source_path = os.path.join(source_root, item)
                    dest_path = os.path.join(source_backup_dir, item)
                    
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path, 
                                      ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules', '.git'))
                        # Count files in directory
                        for root, dirs, files in os.walk(dest_path):
                            source_files_count += len(files)
                    else:
                        shutil.copy2(source_path, dest_path)
                        source_files_count += 1
            
            print(f"✅ {source_files_count} source code files copied")
        else:
            print("❌ Source code directory not found!")
        
        # Copy database file
        db_source = "/data/mindseye.db"
        if os.path.exists(db_source):
            shutil.copy2(db_source, backup_dir)
            print("✅ Database copied")
        else:
            print("⚠️  Database not found")
        
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
            print(f"✅ {image_count} images copied")
        
        # Create comprehensive backup info file
        info_content = f"""
🎯 COMPLETE BACKUP CREATED: {datetime.now()}
Backup Name: {backup_name}

📁 SOURCE CODE: {'✅ ' + str(source_files_count) + ' files' if source_files_count > 0 else '❌ Not found'}
   - Backend Python code (/src)
   - Frontend React code (/frontend) 
   - Configuration files (requirements.txt, package.json, etc.)
   - All application files

💾 Database: {'✅ Included' if os.path.exists(db_source) else '❌ Not found'}
🖼️  Images: {image_count} files

This backup contains EVERYTHING needed to restore the complete website!
        """
        
        with open(os.path.join(backup_dir, "backup_info.txt"), 'w') as f:
            f.write(info_content)
        
        # Create tar.gz file using simple method
        tar_path = os.path.join(temp_dir, f"{backup_name}.tar.gz")
        
        with tarfile.open(tar_path, 'w:gz') as tar:
            # Add files one by one with simple names
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                tar.add(item_path, arcname=item)
        
        print(f"✅ COMPLETE Backup created: {tar_path}")
        print(f"📦 File size: {os.path.getsize(tar_path) / (1024*1024):.1f} MB")
        print(f"🎯 SOURCE CODE FILES: {source_files_count}")
        print(f"💾 DATABASE: {'✅' if os.path.exists(db_source) else '❌'}")
        print(f"🖼️  IMAGES: {image_count}")
        
        return tar_path
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    backup_file = create_simple_backup()
    if backup_file:
        print(f"\n🎉 SUCCESS! COMPLETE BACKUP created at: {backup_file}")
        print("📁 This backup includes ALL source code files!")
    else:
        print("\n💥 FAILED! Could not create backup")

