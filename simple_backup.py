#!/usr/bin/env python3
"""
Simple, reliable backup script for Mind's Eye Photography
This bypasses the broken backup system and creates a working backup
"""

import os
import shutil
import tarfile
import tempfile
from datetime import datetime

def create_simple_backup():
    """Create a simple, working backup"""
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"simple_backup_{timestamp}"
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        backup_dir = os.path.join(temp_dir, backup_name)
        os.makedirs(backup_dir)
        
        print(f"Creating backup in: {backup_dir}")
        
        # Copy database file
        db_source = "/data/mindseye.db"
        if os.path.exists(db_source):
            shutil.copy2(db_source, backup_dir)
            print("✅ Database copied")
        else:
            print("⚠️  Database not found")
        
        # Copy all image files
        data_dir = "/data"
        if os.path.exists(data_dir):
            image_count = 0
            for file in os.listdir(data_dir):
                if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    source_path = os.path.join(data_dir, file)
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, backup_dir)
                        image_count += 1
            print(f"✅ {image_count} images copied")
        
        # Create backup info file
        info_content = f"""
SIMPLE BACKUP CREATED: {datetime.now()}
Backup Name: {backup_name}
Database: {'✅ Included' if os.path.exists(db_source) else '❌ Not found'}
Images: {image_count} files
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
        
        print(f"✅ Backup created: {tar_path}")
        print(f"📦 File size: {os.path.getsize(tar_path) / (1024*1024):.1f} MB")
        
        return tar_path
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    backup_file = create_simple_backup()
    if backup_file:
        print(f"\n🎉 SUCCESS! Backup created at: {backup_file}")
    else:
        print("\n💥 FAILED! Could not create backup")

