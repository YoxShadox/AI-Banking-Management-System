"""
Job Matching and Application Tracking Routes
Handles job recommendations, matching scores, and application management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@jobs_bp.route('/')
@login_required
def dashboard():
    """Job matches dashboard"""
    
    job_matches = [
        {
            'job_id': 'job_001',
            'title': 'Senior Software Engineer',
            'company': 'Google',
            'location': 'Mountain View, CA',
            'match_score': 92,
            'status': 'applied',
            'salary_range': '$180K - $240K'
        },
        {
            'job_id': 'job_002',
            'title': 'Full Stack Developer',
            'company': 'Amazon',
            'location': 'Seattle, WA',
            'match_score': 85,
            'status': 'interested',
            'salary_range': '$160K - $220K'
        },
        {
            'job_id': 'job_003',
            'title': 'DevOps Engineer',
            'company': 'Microsoft',
            'location': 'Redmond, WA',
            'match_score': 78,
            'status': 'matched',
            'salary_range': '$150K - $210K'
        }
    ]
    
    return render_template('jobs/dashboard.html', matches=job_matches)


@jobs_bp.route('/<job_id>')
@login_required
def view_job(job_id):
    """View job details with match analysis"""
    
    job_data = {
        'job_id': job_id,
        'title': 'Senior Software Engineer',
        'company': 'Google',
        'location': 'Mountain View, CA',
        'description': 'We are looking for a senior engineer...',
        'salary_range': '$180K - $240K',
        'match_analysis': {
            'overall_score': 92,
            'matching_skills': ['Python', 'System Design', 'Leadership', 'REST APIs'],
            'missing_skills': ['Kubernetes', 'Go Language'],
            'skill_match_percent': 85,
            'confidence': 94
        },
        'recommendations': [
            'Strong match - Your system design experience aligns perfectly',
            'Learn Go for better opportunities in this role',
            'Your leadership background is highly valued'
        ]
    }
    
    return render_template('jobs/view.html', job=job_data)


@jobs_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_job():
    """Analyze job posting for match"""
    
    job_description = request.form.get('job_description', '')
    job_title = request.form.get('job_title', 'Job')
    
    analysis = {
        'title': job_title,
        'match_score': 78,
        'matching_skills': ['Python', 'REST API'],
        'missing_skills': ['Docker', 'Kubernetes'],
        'gap_percentage': 25
    }
    
    return jsonify(analysis), 200


@jobs_bp.route('/<job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    """Apply to job"""
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('jobs.view_job', job_id=job_id))


@jobs_bp.route('/<job_id>/save', methods=['POST'])
@login_required
def save_job(job_id):
    """Save job for later"""
    flash('Job saved to your collection', 'success')
    return redirect(url_for('jobs.dashboard'))


@jobs_bp.route('/saved')
@login_required
def saved_jobs():
    """View saved jobs"""
    
    saved = [
        {
            'job_id': 'job_001',
            'title': 'Principal Engineer',
            'company': 'Apple',
            'saved_date': '2025-02-08'
        },
        {
            'job_id': 'job_004',
            'title': 'Tech Lead',
            'company': 'Meta',
            'saved_date': '2025-02-07'
        }
    ]
    
    return render_template('jobs/saved.html', jobs=saved)


@jobs_bp.route('/applications')
@login_required
def applications():
    """View submitted applications"""
    
    applications_data = [
        {
            'job_id': 'job_001',
            'title': 'Senior Software Engineer',
            'company': 'Google',
            'applied_date': '2025-02-08',
            'status': 'applied',
            'match_score': 92
        },
        {
            'job_id': 'job_002',
            'title': 'Full Stack Developer',
            'company': 'Amazon',
            'applied_date': '2025-02-07',
            'status': 'interview',
            'match_score': 85
        }
    ]
    
    return render_template('jobs/applications.html', applications=applications_data)


@jobs_bp.route('/<job_id>/track')
@login_required
def track_application(job_id):
    """Track application progress"""
    
    timeline = [
        {'date': '2025-02-08', 'status': 'Applied', 'icon': 'check'},
        {'date': '2025-02-10', 'status': 'Resume Reviewed', 'icon': 'hourglass'},
        {'date': 'Pending', 'status': 'Phone Screen', 'icon': 'minus'},
        {'date': 'Pending', 'status': 'Technical Interview', 'icon': 'minus'},
        {'date': 'Pending', 'status': 'Offer', 'icon': 'minus'}
    ]
    
    return render_template('jobs/track.html', job_id=job_id, timeline=timeline)


@jobs_bp.route('/<job_id>/withdraw', methods=['POST'])
@login_required
def withdraw_application(job_id):
    """Withdraw job application"""
    flash('Application withdrawn', 'info')
    return redirect(url_for('jobs.applications'))
