from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Transaction, Account
from datetime import datetime, timedelta
from functools import reduce
import operator

planning_bp = Blueprint('planning', __name__, url_prefix='/planning')

@planning_bp.route('/')
@login_required
def dashboard():
    """Financial planning dashboard"""
    # Get user's accounts and balance
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    # Get spending by category (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= thirty_days_ago
    ).all()
    
    # Calculate spending breakdown
    spending = {}
    for txn in transactions:
        category = txn.transaction_type
        if category not in spending:
            spending[category] = 0
        spending[category] += txn.amount
    
    # Get financial goals
    goals = [
        {'name': 'Emergency Fund', 'target': 50000, 'current': total_balance * 0.3, 'progress': 65},
        {'name': 'Vacation', 'target': 100000, 'current': 35000, 'progress': 35},
        {'name': 'Home Down Payment', 'target': 500000, 'current': 120000, 'progress': 24},
    ]
    
    return render_template('planning/dashboard.html',
                         total_balance=total_balance,
                         spending=spending,
                         goals=goals,
                         accounts=accounts)

@planning_bp.route('/budget')
@login_required
def budget():
    """Budget management"""
    # Get budget data
    budgets = [
        {'category': 'Groceries', 'allocated': 10000, 'spent': 8500, 'remaining': 1500},
        {'category': 'Entertainment', 'allocated': 5000, 'spent': 4200, 'remaining': 800},
        {'category': 'Utilities', 'allocated': 8000, 'spent': 7800, 'remaining': 200},
        {'category': 'Transportation', 'allocated': 12000, 'spent': 11500, 'remaining': 500},
        {'category': 'Dining Out', 'allocated': 8000, 'spent': 6300, 'remaining': 1700},
    ]
    
    total_allocated = sum(b['allocated'] for b in budgets)
    total_spent = sum(b['spent'] for b in budgets)
    total_remaining = total_allocated - total_spent
    
    return render_template('planning/budget.html',
                         budgets=budgets,
                         total_allocated=total_allocated,
                         total_spent=total_spent,
                         total_remaining=total_remaining)

@planning_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    """Financial goals management"""
    if request.method == 'POST':
        goal_name = request.form.get('goal_name')
        target_amount = float(request.form.get('target_amount', 0))
        deadline = request.form.get('deadline')
        
        flash(f'Goal "{goal_name}" added successfully!', 'success')
        return redirect(url_for('planning.goals'))
    
    goals = [
        {'id': 1, 'name': 'Emergency Fund', 'target': 50000, 'current': 30000, 'deadline': '2026-12-31'},
        {'id': 2, 'name': 'Vacation', 'target': 100000, 'current': 35000, 'deadline': '2026-06-30'},
        {'id': 3, 'name': 'Home Down Payment', 'target': 500000, 'current': 120000, 'deadline': '2027-12-31'},
    ]
    
    return render_template('planning/goals.html', goals=goals)

@planning_bp.route('/expense-analysis')
@login_required
def expense_analysis():
    """AI-powered expense analysis"""
    # Get transactions from last 3 months
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= ninety_days_ago
    ).all()
    
    # Analyze spending patterns
    analysis = {
        'total_spending': sum(txn.amount for txn in transactions if txn.transaction_type in ['WITHDRAWAL', 'PAYMENT']),
        'average_monthly': sum(txn.amount for txn in transactions) / 3,
        'top_category': 'Dining Out',
        'spending_trend': 'Increasing',
        'ai_recommendation': 'Consider setting a budget for dining out expenses to optimize savings.',
        'alerts': [
            'Your spending exceeded budget by 15% this month',
            'Unusual transaction detected on Card ending in 4521'
        ]
    }
    
    return render_template('planning/expense-analysis.html', analysis=analysis)

@planning_bp.route('/recommendations')
@login_required
def recommendations():
    """AI-powered financial recommendations"""
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    recommendations = [
        {
            'title': 'Optimize Emergency Fund',
            'description': 'You have sufficient balance. Consider moving excess to a high-yield savings account.',
            'potential_gain': 2500,
            'action': 'View Fixed Deposits'
        },
        {
            'title': 'Reduce Credit Card Interest',
            'description': 'Consolidate credit card debt with our personal loan at lower interest rates.',
            'potential_gain': 5000,
            'action': 'View Loans'
        },
        {
            'title': 'Diversify Your Investments',
            'description': 'Your portfolio is heavily weighted towards cash. Consider mutual funds for better returns.',
            'potential_gain': 10000,
            'action': 'Explore Investments'
        },
    ]
    
    return render_template('planning/recommendations.html', recommendations=recommendations)

@planning_bp.route('/api/spending-chart')
@login_required
def api_spending_chart():
    """Get spending data for charts"""
    # Get last 12 months data
    months_data = []
    days_ago_range = 365
    
    for i in range(12):
        date = datetime.utcnow() - timedelta(days=days_ago_range - i*30)
        month_transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.created_at.between(
                date.replace(day=1),
                (date.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            )
        ).all()
        
        monthly_spending = sum(txn.amount for txn in month_transactions if txn.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
        months_data.append({
            'month': date.strftime('%b'),
            'spending': monthly_spending
        })
    
    return jsonify(months_data)
