from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    client = db.Column(db.String(100), nullable=False)
    agency = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Text, nullable=False)  # JSON array as string
    year = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String(50), nullable=True)
    tools = db.Column(db.Text, nullable=True)  # JSON array as string
    description = db.Column(db.Text, nullable=False)
    results = db.Column(db.Text, nullable=True)  # JSON array as string
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with images
    images = db.relationship('ProjectImage', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)
        # Convert lists to JSON strings
        if isinstance(kwargs.get('type'), list):
            self.type = json.dumps(kwargs['type'])
        if isinstance(kwargs.get('tools'), list):
            self.tools = json.dumps(kwargs['tools'])
        if isinstance(kwargs.get('results'), list):
            self.results = json.dumps(kwargs['results'])
    
    @property
    def type_list(self):
        """Return type as a list"""
        try:
            return json.loads(self.type) if self.type else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @type_list.setter
    def type_list(self, value):
        """Set type from a list"""
        self.type = json.dumps(value) if isinstance(value, list) else value
    
    @property
    def tools_list(self):
        """Return tools as a list"""
        try:
            return json.loads(self.tools) if self.tools else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @tools_list.setter
    def tools_list(self, value):
        """Set tools from a list"""
        self.tools = json.dumps(value) if isinstance(value, list) else value
    
    @property
    def results_list(self):
        """Return results as a list"""
        try:
            return json.loads(self.results) if self.results else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @results_list.setter
    def results_list(self, value):
        """Set results from a list"""
        self.results = json.dumps(value) if isinstance(value, list) else value
    
    def to_dict(self):
        """Convert project to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'client': self.client,
            'agency': self.agency,
            'type': self.type_list,
            'year': self.year,
            'duration': self.duration,
            'tools': self.tools_list,
            'description': self.description,
            'results': self.results_list,
            'published': self.published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'images': [img.to_dict() for img in sorted(self.images, key=lambda x: x.order)]
        }

class ProjectImage(db.Model):
    __tablename__ = 'project_images'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(255), nullable=True)
    caption = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert image to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'url': f'/api/images/{self.filename}',
            'alt_text': self.alt_text,
            'caption': self.caption,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization (excluding password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

