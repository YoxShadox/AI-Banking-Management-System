from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Account, Transaction, AIInsight
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Get user's accounts
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(account.balance for account in accounts)
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Get AI insights
    insights = AIInsight.query.filter_by(user_id=current_user.id)\
        .order_by(AIInsight.created_at.desc()).limit(5).all()
    
    # Get transaction statistics
    today = datetime.utcnow().date()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    month_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= thirty_days_ago
    ).all()
    
    month_spending = sum(t.amount for t in month_transactions if t.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
    month_deposits = sum(t.amount for t in month_transactions if t.transaction_type == 'DEPOSIT')
    
    # Get unread insights count
    unread_insights = AIInsight.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('dashboard/index.html',
        accounts=accounts,
        total_balance=total_balance,
        recent_transactions=recent_transactions,
        insights=insights,
        unread_insights=unread_insights,
        month_spending=month_spending,
        month_deposits=month_deposits,
        transaction_count=len(recent_transactions)
    )

@dashboard_bp.route('/accounts')
@login_required
def accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/accounts.html', accounts=accounts)

@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html', user=current_user)

@dashboard_bp.route('/api/balance')
@login_required
def api_balance():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'total_balance': sum(account.balance for account in accounts),
        'accounts': [{'type': a.account_type, 'balance': a.balance} for a in accounts]
    })
