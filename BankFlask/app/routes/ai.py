from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import AIInsight, Transaction
from app import db
from datetime import datetime, timedelta
import os

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

def generate_ai_insights(user):
    """Generate AI insights based on user's transactions"""
    insights = []
    
    # Get recent transactions
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.created_at >= thirty_days_ago
    ).all()
    
    if not transactions:
        return insights
    
    # Analyze spending patterns
    total_spending = sum(t.amount for t in transactions if t.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
    total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'DEPOSIT')
    
    # Spending pattern insight
    if total_spending > total_deposits * 0.8:
        insights.append(AIInsight(
            user_id=user.id,
            insight_type='SPENDING_PATTERN',
            title='High Spending Detected',
            description=f'Your spending (${total_spending:.2f}) is {(total_spending/total_deposits*100):.0f}% of your income. Consider reducing discretionary expenses.',
            confidence=0.85,
            action_items=['Track daily expenses', 'Set spending limits', 'Review subscriptions']
        ))
    
    # Saving recommendation
    if total_deposits > 0:
        insights.append(AIInsight(
            user_id=user.id,
            insight_type='SAVING_RECOMMENDATION',
            title='Savings Goal Recommendation',
            description=f'Based on your income of ${total_deposits:.2f}, consider saving ${total_deposits*0.2:.2f} monthly (20% rule).',
            confidence=0.75,
            action_items=['Open savings account', 'Set automatic transfers', 'Review investment options']
        ))
    
    # Account health insight
    insights.append(AIInsight(
        user_id=user.id,
        insight_type='ACCOUNT_HEALTH',
        title='Account Activity Status',
        description=f'You have {len(transactions)} transactions in the last 30 days. Your account is active and healthy.',
        confidence=0.95,
        action_items=['Continue monitoring', 'Review statements regularly']
    ))
    
    return insights

@ai_bp.route('/dashboard')
@login_required
def dashboard():
    # Get or generate insights
    insights = AIInsight.query.filter_by(user_id=current_user.id)\
        .order_by(AIInsight.created_at.desc()).limit(10).all()
    
    if not insights:
        new_insights = generate_ai_insights(current_user)
        db.session.add_all(new_insights)
        db.session.commit()
        insights = new_insights
    
    # Get transactions for analysis
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= thirty_days_ago
    ).all()
    
    # Calculate statistics
    spending = sum(t.amount for t in transactions if t.transaction_type in ['WITHDRAWAL', 'PAYMENT'])
    deposits = sum(t.amount for t in transactions if t.transaction_type == 'DEPOSIT')
    
    return render_template('ai/dashboard.html',
        insights=insights,
        spending=spending,
        deposits=deposits,
        transaction_count=len(transactions)
    )

@ai_bp.route('/insights')
@login_required
def insights():
    insights = AIInsight.query.filter_by(user_id=current_user.id)\
        .order_by(AIInsight.created_at.desc()).all()
    
    return render_template('ai/insights.html', insights=insights)

@ai_bp.route('/api/recommendations')
@login_required
def api_recommendations():
    # Generate personalized recommendations
    insights = AIInsight.query.filter_by(user_id=current_user.id).limit(5).all()
    
    return jsonify([{
        'id': i.id,
        'type': i.insight_type,
        'title': i.title,
        'description': i.description,
        'confidence': i.confidence,
        'actions': i.action_items or []
    } for i in insights])

@ai_bp.route('/api/mark-read/<int:insight_id>', methods=['POST'])
@login_required
def mark_read(insight_id):
    insight = AIInsight.query.get_or_404(insight_id)
    if insight.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    insight.is_read = True
    db.session.commit()
    return jsonify({'success': True})
