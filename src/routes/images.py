from flask import Blueprint, send_from_directory, abort
import os

images_bp = Blueprint('images', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')

@images_bp.route('/images/<filename>')
def serve_image(filename):
    """Serve uploaded images"""
    try:
        # Security check - ensure filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(404)
        
        # Check if file exists
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            abort(404)
        
        return send_from_directory(UPLOAD_FOLDER, filename)
        
    except Exception as e:
        abort(404)

