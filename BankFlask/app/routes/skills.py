"""
Skills Management and Analysis Routes
Handles skill extraction, proficiency tracking, gap analysis
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')


@skills_bp.route('/')
@login_required
def dashboard():
    """Skills dashboard with visualization"""
    
    skills_data = [
        {'name': 'Python', 'proficiency': 85, 'category': 'programming', 'demand': 95, 'growth': 92},
        {'name': 'React', 'proficiency': 78, 'category': 'framework', 'demand': 88, 'growth': 90},
        {'name': 'AWS', 'proficiency': 72, 'category': 'cloud', 'demand': 92, 'growth': 95},
        {'name': 'Docker', 'proficiency': 65, 'category': 'devops', 'demand': 85, 'growth': 88},
        {'name': 'Leadership', 'proficiency': 70, 'category': 'soft', 'demand': 85, 'growth': 80},
    ]
    
    return render_template('skills/dashboard.html', skills=skills_data)


@skills_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_skill():
    """Add new skill manually"""
    
    if request.method == 'POST':
        skill_name = request.form.get('skill_name')
        proficiency = request.form.get('proficiency', 50)
        
        flash(f'Skill "{skill_name}" added successfully', 'success')
        return redirect(url_for('skills.dashboard'))
    
    return render_template('skills/add.html')


@skills_bp.route('/<skill_name>')
@login_required
def view_skill(skill_name):
    """View detailed skill information"""
    
    skill_data = {
        'name': skill_name,
        'proficiency': 75,
        'category': 'programming',
        'market_demand': 92,
        'growth_potential': 88,
        'current_job_roles': ['Senior Developer', 'Tech Lead', 'Architect'],
        'learning_resources': [
            {'title': 'Advanced Course', 'platform': 'Udemy', 'hours': 30},
            {'title': 'Official Documentation', 'platform': 'Official', 'hours': 20}
        ]
    }
    
    return render_template('skills/view.html', skill=skill_data)


@skills_bp.route('/gap-analysis', methods=['GET', 'POST'])
@login_required
def gap_analysis():
    """Analyze skill gap for target role"""
    
    gap_data = {
        'target_role': 'Senior Full Stack Engineer',
        'completion': 70,
        'matching_skills': ['Python', 'React', 'Git'],
        'missing_skills': ['Docker', 'Kubernetes', 'GraphQL'],
        'excess_skills': ['Excel', 'PowerPoint'],
        'recommendations': [
            'Complete Docker fundamental course',
            'Build 2 containerized projects',
            'Study Kubernetes architecture'
        ]
    }
    
    return render_template('skills/gap-analysis.html', gap=gap_data)


@skills_bp.route('/endorsements/<skill_name>', methods=['GET', 'POST'])
@login_required
def manage_endorsements(skill_name):
    """View and manage skill endorsements"""
    
    endorsements = [
        {'endorser': 'Alice Johnson', 'role': 'Former Manager'},
        {'endorser': 'Bob Smith', 'role': 'Colleague'},
        {'endorser': 'Carol White', 'role': 'Team Lead'}
    ]
    
    return render_template('skills/endorsements.html', 
                         skill_name=skill_name, 
                         endorsements=endorsements)


@skills_bp.route('/trending')
@login_required
def trending():
    """Trending skills in market"""
    
    trending_skills = [
        {'name': 'Machine Learning', 'demand': 98, 'growth': 95, 'avg_salary': 180000},
        {'name': 'Cloud Architecture', 'demand': 92, 'growth': 90, 'avg_salary': 165000},
        {'name': 'DevOps', 'demand': 88, 'growth': 85, 'avg_salary': 155000},
        {'name': 'CUDA/GPU Programming', 'demand': 85, 'growth': 92, 'avg_salary': 175000}
    ]
    
    return render_template('skills/trending.html', trending=trending_skills)
