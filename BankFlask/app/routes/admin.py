"""
Admin Dashboard Routes
Handles platform analytics, KPIs, and administrative functions
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mock admin check - in production, verify user.is_admin
        if not current_user.is_authenticated:
            return {'error': 'Not authenticated'}, 401
        
        # Simple mock - would check actual role in production
        if current_user.id != 1:  # Mock admin ID
            return {'error': 'Admin access required'}, 403
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Main admin dashboard with KPIs"""
    
    analytics = {
        'users': {
            'total': 14250,
            'active_today': 3450,
            'new_today': 127,
            'growth_percent': 8.5
        },
        'resumes': {
            'total_processed': 8920,
            'processing_now': 45,
            'avg_processing_time': '2.5 min',
            'success_rate': 96.8
        },
        'learning': {
            'paths_created': 5680,
            'paths_active': 4200,
            'avg_completion': 42.5,
            'completion_rate': '12.4%'
        },
        'mentoring': {
            'total_mentors': 1240,
            'active_mentors': 890,
            'sessions_month': 2450,
            'satisfaction_score': 4.7
        }
    }
    
    return render_template('admin/dashboard.html', analytics=analytics)


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Detailed analytics and reporting"""
    
    data = {
        'user_growth': [
            {'date': '2025-01-01', 'users': 10000},
            {'date': '2025-01-08', 'users': 11200},
            {'date': '2025-01-15', 'users': 12450},
            {'date': '2025-02-01', 'users': 14250}
        ],
        'skill_demand': [
            {'skill': 'Machine Learning', 'demand': 98},
            {'skill': 'Cloud Architecture', 'demand': 92},
            {'skill': 'DevOps', 'demand': 88},
            {'skill': 'CUDA/GPU', 'demand': 85}
        ],
        'job_match_scores': [
            {'range': '90-100', 'count': 1250},
            {'range': '80-89', 'count': 3400},
            {'range': '70-79', 'count': 2100},
            {'range': '60-69', 'count': 1200}
        ],
        'path_completion_rates': [
            {'week': 'Week 1', 'rate': 95},
            {'week': 'Week 2', 'rate': 88},
            {'week': 'Week 3', 'rate': 75},
            {'week': 'Week 4', 'rate': 58}
        ]
    }
    
    return render_template('admin/analytics.html', data=data)


@admin_bp.route('/users')
@login_required
@admin_required
def users_management():
    """Manage platform users"""
    
    users = [
        {
            'id': 1,
            'name': 'John Developer',
            'email': 'john@example.com',
            'joined': '2025-01-15',
            'status': 'active',
            'resumes': 2,
            'paths': 3
        },
        {
            'id': 2,
            'name': 'Alice Engineer',
            'email': 'alice@example.com',
            'joined': '2025-01-20',
            'status': 'active',
            'resumes': 1,
            'paths': 1
        },
        {
            'id': 3,
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'joined': '2025-02-05',
            'status': 'inactive',
            'resumes': 0,
            'paths': 0
        }
    ]
    
    return render_template('admin/users.html', users=users)


@admin_bp.route('/mentors-management')
@login_required
@admin_required
def mentors_management():
    """Manage mentor profiles"""
    
    mentors = [
        {
            'id': 'mentor_001',
            'name': 'Sarah Chen',
            'expertise': ['System Design', 'Python', 'Leadership'],
            'rating': 4.9,
            'sessions_completed': 156,
            'revenue_month': 15600
        },
        {
            'id': 'mentor_002',
            'name': 'Marcus Johnson',
            'expertise': ['Cloud Architecture', 'Management'],
            'rating': 4.8,
            'sessions_completed': 89,
            'revenue_month': 12000
        }
    ]
    
    return render_template('admin/mentors.html', mentors=mentors)


@admin_bp.route('/content-management')
@login_required
@admin_required
def content_management():
    """Manage learning paths, skills taxonomy, roles"""
    
    content = {
        'skills': {
            'total': 250,
            'technical': 180,
            'soft': 50,
            'languages': 20
        },
        'roles': {
            'total': 45,
            'active': 40,
            'trending': ['ML Engineer', 'Cloud Architect', 'DevOps']
        },
        'learning_resources': {
            'total': 1200,
            'courses': 450,
            'books': 300,
            'projects': 450
        }
    }
    
    return render_template('admin/content.html', content=content)


@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings and configuration"""
    
    settings_data = {
        'platform': {
            'name': 'EduAI',
            'version': '1.0.0',
            'environment': 'production'
        },
        'features': {
            'mentoring_enabled': True,
            'ai_recommendations': True,
            'job_matching': True,
            'social_features': False
        }
    }
    
    return render_template('admin/settings.html', settings=settings_data)


# ===== API ENDPOINTS FOR ADMIN DASHBOARD =====

@admin_bp.route('/api/kpis')
@login_required
@admin_required
def get_kpis():
    """Get KPI data (called by AJAX)"""
    
    kpis = {
        'users': 14250,
        'active_today': 3450,
        'resumes_processed': 8920,
        'paths_created': 5680,
        'mentoring_sessions': 2450,
        'avg_satisfaction': 4.7
    }
    
    return jsonify(kpis), 200


@admin_bp.route('/api/daily-stats')
@login_required
@admin_required
def get_daily_stats():
    """Get daily statistics"""
    
    stats = [
        {'date': '2025-02-01', 'new_users': 120, 'resumes': 45, 'paths': 28},
        {'date': '2025-02-02', 'new_users': 135, 'resumes': 52, 'paths': 31},
        {'date': '2025-02-03', 'new_users': 142, 'resumes': 48, 'paths': 29},
        {'date': '2025-02-04', 'new_users': 128, 'resumes': 55, 'paths': 32},
        {'date': '2025-02-05', 'new_users': 157, 'resumes': 61, 'paths': 35}
    ]
    
    return jsonify(stats), 200


@admin_bp.route('/api/export-report')
@login_required
@admin_required
def export_report():
    """Export analytics report"""
    
    # In production, would generate CSV/PDF
    report = {
        'generated_at': '2025-02-08',
        'report_type': 'monthly',
        'file_url': '/reports/analytics_feb_2025.pdf'
    }
    
    return jsonify(report), 200
