from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.ai import ai_bp
    from app.routes.accounts import accounts_bp
    from app.routes.products import products_bp
    from app.routes.planning import planning_bp
    from app.routes.investments import investments_bp
    from app.routes.advisor import advisor_bp
    from app.routes.admin import admin_bp
    from app.routes.savings_credit import savings_bp, credit_bp
    from app.api_blueprint import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(advisor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(credit_bp)
    app.register_blueprint(api_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
