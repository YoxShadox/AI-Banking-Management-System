"""
Mentor Network Management Routes
Handles mentor discovery, booking, and relationship management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

mentors_bp = Blueprint('mentors', __name__, url_prefix='/mentors')


@mentors_bp.route('/')
@login_required
def discover():
    """Discover mentors by expertise"""
    
    mentors = [
        {
            'mentor_id': 'mentor_001',
            'name': 'Sarah Chen',
            'title': 'Senior Software Engineer',
            'company': 'Google',
            'photo': '/static/mentors/sarah.jpg',
            'expertise': ['System Design', 'Python', 'Leadership'],
            'rating': 4.9,
            'reviews': 127,
            'hourly_rate': 150,
            'availability': 'Available'
        },
        {
            'mentor_id': 'mentor_002',
            'name': 'Marcus Johnson',
            'title': 'Engineering Manager',
            'company': 'Amazon',
            'photo': '/static/mentors/marcus.jpg',
            'expertise': ['Cloud Architecture', 'Team Management', 'Hiring'],
            'rating': 4.8,
            'reviews': 89,
            'hourly_rate': 120,
            'availability': 'Available'
        },
        {
            'mentor_id': 'mentor_003',
            'name': 'Lisa Wang',
            'title': 'Principal Architect',
            'company': 'Microsoft',
            'photo': '/static/mentors/lisa.jpg',
            'expertise': ['Enterprise Architecture', 'DevOps', 'Kubernetes'],
            'rating': 4.95,
            'reviews': 156,
            'hourly_rate': 180,
            'availability': 'Limited'
        }
    ]
    
    return render_template('mentors/discover.html', mentors=mentors)


@mentors_bp.route('/<mentor_id>')
@login_required
def view_profile(mentor_id):
    """View mentor profile"""
    
    mentor_data = {
        'mentor_id': mentor_id,
        'name': 'Sarah Chen',
        'title': 'Senior Software Engineer',
        'company': 'Google',
        'bio': 'I help engineers grow through targeted mentoring...',
        'photo': '/static/mentors/sarah.jpg',
        'expertise': ['System Design', 'Python', 'Leadership', 'Scaling Systems'],
        'experience_years': 12,
        'rating': 4.9,
        'reviews': 127,
        'hourly_rate': 150,
        'response_time': '< 1 hour',
        'languages': ['English', 'Mandarin'],
        'availability': [
            'Monday: 6-9 PM PST',
            'Wednesday: 6-9 PM PST',
            'Saturday: 10 AM - 1 PM PST'
        ],
        'recent_reviews': [
            {'reviewer': 'Alex K.', 'rating': 5, 'text': 'Excellent mentor! Very knowledgeable...'},
            {'reviewer': 'Jordan M.', 'rating': 5, 'text': 'Transformed my system design thinking...'}
        ]
    }
    
    return render_template('mentors/profile.html', mentor=mentor_data)


@mentors_bp.route('/recommended')
@login_required
def recommended():
    """Get AI-recommended mentors"""
    
    recommendations = [
        {
            'mentor_id': 'mentor_001',
            'name': 'Sarah Chen',
            'match_reason': 'Expertise in your target role matches 95%',
            'match_score': 95
        },
        {
            'mentor_id': 'mentor_002',
            'name': 'Marcus Johnson',
            'match_reason': 'Your skills align well with their experience',
            'match_score': 88
        }
    ]
    
    return render_template('mentors/recommended.html', recommendations=recommendations)


@mentors_bp.route('/<mentor_id>/book', methods=['GET', 'POST'])
@login_required
def book_session(mentor_id):
    """Book mentoring session"""
    
    if request.method == 'POST':
        session_date = request.form.get('session_date')
        duration = request.form.get('duration')
        topic = request.form.get('topic')
        
        flash('Mentoring session booked! Check your email for confirmation.', 'success')
        return redirect(url_for('mentors.my_sessions'))
    
    return render_template('mentors/book.html', mentor_id=mentor_id)


@mentors_bp.route('/my-sessions')
@login_required
def my_sessions():
    """View user's mentoring sessions"""
    
    sessions = [
        {
            'session_id': 'session_001',
            'mentor_name': 'Sarah Chen',
            'scheduled_date': '2025-02-15',
            'time': '6:00 PM - 7:00 PM PST',
            'topic': 'System Design Patterns',
            'status': 'scheduled',
            'recording_available': False
        },
        {
            'session_id': 'session_002',
            'mentor_name': 'Marcus Johnson',
            'scheduled_date': '2025-02-10',
            'time': '5:00 PM - 6:00 PM PST',
            'topic': 'Career Growth Strategy',
            'status': 'completed',
            'recording_available': True
        }
    ]
    
    return render_template('mentors/sessions.html', sessions=sessions)


@mentors_bp.route('/<session_id>/join')
@login_required
def join_session(session_id):
    """Join mentoring session (video call)"""
    
    session_data = {
        'session_id': session_id,
        'mentor_name': 'Sarah Chen',
        'topic': 'System Design Patterns',
        'meeting_link': 'https://meet.example.com/session_001'
    }
    
    return render_template('mentors/session_join.html', session=session_data)


@mentors_bp.route('/<session_id>/rate', methods=['GET', 'POST'])
@login_required
def rate_session(session_id):
    """Rate mentoring session"""
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        feedback = request.form.get('feedback')
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('mentors.my_sessions'))
    
    return render_template('mentors/rate_session.html', session_id=session_id)


@mentors_bp.route('/search')
@login_required
def search():
    """Search mentors by skills, expertise, or role"""
    
    query = request.args.get('q', '')
    filters = {
        'expertise': request.args.getlist('expertise'),
        'experience_min': request.args.get('experience_min'),
        'experience_max': request.args.get('experience_max'),
        'hourly_rate_max': request.args.get('rate_max')
    }
    
    results = [
        {
            'mentor_id': 'mentor_001',
            'name': 'Sarah Chen',
            'title': 'Senior Software Engineer',
            'expertise': ['System Design', 'Python'],
            'rating': 4.9,
            'hourly_rate': 150
        }
    ]
    
    return render_template('mentors/search.html', results=results, query=query)
