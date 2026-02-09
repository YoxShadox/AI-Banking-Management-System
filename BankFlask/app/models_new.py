"""
EduAI Models - Modern AI-first educational platform
Refactored for 2025-level architecture
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import json

class User(UserMixin, db.Model):
    """Student/User model with extended profiles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(500))
    bio = db.Column(db.Text)
    
    # Career info
    current_role = db.Column(db.String(120))
    target_role = db.Column(db.String(120))
    years_experience = db.Column(db.Integer, default=0)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    theme = db.Column(db.String(20), default='dark')  # dark, light
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    skills = db.relationship('Skill', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_paths = db.relationship('LearningPath', backref='user', lazy=True, cascade='all, delete-orphan')
    job_applications = db.relationship('JobApplication', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_insights = db.relationship('AIInsight', backref='user', lazy=True, cascade='all, delete-orphan')
    progress_tracking = db.relationship('ProgressTracking', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def profile_completion(self):
        """Calculate profile completion percentage"""
        fields = [self.bio, self.current_role, self.target_role, self.profile_picture]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)


class Resume(db.Model):
    """Resume uploads with AI processing"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:12])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    
    # Processing status
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    processing_progress = db.Column(db.Integer, default=0)  # 0-100
    error_message = db.Column(db.Text)
    
    # Extracted data
    extracted_text = db.Column(db.Text)
    raw_data = db.Column(db.JSON)  # Structured extraction
    
    # Analysis results
    readability_score = db.Column(db.Float)  # 0-100
    ats_compatibility = db.Column(db.Float)  # 0-100
    impact_score = db.Column(db.Float)  # 0-100
    
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Skill(db.Model):
    """Skills extracted from resume/profile"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), default='technical')  # technical, soft, language, tool
    proficiency = db.Column(db.Integer, default=50)  # 0-100
    endorsements = db.Column(db.Integer, default=0)
    
    # AI analysis
    market_demand = db.Column(db.Float)  # 0-100
    growth_potential = db.Column(db.Float)  # 0-100
    salary_premium = db.Column(db.Float)  # percentage
    
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Skill {self.name}>'


class LearningPath(db.Model):
    """AI-generated personalized learning paths"""
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:12])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    target_role = db.Column(db.String(120))
    
    # Path structure
    milestones = db.Column(db.JSON)  # List of milestones
    estimated_duration_days = db.Column(db.Integer)
    
    # Progress
    progress_percentage = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='active')  # active, paused, completed
    
    # AI generated
    ai_confidence = db.Column(db.Float)  # 0-100
    personalization_score = db.Column(db.Float)  # 0-100
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress_tracking = db.relationship('ProgressTracking', backref='learning_path', lazy=True, cascade='all, delete-orphan')


class ProgressTracking(db.Model):
    """Track learning progress"""
    __tablename__ = 'progress_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False, index=True)
    
    section_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobApplication(db.Model):
    """Job match and application tracking"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:12])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    job_description = db.Column(db.Text)
    
    # AI Match Analysis
    match_score = db.Column(db.Float)  # 0-100
    skill_gap_analysis = db.Column(db.JSON)
    recommended_actions = db.Column(db.JSON)
    
    # Status
    status = db.Column(db.String(50), default='interested')  # interested, applied, interviews, offered, rejected
    
    applied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AIInsight(db.Model):
    """AI-generated insights and recommendations"""
    __tablename__ = 'ai_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    insight_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:12])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    insight_type = db.Column(db.String(100))  # SKILL_DEMAND, CAREER_PATH, LEARNING_RECOMMENDATION, INTERVIEW_TIP
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # AI metadata
    confidence = db.Column(db.Float)  # 0-100
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    action_items = db.Column(db.JSON)
    
    # Engagement
    is_read = db.Column(db.Boolean, default=False)
    is_actioned = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Time-sensitive insights


class Mentor(db.Model):
    """Mentor network profiles"""
    __tablename__ = 'mentors'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:12])
    
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(255))
    company = db.Column(db.String(255))
    photo = db.Column(db.String(500))
    bio = db.Column(db.Text)
    
    # Expertise
    expertise = db.Column(db.JSON)  # List of skills/areas
    experience_years = db.Column(db.Integer)
    
    # Rating
    rating = db.Column(db.Float, default=5.0)  # 0-5
    reviews_count = db.Column(db.Integer, default=0)
    
    # Availability
    hourly_rate = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdminAnalytics(db.Model):
    """Analytics data for admin dashboard"""
    __tablename__ = 'admin_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User metrics
    total_users = db.Column(db.Integer, default=0)
    active_users_today = db.Column(db.Integer, default=0)
    new_users_today = db.Column(db.Integer, default=0)
    
    # Engagement
    total_resumes_processed = db.Column(db.Integer, default=0)
    total_paths_created = db.Column(db.Integer, default=0)
    avg_path_completion = db.Column(db.Float, default=0)  # percentage
    
    # AI metrics
    avg_match_score = db.Column(db.Float, default=0)
    total_insights_generated = db.Column(db.Integer, default=0)
    
    date = db.Column(db.DateTime, default=datetime.utcnow)
