"""
Learning Path Management Routes
Handles AI-generated learning roadmaps and progress tracking
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

learning_bp = Blueprint('learning', __name__, url_prefix='/learning-paths')


@learning_bp.route('/')
@login_required
def dashboard():
    """Learning paths overview"""
    
    paths = [
        {
            'path_id': 'path_001',
            'title': 'Path to Senior Software Engineer',
            'role': 'Senior Software Engineer',
            'progress': 45,
            'duration_weeks': 16,
            'status': 'active',
            'milestones_completed': 3,
            'milestones_total': 8
        },
        {
            'path_id': 'path_002',
            'title': 'Cloud Architecture Mastery',
            'role': 'Cloud Architect',
            'progress': 20,
            'duration_weeks': 12,
            'status': 'active',
            'milestones_completed': 1,
            'milestones_total': 6
        }
    ]
    
    return render_template('learning/dashboard.html', paths=paths)


@learning_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Generate AI learning path for target role"""
    
    if request.method == 'POST':
        target_role = request.form.get('target_role')
        
        flash(f'Learning path to "{target_role}" created successfully', 'success')
        return redirect(url_for('learning.view', path_id='path_new_123'))
    
    return render_template('learning/create.html')


@learning_bp.route('/<path_id>')
@login_required
def view(path_id):
    """View learning path with milestones"""
    
    path_data = {
        'path_id': path_id,
        'title': 'Path to Senior Software Engineer',
        'target_role': 'Senior Software Engineer',
        'progress': 45,
        'total_duration_weeks': 16,
        'completed_weeks': 7,
        'milestones': [
            {
                'order': 1,
                'title': 'Master Core Architecture Patterns',
                'status': 'completed',
                'duration_weeks': 4,
                'resources': [
                    {'type': 'course', 'title': 'Design Patterns Masterclass', 'platform': 'Udemy'},
                    {'type': 'book', 'title': 'Clean Architecture', 'author': 'Robert Martin'}
                ]
            },
            {
                'order': 2,
                'title': 'Advanced System Design',
                'status': 'in_progress',
                'duration_weeks': 6,
                'resources': [
                    {'type': 'course', 'title': 'System Design Interview Prep', 'platform': 'Educative'},
                    {'type': 'project', 'title': 'Build scalable microservices'}
                ]
            },
            {
                'order': 3,
                'title': 'Leadership & Mentoring Skills',
                'status': 'not_started',
                'duration_weeks': 4,
                'resources': [
                    {'type': 'course', 'title': 'Engineering Leadership', 'platform': 'LinkedIn Learning'},
                    {'type': 'project', 'title': 'Mentor junior engineer'}
                ]
            },
            {
                'order': 4,
                'title': 'Build Portfolio Project',
                'status': 'not_started',
                'duration_weeks': 2,
                'resources': [
                    {'type': 'project', 'title': 'Distributed system implementation'}
                ]
            }
        ]
    }
    
    return render_template('learning/view.html', path=path_data)


@learning_bp.route('/<path_id>/milestone/<milestone_id>/complete', methods=['POST'])
@login_required
def complete_milestone(path_id, milestone_id):
    """Mark milestone as completed"""
    flash('Milestone marked as completed!', 'success')
    return redirect(url_for('learning.view', path_id=path_id))


@learning_bp.route('/<path_id>/resources')
@login_required
def view_resources(path_id):
    """View all resources for learning path"""
    
    resources = [
        {'title': 'Design Patterns Masterclass', 'type': 'course', 'platform': 'Udemy', 'hours': 25},
        {'title': 'Clean Architecture', 'type': 'book', 'platform': 'Amazon', 'hours': 15},
        {'title': 'System Design Interview Prep', 'type': 'course', 'platform': 'Educative', 'hours': 20}
    ]
    
    return render_template('learning/resources.html', path_id=path_id, resources=resources)


@learning_bp.route('/<path_id>/adjust', methods=['GET', 'POST'])
@login_required
def adjust_pace():
    """Adjust learning pace and preferences"""
    
    if request.method == 'POST':
        pace = request.form.get('pace')
        flash(f'Learning pace adjusted to {pace}', 'success')
        return redirect(url_for('learning.dashboard'))
    
    return render_template('learning/adjust.html')


@learning_bp.route('/<path_id>/pause', methods=['POST'])
@login_required
def pause_path(path_id):
    """Pause learning path"""
    flash('Learning path paused. You can resume it anytime.', 'info')
    return redirect(url_for('learning.dashboard'))


@learning_bp.route('/<path_id>/resume', methods=['POST'])
@login_required
def resume_path(path_id):
    """Resume paused learning path"""
    flash('Learning path resumed!', 'success')
    return redirect(url_for('learning.view', path_id=path_id))
