"""
Configuration file for Mind's Eye Photography
Centralizes asset directory paths for easy management
"""
import os

# Base directories here
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'src', 'static')

# Separate photography assets directory (persistent volume for Railway)
# Use Railway's volume mount path from environment variable, with fallbacks
RAILWAY_VOLUME_PATH = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH')
if RAILWAY_VOLUME_PATH and os.path.exists(RAILWAY_VOLUME_PATH):
    PHOTOGRAPHY_ASSETS_DIR = RAILWAY_VOLUME_PATH
elif os.path.exists('/data'):
    PHOTOGRAPHY_ASSETS_DIR = '/data'
elif os.path.exists('/mnt/data'):
    PHOTOGRAPHY_ASSETS_DIR = '/mnt/data'
else:
    # Local development fallback
    PHOTOGRAPHY_ASSETS_DIR = os.path.join(BASE_DIR, '..', 'photography-assets')

print(f"🔍 PHOTOGRAPHY_ASSETS_DIR set to: {PHOTOGRAPHY_ASSETS_DIR}")
print(f"🔍 RAILWAY_VOLUME_MOUNT_PATH: {RAILWAY_VOLUME_PATH}")
print(f"🔍 Directory exists: {os.path.exists(PHOTOGRAPHY_ASSETS_DIR)}")

# Data files (keep with website for easy admin updates)
PORTFOLIO_DATA_FILE = os.path.join(STATIC_DIR, 'assets', 'portfolio-data-multicategory.json')
CATEGORIES_CONFIG_FILE = os.path.join(STATIC_DIR, 'assets', 'categories-config.json')
FEATURED_DATA_FILE = os.path.join(STATIC_DIR, 'assets', 'featured-image.json')

# Legacy paths for backward compatibility
LEGACY_ASSETS_DIR = os.path.join(STATIC_DIR, 'assets')

# URL paths for serving images
PHOTOGRAPHY_ASSETS_URL_PREFIX = '/data/'
LEGACY_ASSETS_URL_PREFIX = '/data/'

def get_image_url(filename):
    """
    Get the URL for an image file
    Returns new photography-assets URL format
    """
    return f"{PHOTOGRAPHY_ASSETS_URL_PREFIX}{filename}"

def get_legacy_image_url(filename):
    """
    Get the legacy URL for an image file
    Used for backward compatibility during migration
    """
    return f"{LEGACY_ASSETS_URL_PREFIX}{filename}"

