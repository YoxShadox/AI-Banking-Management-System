from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Account
from datetime import datetime

investments_bp = Blueprint('investments', __name__, url_prefix='/investments')

@investments_bp.route('/')
@login_required
def dashboard():
    """Investment portfolio dashboard"""
    portfolio = {
        'total_value': 500000,
        'invested': 350000,
        'gain': 50000,
        'gain_percent': 14.3,
        'positions': [
            {'symbol': 'NIFTY50', 'name': 'Nifty 50 Index Fund', 'quantity': 100, 'buy_price': 2500, 'current_price': 2750, 'gain': 25000},
            {'symbol': 'BANKEX', 'name': 'Banking Index Fund', 'quantity': 50, 'buy_price': 3000, 'current_price': 3150, 'gain': 7500},
            {'symbol': 'TCS', 'name': 'TCS Stock', 'quantity': 20, 'buy_price': 3500, 'current_price': 3800, 'gain': 6000},
        ]
    }
    
    return render_template('investments/dashboard.html', portfolio=portfolio)

@investments_bp.route('/positions')
@login_required
def positions():
    """View all investment positions"""
    positions = [
        {'id': 1, 'symbol': 'NIFTY50', 'name': 'Nifty 50 Index Fund', 'quantity': 100, 'buy_price': 2500, 'current_price': 2750, 'gain': 25000, 'gain_percent': 10},
        {'id': 2, 'symbol': 'BANKEX', 'name': 'Banking Index Fund', 'quantity': 50, 'buy_price': 3000, 'current_price': 3150, 'gain': 7500, 'gain_percent': 5},
        {'id': 3, 'symbol': 'TCS', 'name': 'TCS Stock', 'quantity': 20, 'buy_price': 3500, 'current_price': 3800, 'gain': 6000, 'gain_percent': 8.6},
        {'id': 4, 'symbol': 'INFY', 'name': 'Infosys Stock', 'quantity': 30, 'buy_price': 1500, 'current_price': 1450, 'gain': -1500, 'gain_percent': -3.3},
    ]
    
    return render_template('investments/positions.html', positions=positions)

@investments_bp.route('/position/<int:position_id>')
@login_required
def view_position(position_id):
    """View detailed position information"""
    position = {
        'id': position_id,
        'symbol': 'NIFTY50',
        'name': 'Nifty 50 Index Fund',
        'sector': 'Diversified',
        'quantity': 100,
        'buy_price': 2500,
        'current_price': 2750,
        'total_value': 275000,
        'gain': 25000,
        'gain_percent': 10,
        'pe_ratio': 22.5,
        'dividend_yield': 1.8,
        'description': 'Track the top 50 companies on NSE. Highly liquid and diversified.',
    }
    
    return render_template('investments/position_detail.html', position=position)

@investments_bp.route('/mutual-funds')
@login_required
def mutual_funds():
    """Browse mutual fund options"""
    funds = [
        {'id': 1, 'name': 'HDFC Index Fund 50', 'category': 'Equity', 'nav': 500, 'aum': '5000 Cr', 'returns_1y': 12.5, 'returns_3y': 14.2},
        {'id': 2, 'name': 'ICICI Liquid Fund', 'category': 'Liquid', 'nav': 100, 'aum': '10000 Cr', 'returns_1y': 4.5, 'returns_3y': 4.8},
        {'id': 3, 'name': 'Axis Balanced Fund', 'category': 'Balanced', 'nav': 250, 'aum': '3000 Cr', 'returns_1y': 10.2, 'returns_3y': 11.5},
    ]
    
    return render_template('investments/mutual_funds.html', funds=funds)

@investments_bp.route('/stocks')
@login_required
def stocks():
    """Browse stock options"""
    stocks = [
        {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'price': 3800, 'pe': 25.5, 'return_1y': 15, 'market_cap': '14L Cr'},
        {'symbol': 'INFY', 'name': 'Infosys Limited', 'price': 1450, 'pe': 22.3, 'return_1y': 5, 'market_cap': '6L Cr'},
        {'symbol': 'WIPRO', 'name': 'Wipro Limited', 'price': 420, 'pe': 18.2, 'return_1y': 8, 'market_cap': '2L Cr'},
    ]
    
    return render_template('investments/stocks.html', stocks=stocks)

@investments_bp.route('/buy/<product_type>/<product_id>', methods=['GET', 'POST'])
@login_required
def buy(product_type, product_id):
    """Buy investment product"""
    if request.method == 'POST':
        quantity = request.form.get('quantity', 1)
        flash(f'Purchase of {quantity} units initiated! Order will be processed shortly.', 'success')
        return redirect(url_for('investments.dashboard'))
    
    return render_template('investments/buy.html', product_type=product_type, product_id=product_id)

@investments_bp.route('/sell/<int:position_id>', methods=['GET', 'POST'])
@login_required
def sell(position_id):
    """Sell investment position"""
    if request.method == 'POST':
        quantity = request.form.get('quantity', 1)
        flash(f'Sale of {quantity} units initiated! Order will be processed shortly.', 'success')
        return redirect(url_for('investments.positions'))
    
    return render_template('investments/sell.html', position_id=position_id)

@investments_bp.route('/portfolio-analysis')
@login_required
def portfolio_analysis():
    """AI-powered portfolio analysis and rebalancing"""
    analysis = {
        'current_allocation': {
            'stocks': 60,
            'mutual_funds': 30,
            'bonds': 10
        },
        'recommended_allocation': {
            'stocks': 50,
            'mutual_funds': 35,
            'bonds': 15
        },
        'diversification_score': 7.5,
        'risk_score': 6.0,
        'recommendations': [
            'Your equity allocation is higher than recommended. Consider reducing by 10%.',
            'Diversify into international funds for global exposure.',
            'Add fixed income securities to reduce overall risk.',
        ]
    }
    
    return render_template('investments/portfolio_analysis.html', analysis=analysis)

@investments_bp.route('/api/portfolio-value')
@login_required
def api_portfolio_value():
    """Get portfolio value trend"""
    data = [
        {'date': '2025-01', 'value': 300000},
        {'date': '2025-04', 'value': 320000},
        {'date': '2025-07', 'value': 350000},
        {'date': '2025-10', 'value': 380000},
        {'date': '2026-01', 'value': 500000},
    ]
    return jsonify(data)

@investments_bp.route('/api/recommended-trades')
@login_required
def api_recommended_trades():
    """Get AI-recommended trading opportunities"""
    recommendations = [
        {'action': 'BUY', 'stock': 'WIPRO', 'reason': 'Strong fundamentals, undervalued', 'confidence': 85},
        {'action': 'SELL', 'stock': 'INFY', 'reason': 'Negative outlook, reduce losses', 'confidence': 72},
        {'action': 'HOLD', 'stock': 'TCS', 'reason': 'Stable performer', 'confidence': 90},
    ]
    return jsonify(recommendations)
