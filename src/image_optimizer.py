#!/usr/bin/env python3
"""
Image Optimization System for Mind's Eye Photography
Generates optimized versions of images for faster loading
"""

import os
import sys
from PIL import Image as PILImage, ImageOps
from datetime import datetime
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PHOTOGRAPHY_ASSETS_DIR

class ImageOptimizer:
    """Image optimization and resizing system"""
    
    def __init__(self, assets_dir=PHOTOGRAPHY_ASSETS_DIR):
        self.assets_dir = assets_dir
        self.optimized_dir = os.path.join(assets_dir, 'optimized')
        self.thumbnails_dir = os.path.join(assets_dir, 'thumbnails')
        
        # Create optimization directories
        os.makedirs(self.optimized_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
        
        # Image size configurations
        self.sizes = {
            'thumbnail': {'width': 300, 'height': 300, 'quality': 85},
            'small': {'width': 600, 'height': 600, 'quality': 85},
            'medium': {'width': 1200, 'height': 1200, 'quality': 90},
            'large': {'width': 1920, 'height': 1920, 'quality': 95}
        }
    
    def get_optimized_filename(self, original_filename, size_name):
        """Generate filename for optimized version"""
        name, ext = os.path.splitext(original_filename)
        return f"{name}_{size_name}{ext}"
    
    def optimize_image(self, filename, force_regenerate=False):
        """Optimize a single image into multiple sizes"""
        original_path = os.path.join(self.assets_dir, filename)
        
        if not os.path.exists(original_path):
            print(f"❌ Original image not found: {filename}")
            return False
        
        print(f"🔄 Optimizing: {filename}")
        
        try:
            with PILImage.open(original_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get original dimensions
                original_width, original_height = img.size
                
                results = {
                    'original': {
                        'width': original_width,
                        'height': original_height,
                        'file_size': os.path.getsize(original_path)
                    },
                    'optimized': {}
                }
                
                # Generate each size
                for size_name, config in self.sizes.items():
                    optimized_filename = self.get_optimized_filename(filename, size_name)
                    
                    # Determine output directory
                    if size_name == 'thumbnail':
                        output_path = os.path.join(self.thumbnails_dir, optimized_filename)
                    else:
                        output_path = os.path.join(self.optimized_dir, optimized_filename)
                    
                    # Skip if already exists and not forcing regeneration
                    if os.path.exists(output_path) and not force_regenerate:
                        print(f"   ⏭️  {size_name} already exists")
                        continue
                    
                    # Calculate new dimensions maintaining aspect ratio
                    max_width = config['width']
                    max_height = config['height']
                    
                    # Don't upscale images
                    if original_width <= max_width and original_height <= max_height:
                        if size_name == 'large':
                            # For large size, just copy original if it's already small enough
                            new_width, new_height = original_width, original_height
                            resized_img = img.copy()
                        else:
                            continue  # Skip smaller sizes if original is already small
                    else:
                        # Calculate aspect ratio preserving dimensions
                        ratio = min(max_width / original_width, max_height / original_height)
                        new_width = int(original_width * ratio)
                        new_height = int(original_height * ratio)
                        
                        # Resize image with high quality resampling
                        resized_img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                    
                    # Save optimized image
                    resized_img.save(
                        output_path,
                        'JPEG',
                        quality=config['quality'],
                        optimize=True,
                        progressive=True
                    )
                    
                    # Record results
                    file_size = os.path.getsize(output_path)
                    results['optimized'][size_name] = {
                        'filename': optimized_filename,
                        'width': new_width,
                        'height': new_height,
                        'file_size': file_size,
                        'compression_ratio': round(file_size / results['original']['file_size'], 2)
                    }
                    
                    print(f"   ✅ {size_name}: {new_width}x{new_height} ({file_size // 1024}KB)")
                
                return results
                
        except Exception as e:
            print(f"❌ Error optimizing {filename}: {e}")
            return False
    
    def optimize_all_images(self, force_regenerate=False):
        """Optimize all images in the assets directory"""
        print("🚀 Starting image optimization for all images...")
        
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        image_files = []
        
        for file in os.listdir(self.assets_dir):
            if os.path.isfile(os.path.join(self.assets_dir, file)):
                _, ext = os.path.splitext(file.lower())
                if ext in image_extensions:
                    image_files.append(file)
        
        print(f"📁 Found {len(image_files)} images to optimize")
        
        if len(image_files) == 0:
            print("ℹ️  No images to optimize")
            return
        
        optimization_results = {}
        success_count = 0
        error_count = 0
        
        for filename in image_files:
            result = self.optimize_image(filename, force_regenerate)
            if result:
                optimization_results[filename] = result
                success_count += 1
            else:
                error_count += 1
        
        # Save optimization report
        report_path = os.path.join(self.assets_dir, 'optimization_report.json')
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_images': len(image_files),
            'successful': success_count,
            'errors': error_count,
            'results': optimization_results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n🎉 Optimization completed!")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📊 Report saved: {report_path}")
        
        # Calculate total space savings
        total_original_size = 0
        total_optimized_size = 0
        
        for result in optimization_results.values():
            total_original_size += result['original']['file_size']
            for optimized in result['optimized'].values():
                total_optimized_size += optimized['file_size']
        
        if total_original_size > 0:
            space_savings = total_original_size - total_optimized_size
            savings_percent = (space_savings / total_original_size) * 100
            print(f"   💾 Space analysis:")
            print(f"      Original: {total_original_size // (1024*1024)}MB")
            print(f"      Optimized versions: {total_optimized_size // (1024*1024)}MB")
            print(f"      Additional storage: {total_optimized_size // (1024*1024)}MB for faster loading")
    
    def get_optimized_url(self, original_filename, size='medium'):
        """Get URL for optimized version of an image"""
        if size == 'thumbnail':
            optimized_filename = self.get_optimized_filename(original_filename, size)
            return f'/assets/thumbnails/{optimized_filename}'
        else:
            optimized_filename = self.get_optimized_filename(original_filename, size)
            optimized_path = os.path.join(self.optimized_dir, optimized_filename)
            
            # Return optimized version if it exists, otherwise original
            if os.path.exists(optimized_path):
                return f'/assets/optimized/{optimized_filename}'
            else:
                return f'/assets/{original_filename}'
    
    def cleanup_orphaned_optimized_images(self):
        """Remove optimized images that no longer have original files"""
        print("🧹 Cleaning up orphaned optimized images...")
        
        # Get list of original images
        original_images = set()
        for file in os.listdir(self.assets_dir):
            if os.path.isfile(os.path.join(self.assets_dir, file)):
                _, ext = os.path.splitext(file.lower())
                if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}:
                    original_images.add(file)
        
        cleaned_count = 0
        
        # Check optimized directory
        if os.path.exists(self.optimized_dir):
            for file in os.listdir(self.optimized_dir):
                # Extract original filename from optimized filename
                for size_name in self.sizes.keys():
                    if f'_{size_name}.' in file:
                        original_name = file.replace(f'_{size_name}', '')
                        if original_name not in original_images:
                            os.remove(os.path.join(self.optimized_dir, file))
                            print(f"   🗑️  Removed: {file}")
                            cleaned_count += 1
                        break
        
        # Check thumbnails directory
        if os.path.exists(self.thumbnails_dir):
            for file in os.listdir(self.thumbnails_dir):
                if '_thumbnail.' in file:
                    original_name = file.replace('_thumbnail', '')
                    if original_name not in original_images:
                        os.remove(os.path.join(self.thumbnails_dir, file))
                        print(f"   🗑️  Removed thumbnail: {file}")
                        cleaned_count += 1
        
        print(f"✅ Cleanup completed: {cleaned_count} orphaned files removed")

def main():
    """Main function for running image optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Image Optimization System')
    parser.add_argument('--force', action='store_true', help='Force regeneration of existing optimized images')
    parser.add_argument('--cleanup', action='store_true', help='Clean up orphaned optimized images')
    parser.add_argument('--single', type=str, help='Optimize a single image file')
    
    args = parser.parse_args()
    
    optimizer = ImageOptimizer()
    
    if args.cleanup:
        optimizer.cleanup_orphaned_optimized_images()
    elif args.single:
        optimizer.optimize_image(args.single, args.force)
    else:
        optimizer.optimize_all_images(args.force)

if __name__ == "__main__":
    main()

