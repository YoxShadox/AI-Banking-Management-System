from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction
from datetime import datetime, timedelta
import random

# Create blueprint
savings_bp = Blueprint('savings', __name__, url_prefix='/savings')
credit_bp = Blueprint('credit', __name__, url_prefix='/credit')

# ========== SAVINGS ROUTES ==========

@savings_bp.route('/dashboard')
@login_required
def savings_dashboard():
    """Savings management dashboard"""
    user_accounts = Account.query.filter_by(user_id=current_user.id, account_type='SAVINGS').all()
    
    total_savings = sum(acc.balance for acc in user_accounts) if user_accounts else 0
    
    # Calculate interest earned (for demo: 4% annual)
    annual_interest_rate = 0.04
    monthly_interest = total_savings * (annual_interest_rate / 12)
    yearly_interest = total_savings * annual_interest_rate
    
    # Get recent savings deposits
    recent_deposits = Transaction.query.filter_by(
        user_id=current_user.id,
        transaction_type='DEPOSIT',
        status='COMPLETED'
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    savings_plans = [
        {'name': 'Emergency Fund', 'target': 10000, 'current': total_savings * 0.3, 'goal_months': 12},
        {'name': 'Vacation', 'target': 5000, 'current': total_savings * 0.2, 'goal_months': 6},
        {'name': 'Retirement', 'target': 100000, 'current': total_savings * 0.5, 'goal_months': 240},
    ]
    
    stats = {
        'total_savings': total_savings,
        'monthly_interest': monthly_interest,
        'yearly_interest': yearly_interest,
        'accounts_count': len(user_accounts),
        'annual_rate': '4.0%'
    }
    
    return render_template('savings/dashboard.html', 
                         stats=stats, 
                         accounts=user_accounts,
                         plans=savings_plans,
                         recent_deposits=recent_deposits)

@savings_bp.route('/products')
@login_required
def products():
    """Browse savings products"""
    products_list = [
        {
            'id': 1,
            'name': 'Regular Savings Account',
            'rate': '4.0%',
            'description': 'Flexible savings with 4% annual interest',
            'min_balance': 0,
            'features': ['No lock-in period', 'Monthly interest', 'Unlimited deposits']
        },
        {
            'id': 2,
            'name': 'Fixed Deposit - 1 Year',
            'rate': '5.5%',
            'description': '5.5% return on 1-year fixed deposits',
            'min_balance': 1000,
            'features': ['Guaranteed returns', 'Auto-renewal options', 'Tax-saving options']
        },
        {
            'id': 3,
            'name': 'Senior Citizen Savings',
            'rate': '5.75%',
            'description': 'Premium rates for senior citizens',
            'min_balance': 1000,
            'features': ['Higher interest rates', 'Priority service', 'Flexible withdrawal']
        },
    ]
    
    return render_template('savings/products.html', products=products_list)

@savings_bp.route('/recurring-deposit', methods=['GET', 'POST'])
@login_required
def recurring_deposit():
    """Setup recurring deposits"""
    user_accounts = Account.query.filter_by(user_id=current_user.id, account_type='SAVINGS').all()
    
    if request.method == 'POST':
        amount = request.form.get('amount', 0, type=float)
        frequency = request.form.get('frequency', 'MONTHLY')
        duration = request.form.get('duration', 12, type=int)
        
        if amount <= 0 or duration <= 0:
            flash('Invalid amount or duration', 'danger')
            return render_template('savings/recurring_deposit.html', accounts=user_accounts)
        
        flash(f'✓ Recurring deposit of ${amount} set up ({frequency} for {duration} months)', 'success')
        return redirect(url_for('savings.savings_dashboard'))
    
    return render_template('savings/recurring_deposit.html', accounts=user_accounts)

# ========== CREDIT ROUTES ==========

@credit_bp.route('/dashboard')
@login_required
def credit_dashboard():
    """Credit management dashboard"""
    # Mock credit data
    credit_lines = [
        {
            'id': 1,
            'type': 'Personal Loan',
            'limit': 50000,
            'used': 25000,
            'available': 25000,
            'rate': '8.5%',
            'status': 'ACTIVE',
            'emi': 5250
        },
        {
            'id': 2,
            'type': 'Credit Card',
            'limit': 100000,
            'used': 35000,
            'available': 65000,
            'rate': '15.99%',
            'status': 'ACTIVE',
            'min_payment': 3500
        }
    ]
    
    total_credit_limit = sum(line['limit'] for line in credit_lines)
    total_used = sum(line['used'] for line in credit_lines)
    total_available = sum(line['available'] for line in credit_lines)
    credit_score = 750  # Mock credit score
    
    # Recent transactions
    recent_transactions = [
        {'date': '2026-02-09', 'description': 'EMI Payment', 'amount': 5250, 'type': 'payment'},
        {'date': '2026-02-08', 'description': 'Credit Card Purchase', 'amount': 2150, 'type': 'charge'},
    ]
    
    stats = {
        'credit_score': credit_score,
        'credit_score_status': 'Excellent' if credit_score >= 750 else 'Good' if credit_score >= 650 else 'Fair',
        'total_limit': total_credit_limit,
        'total_used': total_used,
        'total_available': total_available,
        'utilization_percent': round((total_used / total_credit_limit) * 100) if total_credit_limit > 0 else 0,
        'outstanding_emi': 5250 + 3500  # Sum of EMI payments
    }
    
    return render_template('credit/dashboard.html',
                         stats=stats,
                         credit_lines=credit_lines,
                         recent_transactions=recent_transactions)

@credit_bp.route('/apply-loan', methods=['GET', 'POST'])
@login_required
def apply_loan():
    """Apply for personal loan"""
    if request.method == 'POST':
        amount = request.form.get('amount', 0, type=float)
        tenure = request.form.get('tenure', 12, type=int)
        purpose = request.form.get('purpose', '')
        
        # Calculate EMI: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        # Where r = monthly rate (annual rate / 12 / 100)
        annual_rate = 8.5
        monthly_rate = annual_rate / 12 / 100
        n = tenure
        
        if monthly_rate == 0:
            emi = amount / n
        else:
            emi = amount * monthly_rate * ((1 + monthly_rate) ** n) / (((1 + monthly_rate) ** n) - 1)
        
        if amount <= 0 or tenure <= 0:
            flash('Invalid loan amount or tenure', 'danger')
            return render_template('credit/apply_loan.html')
        
        flash(f'✓ Loan application submitted! Estimated EMI: ${emi:,.2f}', 'success')
        return redirect(url_for('credit.credit_dashboard'))
    
    return render_template('credit/apply_loan.html')

@credit_bp.route('/credit-cards')
@login_required
def credit_cards():
    """Browse credit card options"""
    cards = [
        {
            'id': 1,
            'name': 'Premium Credit Card',
            'limit': 100000,
            'rate': '15.99%',
            'annual_fee': 500,
            'rewards': '2% cashback on all purchases',
            'benefits': ['Lounge access', 'Travel insurance', 'Purchase protection']
        },
        {
            'id': 2,
            'name': 'Silver Credit Card',
            'limit': 50000,
            'rate': '16.99%',
            'annual_fee': 0,
            'rewards': '1% cashback',
            'benefits': ['Basic insurance', 'EMI options', 'Bill payment rewards']
        },
        {
            'id': 3,
            'name': 'Business Credit Card',
            'limit': 500000,
            'rate': '12.99%',
            'annual_fee': 2000,
            'rewards': '3% cashback on business purchases',
            'benefits': ['Business reporting', 'Higher limits', 'Priority support']
        },
    ]
    
    return render_template('credit/cards.html', cards=cards)

@credit_bp.route('/pay-bill', methods=['GET', 'POST'])
@login_required
def pay_bill():
    """Pay credit bill/EMI"""
    if request.method == 'POST':
        amount = request.form.get('amount', 0, type=float)
        bill_type = request.form.get('bill_type', 'CREDIT_CARD')
        
        if amount <= 0:
            flash('Invalid payment amount', 'danger')
            return render_template('credit/pay_bill.html')
        
        # Record transaction
        flash(f'✓ Payment of ${amount:,.2f} processed successfully!', 'success')
        return redirect(url_for('credit.credit_dashboard'))
    
    return render_template('credit/pay_bill.html')

# ========== API ENDPOINTS ==========

@credit_bp.route('/api/credit-score')
@login_required
def api_credit_score():
    """Get credit score"""
    return jsonify({
        'score': 750,
        'status': 'Excellent',
        'change': '+25 points this month'
    })

@savings_bp.route('/api/interest-calculator', methods=['POST'])
@login_required
def api_interest_calculator():
    """Calculate interest on savings"""
    data = request.get_json()
    principal = data.get('principal', 0)
    rate = data.get('rate', 4.0)
    months = data.get('months', 12)
    
    interest = (principal * rate / 100) * (months / 12)
    total = principal + interest
    
    return jsonify({
        'principal': principal,
        'interest': round(interest, 2),
        'total': round(total, 2)
    })
