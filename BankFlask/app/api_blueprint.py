"""
Modern REST API Blueprint - JWT-based authentication
Separates API concerns from web routes
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-production')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRY_HOURS = 24


def token_required(f):
    """Decorator to require JWT token for API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated


# ===== AUTHENTICATION ENDPOINTS =====

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # For now, return mock response
    return jsonify({
        'message': 'User registered successfully',
        'user_id': 1,
        'email': data['email']
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Mock authentication
    if email == 'demo@eduai.com' and password == 'password123':
        user_id = 1
        # Generate JWT token
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return jsonify({
            'token': token,
            'user_id': user_id,
            'email': email,
            'first_name': 'Demo',
            'last_name': 'User'
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


@api_bp.route('/auth/refresh', methods=['POST'])
@token_required
def refresh_token(user_id):
    """Refresh JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return jsonify({
        'token': token,
        'message': 'Token refreshed successfully'
    }), 200


# ===== RESUME ENDPOINTS =====

@api_bp.route('/resume/upload', methods=['POST'])
def upload_resume():
    """Upload and process resume"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Mock processing
    return jsonify({
        'resume_id': 'resume_12345',
        'status': 'processing',
        'progress': 0,
        'message': 'Resume uploaded and processing started'
    }), 202


@api_bp.route('/resume/<resume_id>', methods=['GET'])
def get_resume(resume_id):
    """Get resume processing status and extracted data"""
    
    # Mock response
    return jsonify({
        'resume_id': resume_id,
        'status': 'completed',
        'progress': 100,
        'extracted_data': {
            'email': 'user@example.com',
            'phone': '+1-234-567-8900',
            'experience_years': 5,
            'education': ['Bachelor in Computer Science']
        },
        'analysis': {
            'readability_score': 85.5,
            'ats_compatibility': 92.0,
            'impact_score': 78.5
        }
    }), 200


# ===== SKILLS ENDPOINTS =====

@api_bp.route('/skills', methods=['GET'])
@token_required
def get_skills(user_id):
    """Get user's extracted skills"""
    
    # Mock response
    return jsonify({
        'skills': [
            {
                'name': 'Python',
                'category': 'programming',
                'proficiency': 85,
                'market_demand': 95,
                'growth_potential': 92,
                'verified': True
            },
            {
                'name': 'React',
                'category': 'framework',
                'proficiency': 78,
                'market_demand': 88,
                'growth_potential': 90,
                'verified': False
            },
            {
                'name': 'Leadership',
                'category': 'soft',
                'proficiency': 70,
                'market_demand': 85,
                'growth_potential': 80,
                'verified': True
            }
        ]
    }), 200


@api_bp.route('/skills/gap-analysis', methods=['POST'])
@token_required
def analyze_skill_gap(user_id):
    """Analyze skill gap for target role"""
    data = request.get_json()
    target_role = data.get('target_role', 'Software Engineer')
    
    return jsonify({
        'target_role': target_role,
        'gap_analysis': {
            'missing_skills': ['Docker', 'AWS', 'Kubernetes'],
            'excess_skills': ['Excel', 'PowerPoint'],
            'gap_percentage': 30,
            'completion_percentage': 70
        },
        'recommendations': [
            'Start Docker course on Udemy',
            'AWS Hands-on Labs',
            'Build containerized project'
        ]
    }), 200


# ===== LEARNING PATH ENDPOINTS =====

@api_bp.route('/learning-paths', methods=['GET'])
@token_required
def get_learning_paths(user_id):
    """Get user's learning paths"""
    
    return jsonify({
        'paths': [
            {
                'path_id': 'path_001',
                'title': 'Path to Senior Software Engineer',
                'target_role': 'Senior Software Engineer',
                'progress_percentage': 45,
                'estimated_duration_days': 120,
                'status': 'active'
            },
            {
                'path_id': 'path_002',
                'title': 'Cloud Architecture Mastery',
                'target_role': 'Cloud Architect',
                'progress_percentage': 20,
                'estimated_duration_days': 90,
                'status': 'active'
            }
        ]
    }), 200


@api_bp.route('/learning-paths', methods=['POST'])
@token_required
def create_learning_path(user_id):
    """Generate AI learning path"""
    data = request.get_json()
    
    return jsonify({
        'path_id': 'path_new_123',
        'title': f'Path to {data.get("target_role")}',
        'status': 'created',
        'milestones': [
            {
                'title': 'Foundation Skills',
                'duration_weeks': 4,
                'resources': ['Online Course', 'Documentation']
            },
            {
                'title': 'Advanced Concepts',
                'duration_weeks': 6,
                'resources': ['Advanced Course', 'Practice Projects']
            }
        ]
    }), 201


# ===== JOB MATCH ENDPOINTS =====

@api_bp.route('/job-match', methods=['POST'])
@token_required
def calculate_job_match(user_id):
    """Calculate match score for job posting"""
    data = request.get_json()
    job_description = data.get('job_description', '')
    
    return jsonify({
        'job_id': 'job_12345',
        'match_score': 78.5,
        'skill_match': {
            'matching_skills': ['Python', 'REST API', 'Git'],
            'missing_skills': ['Docker', 'Kubernetes'],
            'match_percentage': 75
        },
        'recommendations': [
            'Learn Docker for better match',
            'Build cloud-native project',
            'Study Kubernetes concepts'
        ]
    }), 200


# ===== AI INSIGHTS ENDPOINTS =====

@api_bp.route('/insights', methods=['GET'])
@token_required
def get_insights(user_id):
    """Get AI-generated insights"""
    
    return jsonify({
        'insights': [
            {
                'insight_id': 'insight_001',
                'type': 'SKILL_DEMAND',
                'title': 'High-Demand Skill Alert',
                'description': 'Machine Learning is in high demand. Consider adding this skill.',
                'priority': 'high',
                'confidence': 92.5
            },
            {
                'insight_id': 'insight_002',
                'type': 'CAREER_PATH',
                'title': 'Career Growth Opportunity',
                'description': 'You are well-positioned for a senior role.',
                'priority': 'medium',
                'confidence': 85.0
            }
        ]
    }), 200


# ===== MENTOR ENDPOINTS =====

@api_bp.route('/mentors', methods=['GET'])
@token_required
def get_mentors(user_id):
    """Get recommended mentors"""
    
    return jsonify({
        'mentors': [
            {
                'mentor_id': 'mentor_001',
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'title': 'Senior Software Engineer',
                'company': 'Google',
                'photo': '/static/avatars/sarah.jpg',
                'rating': 4.9,
                'reviews': 127,
                'hourly_rate': 150,
                'expertise': ['Python', 'System Design', 'Leadership']
            },
            {
                'mentor_id': 'mentor_002',
                'first_name': 'Marcus',
                'last_name': 'Johnson',
                'title': 'Engineering Manager',
                'company': 'Amazon',
                'photo': '/static/avatars/marcus.jpg',
                'rating': 4.8,
                'reviews': 89,
                'hourly_rate': 120,
                'expertise': ['Cloud Architecture', 'Team Management']
            }
        ]
    }), 200


# ===== ANALYTICS ENDPOINTS =====

@api_bp.route('/user/analytics', methods=['GET'])
@token_required
def get_user_analytics(user_id):
    """Get user's analytics and progress"""
    
    return jsonify({
        'user_id': user_id,
        'profile_completion': 75,
        'skills_count': 12,
        'paths_in_progress': 2,
        'paths_completed': 1,
        'total_learning_hours': 145,
        'streak_days': 7,
        'recent_activity': [
            {'date': '2025-02-08', 'activity': 'Completed Docker tutorial'},
            {'date': '2025-02-07', 'activity': 'Uploaded resume'},
            {'date': '2025-02-06', 'activity': 'Started AWS course'}
        ]
    }), 200


# ===== ADMIN ENDPOINTS =====

@api_bp.route('/admin/analytics', methods=['GET'])
def get_admin_analytics():
    """Admin dashboard analytics"""
    
    return jsonify({
        'total_users': 1542,
        'active_today': 284,
        'new_today': 12,
        'resumes_processed': 3421,
        'learning_paths_created': 2156,
        'avg_completion': 42.5,
        'trending_skills': [
            {'skill': 'Machine Learning', 'demand': 95},
            {'skill': 'Cloud Architecture', 'demand': 92},
            {'skill': 'DevOps', 'demand': 88}
        ]
    }), 200


# ===== HEALTH CHECK =====

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200
