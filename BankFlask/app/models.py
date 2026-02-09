from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with proper backref configuration
    accounts = db.relationship('Account', backref='owner', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='user', lazy=True, cascade='all, delete-orphan')
    ai_insights = db.relationship('AIInsight', back_populates='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password securely"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def total_balance(self):
        """Get total balance across all accounts"""
        return sum(account.balance for account in self.accounts) if self.accounts else 0.0
    
    @property
    def recent_transactions(self):
        """Get last 5 transactions"""
        return Transaction.query.filter_by(user_id=self.id).order_by(Transaction.created_at.desc()).limit(5).all()

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    account_type = db.Column(db.String(50), default='SAVINGS')  # SAVINGS, CHECKING, INVESTMENT
    account_name = db.Column(db.String(100), nullable=False, default='My Account')
    balance = db.Column(db.Float, default=5000.0)
    currency = db.Column(db.String(10), default='USD')
    account_number = db.Column(db.String(16), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, INACTIVE, FROZEN
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def formatted_balance(self):
        return f"${self.balance:,.2f}"
    
    @property
    def account_type_display(self):
        return self.account_type.replace('_', ' ').title()

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:12])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # DEPOSIT, WITHDRAWAL, TRANSFER, PAYMENT
    status = db.Column(db.String(20), default='COMPLETED')  # PENDING, COMPLETED, FAILED
    description = db.Column(db.Text)
    from_account = db.Column(db.String(50))
    to_account = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', back_populates='transactions')
    
    @property
    def formatted_amount(self):
        return f"${self.amount:,.2f}"
    
    @property
    def status_badge(self):
        badges = {
            'COMPLETED': 'badge-success',
            'PENDING': 'badge-warning',
            'FAILED': 'badge-danger'
        }
        return badges.get(self.status, 'badge-secondary')

class AIInsight(db.Model):
    __tablename__ = 'ai_insights'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    insight_type = db.Column(db.String(100))  # SPENDING_PATTERN, SAVING_RECOMMENDATION, FRAUD_ALERT
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    confidence = db.Column(db.Float)  # 0-1
    action_items = db.Column(db.JSON)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', back_populates='ai_insights')
