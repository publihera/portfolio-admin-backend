from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.project import db, Project, ProjectImage
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image
import json

projects_bp = Blueprint('projects', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_IMAGE_SIZE = (1920, 1080)  # Max dimensions for optimization

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_image(image_path, max_size=MAX_IMAGE_SIZE, quality=85):
    """Optimize image for web use"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if larger than max_size
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return False

@projects_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects with optional filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        client = request.args.get('client')
        agency = request.args.get('agency')
        project_type = request.args.get('type')
        year = request.args.get('year', type=int)
        published_only = request.args.get('published_only', 'true').lower() == 'true'
        search = request.args.get('search')
        
        # Build query
        query = Project.query
        
        if published_only:
            query = query.filter(Project.published == True)
        
        if client:
            query = query.filter(Project.client.ilike(f'%{client}%'))
        
        if agency:
            query = query.filter(Project.agency.ilike(f'%{agency}%'))
        
        if project_type:
            query = query.filter(Project.type.contains(project_type))
        
        if year:
            query = query.filter(Project.year == year)
        
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Project.title.ilike(search_filter),
                    Project.client.ilike(search_filter),
                    Project.agency.ilike(search_filter),
                    Project.description.ilike(search_filter)
                )
            )
        
        # Order by updated_at desc
        query = query.order_by(Project.updated_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        projects = [project.to_dict() for project in pagination.items]
        
        return jsonify({
            'projects': projects,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project by ID"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'project': project.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['title', 'client', 'agency', 'type', 'year', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate unique ID if not provided
        project_id = data.get('id') or str(uuid.uuid4())
        
        # Check if project ID already exists
        if Project.query.get(project_id):
            return jsonify({'error': 'Project ID already exists'}), 400
        
        # Create project
        project = Project(
            id=project_id,
            title=data['title'],
            client=data['client'],
            agency=data['agency'],
            type=json.dumps(data['type']) if isinstance(data['type'], list) else data['type'],
            year=data['year'],
            duration=data.get('duration'),
            tools=json.dumps(data.get('tools', [])) if isinstance(data.get('tools'), list) else data.get('tools'),
            description=data['description'],
            results=json.dumps(data.get('results', [])) if isinstance(data.get('results'), list) else data.get('results'),
            published=data.get('published', True)
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update an existing project"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'title' in data:
            project.title = data['title']
        if 'client' in data:
            project.client = data['client']
        if 'agency' in data:
            project.agency = data['agency']
        if 'type' in data:
            project.type = json.dumps(data['type']) if isinstance(data['type'], list) else data['type']
        if 'year' in data:
            project.year = data['year']
        if 'duration' in data:
            project.duration = data['duration']
        if 'tools' in data:
            project.tools = json.dumps(data['tools']) if isinstance(data['tools'], list) else data['tools']
        if 'description' in data:
            project.description = data['description']
        if 'results' in data:
            project.results = json.dumps(data['results']) if isinstance(data['results'], list) else data['results']
        if 'published' in data:
            project.published = data['published']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project and all its images"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Delete associated image files
        for image in project.images:
            image_path = os.path.join(UPLOAD_FOLDER, image.filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete project (cascade will delete images from DB)
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<project_id>/images', methods=['POST'])
@jwt_required()
def upload_project_images(project_id):
    """Upload images for a project"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        uploaded_images = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Generate unique filename
                original_filename = secure_filename(file.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                
                # Save file
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                
                # Optimize image
                if file_extension in ['jpg', 'jpeg', 'png', 'webp']:
                    optimize_image(file_path)
                
                # Get current max order for this project
                max_order = db.session.query(db.func.max(ProjectImage.order)).filter_by(project_id=project_id).scalar() or 0
                
                # Create image record
                image = ProjectImage(
                    project_id=project_id,
                    filename=unique_filename,
                    original_filename=original_filename,
                    order=max_order + 1
                )
                
                db.session.add(image)
                uploaded_images.append(image)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(uploaded_images)} images uploaded successfully',
            'images': [img.to_dict() for img in uploaded_images]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    """Delete a specific image"""
    try:
        image = ProjectImage.query.get(image_id)
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Delete file
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/images/<int:image_id>/metadata', methods=['PUT'])
@jwt_required()
def update_image_metadata(image_id):
    """Update image metadata (alt_text, caption)"""
    try:
        image = ProjectImage.query.get(image_id)
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update metadata
        if 'alt_text' in data:
            image.alt_text = data['alt_text']
        if 'caption' in data:
            image.caption = data['caption']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Image metadata updated successfully',
            'image': image.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/projects/<project_id>/images/reorder', methods=['PUT'])
@jwt_required()
def reorder_images(project_id):
    """Reorder images for a project"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if not data or 'image_ids' not in data:
            return jsonify({'error': 'image_ids array is required'}), 400
        
        image_ids = data['image_ids']
        
        # Update order for each image
        for index, image_id in enumerate(image_ids):
            image = ProjectImage.query.filter_by(id=image_id, project_id=project_id).first()
            if image:
                image.order = index + 1
        
        db.session.commit()
        
        return jsonify({'message': 'Images reordered successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get portfolio statistics"""
    try:
        total_projects = Project.query.count()
        published_projects = Project.query.filter_by(published=True).count()
        total_images = ProjectImage.query.count()
        
        # Get unique clients and agencies
        clients = db.session.query(Project.client).distinct().count()
        agencies = db.session.query(Project.agency).distinct().count()
        
        return jsonify({
            'total_projects': total_projects,
            'published_projects': published_projects,
            'total_images': total_images,
            'unique_clients': clients,
            'unique_agencies': agencies
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

