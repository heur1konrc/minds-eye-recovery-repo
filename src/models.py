"""
SQL Database Models for Mind's Eye Photography
SURGICAL CONVERSION: Maintains compatibility with existing imports
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# Create the main database instance
db = SQLAlchemy()

# ============================================================================
# NEW SQL MODELS FOR PHOTOGRAPHY SYSTEM
# ============================================================================

class Image(db.Model):
    """Portfolio Image Model"""
    __tablename__ = 'images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    is_featured = db.Column(db.Boolean, default=False)
    is_background = db.Column(db.Boolean, default=False)
    is_slideshow_background = db.Column(db.Boolean, default=False)  # New field for slideshow
    is_about = db.Column(db.Boolean, default=False)  # New field for About page images
    featured_story = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    
    # EXIF Data fields
    camera_make = db.Column(db.String(100))
    camera_model = db.Column(db.String(100))
    lens_model = db.Column(db.String(100))
    focal_length = db.Column(db.String(50))
    aperture = db.Column(db.String(50))
    shutter_speed = db.Column(db.String(50))
    iso = db.Column(db.String(50))
    flash = db.Column(db.String(50))
    exposure_mode = db.Column(db.String(50))
    white_balance = db.Column(db.String(50))
    
    # Relationships
    categories = db.relationship('ImageCategory', back_populates='image', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Image {self.title}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'image': self.filename,  # Keep 'image' key for compatibility
            'title': self.title,
            'description': self.description,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'is_featured': self.is_featured,
            'is_background': self.is_background,
            'featured_story': self.featured_story,
            'display_order': self.display_order,
            'categories': [cat.category.name for cat in self.categories]
        }

class Category(db.Model):
    """Image Category Model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#ff6b35')
    display_order = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    images = db.relationship('ImageCategory', back_populates='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'color': self.color,
            'display_order': self.display_order,
            'is_default': self.is_default,
            'image_count': len(self.images)
        }

class ImageCategory(db.Model):
    """Many-to-Many relationship between Images and Categories"""
    __tablename__ = 'image_categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = db.Column(db.String(36), db.ForeignKey('images.id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    image = db.relationship('Image', back_populates='categories')
    category = db.relationship('Category', back_populates='images')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('image_id', 'category_id', name='unique_image_category'),)
    
    def __repr__(self):
        return f'<ImageCategory {self.image_id} -> {self.category_id}>'

class SystemConfig(db.Model):
    """System Configuration Settings"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')
    description = db.Column(db.Text)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'
    
    def get_value(self):
        """Get typed value based on data_type"""
        if self.data_type == 'json':
            import json
            return json.loads(self.value) if self.value else {}
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes') if self.value else False
        elif self.data_type == 'integer':
            return int(self.value) if self.value else 0
        else:
            return self.value

    def set_value(self, value):
        """Set typed value based on data_type"""
        if self.data_type == 'json':
            import json
            self.value = json.dumps(value)
        elif self.data_type == 'boolean':
            self.value = str(bool(value)).lower()
        elif self.data_type == 'integer':
            self.value = str(int(value))
        else:
            self.value = str(value)

# ============================================================================
# COMPATIBILITY LAYER FOR EXISTING IMPORTS
# ============================================================================

# For src/routes/user.py compatibility
class User(db.Model):
    """User model for compatibility - minimal implementation"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================

def init_default_categories():
    """Initialize default categories if they don't exist"""
    # First, check if we need to migrate the database schema
    try:
        # Try to query with new schema
        existing_test = Category.query.first()
    except Exception as e:
        if "no such column" in str(e):
            print("🔄 Detected old database schema - performing migration...")
            # Drop and recreate tables for clean migration
            db.drop_all()
            db.create_all()
            print("✅ Database schema migrated successfully")
        else:
            raise e
    
    default_categories = [
        {'name': 'Wildlife', 'display_name': 'Wildlife', 'color': '#ff6b35', 'display_order': 1},
        {'name': 'Landscapes', 'display_name': 'Landscapes', 'color': '#4CAF50', 'display_order': 2},
        {'name': 'Portraits', 'display_name': 'Portraits', 'color': '#2196F3', 'display_order': 3},
        {'name': 'Events', 'display_name': 'Events', 'color': '#FF9800', 'display_order': 4},
        {'name': 'Nature', 'display_name': 'Nature', 'color': '#8BC34A', 'display_order': 5},
        {'name': 'Miscellaneous', 'display_name': 'Miscellaneous', 'color': '#9C27B0', 'display_order': 6},
    ]
    
    for cat_data in default_categories:
        existing = Category.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
    
    try:
        db.session.commit()
        print(f"✅ Initialized {len(default_categories)} default categories")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Categories may already exist: {e}")

def init_system_config():
    """Initialize default system configuration"""
    default_configs = [
        {
            'key': 'default_category',
            'value': 'All',
            'data_type': 'string',
            'description': 'Default category for filtering'
        },
        {
            'key': 'featured_image_id',
            'value': '',
            'data_type': 'string',
            'description': 'ID of currently featured image'
        },
        {
            'key': 'background_image_id',
            'value': '',
            'data_type': 'string',
            'description': 'ID of current background image'
        },
        {
            'key': 'site_title',
            'value': "Mind's Eye Photography",
            'data_type': 'string',
            'description': 'Website title'
        },
        {
            'key': 'site_tagline',
            'value': 'Where Moments Meet Imagination',
            'data_type': 'string',
            'description': 'Website tagline'
        }
    ]
    
    for config_data in default_configs:
        existing = SystemConfig.query.filter_by(key=config_data['key']).first()
        if not existing:
            config = SystemConfig(**config_data)
            db.session.add(config)
    
    try:
        db.session.commit()
        print(f"✅ Initialized {len(default_configs)} system config settings")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️  System config may already exist: {e}")

# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def migrate_existing_images():
    """Migrate existing images from volume to database"""
    from src.config import PHOTOGRAPHY_ASSETS_DIR
    import os
    # from PIL import Image as PILImage
    
    print("🔄 Starting image migration from volume to SQL database...")
    
    if not os.path.exists(PHOTOGRAPHY_ASSETS_DIR):
        print(f"❌ Volume directory not found: {PHOTOGRAPHY_ASSETS_DIR}")
        return
    
    # Get all image files from volume
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    image_files = []
    
    for file in os.listdir(PHOTOGRAPHY_ASSETS_DIR):
        file_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, file)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(file.lower())
            if ext in image_extensions:
                image_files.append(file)
    
    print(f"📁 Found {len(image_files)} image files in volume")
    
    if len(image_files) == 0:
        print("ℹ️  No images to migrate")
        return
    
    # Get all categories for assignment
    categories = {cat.name.lower(): cat for cat in Category.query.all()}
    
    migrated_count = 0
    skipped_count = 0
    
    for filename in image_files:
        # Check if image already exists in database
        existing = Image.query.filter_by(filename=filename).first()
        if existing:
            print(f"⏭️  Skipping {filename} (already in database)")
            skipped_count += 1
            continue
        
        # Get image metadata
        file_path = os.path.join(PHOTOGRAPHY_ASSETS_DIR, filename)
        try:
            # with PILImage.open(file_path) as img:
            #     width, height = img.size
            width, height = None, None  # Temporarily disabled
            file_size = os.path.getsize(file_path)
        except Exception as e:
            print(f"⚠️  Could not get info for {filename}: {e}")
            width, height, file_size = None, None, os.path.getsize(file_path)
        
        # Parse filename for title and categories
        name_without_ext = os.path.splitext(filename)[0]
        if '_' in name_without_ext and len(name_without_ext.split('_')[0]) > 30:
            name_without_ext = '_'.join(name_without_ext.split('_')[1:])
        
        title = name_without_ext.replace('-', ' ').replace('_', ' ').title()
        
        # Detect categories from filename
        filename_lower = filename.lower()
        detected_categories = []
        
        category_keywords = {
            'wildlife': ['bird', 'eagle', 'duck', 'rabbit', 'sparrow', 'blackbird', 'woodpecker', 'starling', 'turkey'],
            'nature': ['sunset', 'landscape', 'tree', 'forest', 'lake', 'mountain'],
            'portraits': ['portrait', 'executive', 'headshot'],
            'events': ['festival', 'disability-festival', 'event', 'celebration'],
            'miscellaneous': ['zoo', 'skyline', 'madison']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in filename_lower for keyword in keywords):
                detected_categories.append(category.title())
        
        if not detected_categories:
            detected_categories = ['Miscellaneous']
        
        # Create image record
        image = Image(
            filename=filename,
            title=title,
            description=f"Migrated from volume - {title}",
            file_size=file_size,
            width=width,
            height=height,
            upload_date=datetime.utcnow()
        )
        
        db.session.add(image)
        db.session.flush()  # Get the image ID
        
        # Assign categories
        assigned_categories = []
        for cat_name in detected_categories:
            category = categories.get(cat_name.lower())
            if category:
                image_category = ImageCategory(
                    image_id=image.id,
                    category_id=category.id
                )
                db.session.add(image_category)
                assigned_categories.append(cat_name)
        
        print(f"✅ Migrated: {filename} -> {title} [{', '.join(assigned_categories)}]")
        migrated_count += 1
    
    # Commit all changes
    try:
        db.session.commit()
        print(f"\n🎉 Migration completed successfully!")
        print(f"   📊 Migrated: {migrated_count} images")
        print(f"   ⏭️  Skipped: {skipped_count} images (already existed)")
        print(f"   📁 Total in database: {Image.query.count()} images")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration failed: {e}")
        raise



# ============================================================================
# ABOUT PAGE MODELS
# ============================================================================

class AboutContent(db.Model):
    """About page content model"""
    __tablename__ = 'about_content'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False, default='')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AboutContent {self.id}>'

class AboutImage(db.Model):
    """About page images model"""
    __tablename__ = 'about_image'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AboutImage {self.filename}>'
    
    @property
    def image_url(self):
        """Get the URL for this about image"""
        return f'/assets/about/{self.filename}'



class SlideshowBackground(db.Model):
    """Slideshow background images model"""
    __tablename__ = 'slideshow_background'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(36), db.ForeignKey('images.id'), nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Image
    image = db.relationship('Image', backref='slideshow_backgrounds')
    
    def __repr__(self):
        return f'<SlideshowBackground {self.image_id}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'image_id': self.image_id,
            'filename': self.image.filename if self.image else None,
            'title': self.image.title if self.image else None,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

class SlideshowSettings(db.Model):
    """Slideshow configuration settings"""
    __tablename__ = 'slideshow_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    transition_duration = db.Column(db.Integer, default=5000)  # milliseconds
    fade_duration = db.Column(db.Integer, default=1000)  # milliseconds
    auto_play = db.Column(db.Boolean, default=True)
    pause_on_hover = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SlideshowSettings {self.id}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'transition_duration': self.transition_duration,
            'fade_duration': self.fade_duration,
            'auto_play': self.auto_play,
            'pause_on_hover': self.pause_on_hover,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

