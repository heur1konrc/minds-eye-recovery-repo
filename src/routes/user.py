from flask import Blueprint, jsonify, request
from src.models import User, Image, Category, ImageCategory, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    
    data = request.json
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


@user_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """API endpoint to get portfolio data from SQL database"""
    try:
        # Use same query method as admin - Image.query.all()
        images = Image.query.all()
        portfolio_data = []
        
        print(f"Found {len(images)} images in database")  # Debug log
        
        for image in images:
            # Get categories for this image - same as admin
            image_categories = [cat.category.name for cat in image.categories]
            
            portfolio_item = {
                'id': str(image.id),  # Convert UUID to string
                'title': image.title or f"Image {image.id}",
                'description': image.description or "",
                'image': image.filename,  # Frontend expects 'image' field
                'categories': image_categories,
                'metadata': {
                    'created_at': image.created_at.isoformat() if image.created_at else None,
                    'updated_at': image.updated_at.isoformat() if image.updated_at else None
                }
            }
            portfolio_data.append(portfolio_item)
        
        print(f"Returning {len(portfolio_data)} portfolio items")  # Debug log
        return jsonify(portfolio_data)
        
    except Exception as e:
        print(f"Error loading portfolio from database: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

