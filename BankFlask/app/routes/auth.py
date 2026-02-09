from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, Account
import random
import string
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Security: Track login attempts
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 15  # minutes

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_account_number():
    """Generate unique 16-digit account number"""
    while True:
        account_num = ''.join(random.choices(string.digits, k=16))
        if not User.query.filter_by(account_number=account_num).first() and not Account.query.filter_by(account_number=account_num).first():
            return account_num

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_username(username):
    """Validate username format"""
    # 3-20 chars, alphanumeric and underscore only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def is_strong_password(password):
    """Validate password strength"""
    # At least 8 chars, uppercase, lowercase, number, special char
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    return True, "Valid"

def is_valid_phone(phone):
    """Validate phone number format"""
    phone = ''.join(c for c in phone if c.isdigit())
    return len(phone) >= 10

def check_login_attempts(username):
    """Check if user is locked out due to too many failed attempts"""
    if username not in login_attempts:
        return True
    
    attempts, last_attempt = login_attempts[username]
    time_since_attempt = datetime.now() - last_attempt
    
    if time_since_attempt > timedelta(minutes=LOCKOUT_TIME):
        del login_attempts[username]
        return True
    
    if attempts >= MAX_ATTEMPTS:
        return False
    
    return True

def record_failed_attempt(username):
    """Record a failed login attempt"""
    if username not in login_attempts:
        login_attempts[username] = [1, datetime.now()]
    else:
        attempts, _ = login_attempts[username]
        login_attempts[username] = [attempts + 1, datetime.now()]

@auth_bp.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('auth/login.html')
        
        # Check login attempts
        if not check_login_attempts(username):
            flash('Too many failed login attempts. Please try again in 15 minutes.', 'danger')
            return render_template('auth/login.html')
        
        # Authenticate user
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            record_failed_attempt(username)
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'warning')
            return render_template('auth/login.html')
        
        # Successful login
        login_user(user, remember=remember)
        
        # Clear login attempts
        if username in login_attempts:
            del login_attempts[username]
        
        flash(f'Welcome back, {user.first_name}! 👋', 'success')
        next_page = request.args.get('next')
        
        # Validate next_page for security
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation: Required fields
        if not all([username, email, first_name, last_name, password, confirm_password, phone]):
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Username format
        if not is_valid_username(username):
            flash('Username must be 3-20 characters, alphanumeric and underscore only', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Email format
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Name length
        if len(first_name) < 2 or len(last_name) < 2:
            flash('First and last name must be at least 2 characters', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Phone format
        if not is_valid_phone(phone):
            flash('Please enter a valid phone number (at least 10 digits)', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Password strength
        is_strong, message = is_strong_password(password)
        if not is_strong:
            flash(f'Password requirements: {message}', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Username not taken
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')
        
        # Validation: Email not registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login or use another email.', 'danger')
            return render_template('auth/register.html')
        
        try:
            # Create user account
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                account_number=generate_account_number(),
                email_verified=False
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create default savings account
            savings_account = Account(
                user_id=user.id,
                account_type='SAVINGS',
                account_name='My Savings Account',
                balance=5000.0,
                account_number=generate_account_number(),
                currency='USD'
            )
            db.session.add(savings_account)
            
            # Create default checking account
            checking_account = Account(
                user_id=user.id,
                account_type='CHECKING',
                account_name='My Checking Account',
                balance=2000.0,
                account_number=generate_account_number(),
                currency='USD'
            )
            db.session.add(checking_account)
            
            db.session.commit()
            
            flash('✓ Account created successfully! You now have a Savings and Checking account. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash('You have been logged out successfully 👋', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not all([first_name, last_name]):
            flash('First and last name are required', 'danger')
            return redirect(url_for('auth.profile'))
        
        if phone and not is_valid_phone(phone):
            flash('Invalid phone number', 'danger')
            return redirect(url_for('auth.profile'))
        
        try:
            current_user.first_name = first_name
            current_user.last_name = last_name
            if phone:
                current_user.phone = phone
            current_user.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('✓ Profile updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password == current_password:
            flash('New password must be different from current password', 'danger')
            return render_template('auth/change_password.html')
        
        is_strong, message = is_strong_password(new_password)
        if not is_strong:
            flash(f'New password requirements: {message}', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('auth/change_password.html')
        
        try:
            current_user.set_password(new_password)
            current_user.updated_at = datetime.utcnow()
            db.session.commit()
            flash('✓ Password changed successfully', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error changing password: {str(e)}', 'danger')
            return render_template('auth/change_password.html')
    
    return render_template('auth/change_password.html')
