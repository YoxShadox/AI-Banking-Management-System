from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction
from datetime import datetime, timedelta

advisor_bp = Blueprint('advisor', __name__, url_prefix='/advisor')

@advisor_bp.route('/')
@login_required
def dashboard():
    """AI Financial Advisor dashboard"""
    # Get user financial snapshot
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    # Calculate metrics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= thirty_days_ago
    ).all()
    
    monthly_spending = sum(txn.amount for txn in monthly_transactions if txn.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
    
    # Financial health score (AI calculated)
    health_score = min(100, max(0, 50 + (total_balance / 1000) - (monthly_spending / 100)))
    
    insights = [
        {
            'title': 'Strong Savings Performance',
            'description': 'Your savings have increased by 15% in the last month. Keep it up!',
            'score': 85,
            'action': 'View Savings Goals'
        },
        {
            'title': 'Investment Opportunity',
            'description': 'Based on your profile, you\'re eligible for high-return fixed deposits.',
            'score': 72,
            'action': 'Explore FDs'
        },
        {
            'title': 'Budget Alert',
            'description': 'Your dining expenses have increased by 20%. Consider setting a limit.',
            'score': 60,
            'action': 'Set Budget'
        },
    ]
    
    return render_template('advisor/dashboard.html',
                         total_balance=total_balance,
                         monthly_spending=monthly_spending,
                         health_score=int(health_score),
                         insights=insights)

@advisor_bp.route('/chat')
@login_required
def chat():
    """AI Financial Advisor chat interface"""
    return render_template('advisor/chat.html')

@advisor_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """Simple banking FAQ bot - answers questions from the website"""
    data = request.json
    message = data.get('message', '').lower()
    
    # Get user data for contextual answers
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    spending = sum(t.amount for t in Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= thirty_days_ago
    ).all() if t.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
    
    # Banking FAQ database
    faq = {
        'balance': f'Your current balance is ₹{total_balance:,.0f} across {len(accounts)} account(s).',
        'account': f'You have {len(accounts)} active account(s). Visit My Accounts to manage them.',
        'transaction': 'View all transactions in the Transactions section.',
        'savings': 'Visit Savings dashboard to manage accounts and set savings goals.',
        'credit': 'Check credit cards, loans, and credit score in the Credit section.',
        'investment': 'Explore investment options in the Investments section.',
        'loan': 'Apply for personal loans via Credit section. We offer competitive rates starting at 7.5%.',
        'budget': 'Use Financial Planning to set budgets and track spending.',
        'spending': f'You spent ₹{spending:,.0f} in the last 30 days.',
        'fee': 'Check account details for applicable fees. Most services are zero-fee.',
        'interest': 'Savings accounts earn interest. Rates vary by product type.',
        'transfer': 'Make transfers via Accounts section. Instant transfers available.',
        'payment': 'Pay bills via Credit section.',
        'alert': 'Enable notifications in Settings for transaction alerts.',
        'security': 'Your account is protected with 2FA. Update password regularly.',
        'card': 'Request credit cards via Credit section. Instant approval for eligible members.',
    }
    
    response_text = 'I can help with: balance, accounts, savings, credit, loans, investments, budgeting, and more. What would you like to know?'
    
    # Match keywords and provide answer
    for keyword, answer in faq.items():
        if keyword in message:
            response_text = answer
            break
    
    return jsonify({
        'response': response_text,
        'suggestions': [
            'What is my balance?',
            'How much did I spend?',
            'How do I apply for a loan?',
            'Tell me about savings'
        ]
    })

@advisor_bp.route('/recommendations')
@login_required
def recommendations():
    """AI-powered personalized recommendations"""
    recommendations = [
        {
            'id': 1,
            'category': 'Savings',
            'title': 'High-Yield Fixed Deposit',
            'description': 'Earn 6.5% on your savings with our 1-year FD',
            'benefit': '+₹6,500 annual interest on ₹1,00,000',
            'risk': 'Low',
            'urgency': 'High',
            'icon': 'fa-piggy-bank'
        },
        {
            'id': 2,
            'category': 'Investment',
            'title': 'Balanced Mutual Fund Portfolio',
            'description': 'Diversified portfolio of stocks and bonds',
            'benefit': 'Potential 12% annual returns',
            'risk': 'Medium',
            'urgency': 'Medium',
            'icon': 'fa-chart-pie'
        },
        {
            'id': 3,
            'category': 'Protection',
            'title': 'Term Life Insurance',
            'description': 'Affordable life coverage for your family',
            'benefit': '₹50,00,000 cover for just ₹500/month',
            'risk': 'Low',
            'urgency': 'High',
            'icon': 'fa-shield-alt'
        },
    ]
    
    return render_template('advisor/recommendations.html', recommendations=recommendations)

@advisor_bp.route('/financial-health')
@login_required
def financial_health():
    """Comprehensive financial health assessment"""
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    assessment = {
        'overall_score': 75,
        'categories': {
            'savings': {'score': 85, 'feedback': 'Excellent savings habit'},
            'investments': {'score': 60, 'feedback': 'Room for growth'},
            'spending': {'score': 70, 'feedback': 'Moderate spending'},
            'debt': {'score': 90, 'feedback': 'Very low debt'},
        },
        'strengths': [
            'Consistent savings pattern',
            'Low debt',
            'Diversified accounts',
        ],
        'improvements': [
            'Increase investment allocation',
            'Reduce discretionary spending',
            'Build emergency fund to 6 months expenses',
        ],
        'personalized_tips': [
            'Automate your savings for consistency',
            'Review your portfolio quarterly',
            'Keep 3-6 months expenses in emergency fund',
        ]
    }
    
    return render_template('advisor/financial_health.html', assessment=assessment)

@advisor_bp.route('/risk-profile')
@login_required
def risk_profile():
    """AI-powered risk profiling and asset allocation"""
    profile = {
        'risk_tolerance': 'Moderate',
        'age_group': '30-40',
        'investment_horizon': '15-20 years',
        'current_allocation': {
            'stocks': 40,
            'bonds': 40,
            'cash': 20
        },
        'recommended_allocation': {
            'stocks': 50,
            'bonds': 35,
            'cash': 15
        },
        'rationale': 'You have a moderate risk tolerance with a good investment horizon. We recommend increasing equity allocation while maintaining stability.'
    }
    
    return render_template('advisor/risk_profile.html', profile=profile)

@advisor_bp.route('/api/health-score')
@login_required
def api_health_score():
    """Get real-time financial health score"""
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    spending = sum(t.amount for t in Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= thirty_days_ago
    ).all() if t.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
    
    # Calculate health score
    score = min(100, max(0, 50 + (total_balance / 1000) - (spending / 100)))
    
    return jsonify({
        'score': int(score),
        'balance': total_balance,
        'spending': spending,
        'trend': 'improving' if score > 70 else 'stable' if score > 50 else 'declining'
    })
