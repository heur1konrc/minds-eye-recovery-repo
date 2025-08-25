"""
About page content and images models
"""

from . import db
from datetime import datetime

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

