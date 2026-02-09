from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Account
from datetime import datetime

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def dashboard():
    """Browse available banking products"""
    products = {
        'loans': [
            {'id': 1, 'name': 'Personal Loan', 'rate': 7.5, 'term': '36-60 months', 'icon': 'fa-file-contract'},
            {'id': 2, 'name': 'Home Loan', 'rate': 5.2, 'term': '360 months', 'icon': 'fa-home'},
            {'id': 3, 'name': 'Auto Loan', 'rate': 6.5, 'term': '60-84 months', 'icon': 'fa-car'},
            {'id': 4, 'name': 'Education Loan', 'rate': 4.5, 'term': '240-300 months', 'icon': 'fa-graduation-cap'},
        ],
        'cards': [
            {'id': 1, 'name': 'Premium Credit Card', 'cashback': 2.0, 'annual_fee': 500, 'icon': 'fa-credit-card'},
            {'id': 2, 'name': 'Travel Credit Card', 'cashback': 1.5, 'annual_fee': 0, 'icon': 'fa-plane'},
            {'id': 3, 'name': 'Business Card', 'cashback': 3.0, 'annual_fee': 1000, 'icon': 'fa-briefcase'},
        ],
        'deposits': [
            {'id': 1, 'name': 'Savings Account', 'rate': 4.0, 'icon': 'fa-piggy-bank'},
            {'id': 2, 'name': 'Fixed Deposit', 'rate': 6.5, 'icon': 'fa-lock'},
            {'id': 3, 'name': 'Money Market Account', 'rate': 5.2, 'icon': 'fa-chart-line'},
        ]
    }
    
    return render_template('products/dashboard.html', products=products)

@products_bp.route('/loan/<int:loan_id>')
@login_required
def view_loan(loan_id):
    """View loan product details"""
    loans = {
        1: {'name': 'Personal Loan', 'rate': 7.5, 'min': 50000, 'max': 1000000, 'term': '36-60 months'},
        2: {'name': 'Home Loan', 'rate': 5.2, 'min': 500000, 'max': 50000000, 'term': '360 months'},
        3: {'name': 'Auto Loan', 'rate': 6.5, 'min': 200000, 'max': 5000000, 'term': '60-84 months'},
        4: {'name': 'Education Loan', 'rate': 4.5, 'min': 100000, 'max': 2000000, 'term': '240-300 months'},
    }
    
    loan = loans.get(loan_id, {})
    return render_template('products/loan.html', loan=loan, loan_id=loan_id)

@products_bp.route('/card/<int:card_id>')
@login_required
def view_card(card_id):
    """View credit card product details"""
    cards = {
        1: {'name': 'Premium Credit Card', 'cashback': 2.0, 'annual_fee': 500, 'limit': 500000},
        2: {'name': 'Travel Credit Card', 'cashback': 1.5, 'annual_fee': 0, 'limit': 300000},
        3: {'name': 'Business Card', 'cashback': 3.0, 'annual_fee': 1000, 'limit': 1000000},
    }
    
    card = cards.get(card_id, {})
    return render_template('products/card.html', card=card, card_id=card_id)

@products_bp.route('/deposit/<int:deposit_id>')
@login_required
def view_deposit(deposit_id):
    """View deposit product details"""
    deposits = {
        1: {'name': 'Savings Account', 'rate': 4.0, 'min': 0},
        2: {'name': 'Fixed Deposit', 'rate': 6.5, 'min': 10000},
        3: {'name': 'Money Market Account', 'rate': 5.2, 'min': 50000},
    }
    
    deposit = deposits.get(deposit_id, {})
    return render_template('products/deposit.html', deposit=deposit, deposit_id=deposit_id)

@products_bp.route('/apply/<product_type>/<int:product_id>', methods=['GET', 'POST'])
@login_required
def apply_product(product_type, product_id):
    """Apply for a banking product"""
    if request.method == 'POST':
        # Process application
        flash('Your application has been submitted! Our team will review it within 2-3 business days.', 'success')
        return redirect(url_for('products.dashboard'))
    
    return render_template('products/apply.html', product_type=product_type, product_id=product_id)

@products_bp.route('/api/eligibility', methods=['POST'])
@login_required
def check_eligibility():
    """AI-powered eligibility check for products"""
    data = request.json
    product_type = data.get('product_type')
    
    # Get user accounts and balance
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(acc.balance for acc in accounts)
    
    # Simple eligibility logic (would be AI-powered in production)
    eligibility = {
        'personal_loan': total_balance >= 50000,
        'credit_card': total_balance >= 25000,
        'fixed_deposit': total_balance >= 10000,
    }
    
    is_eligible = eligibility.get(product_type, False)
    
    return jsonify({
        'eligible': is_eligible,
        'reason': 'You meet the eligibility criteria' if is_eligible else 'Insufficient balance or credit history',
        'current_balance': total_balance
    })
