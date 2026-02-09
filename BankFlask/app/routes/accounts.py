from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction
from datetime import datetime, timedelta
import random
import string

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

def generate_account_number():
    """Generate unique 16-digit account number"""
    while True:
        account_num = ''.join(random.choices(string.digits, k=16))
        if not Account.query.filter_by(account_number=account_num).first():
            return account_num

@accounts_bp.route('/dashboard')
@login_required
def dashboard():
    """Account management dashboard with real data"""
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals
    total_balance = sum(acc.balance for acc in user_accounts) if user_accounts else 0
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(
        Transaction.created_at.desc()
    ).limit(10).all()
    
    # Calculate monthly metrics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    monthly_spending = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type.in_(['WITHDRAWAL', 'TRANSFER', 'PAYMENT']),
        Transaction.created_at >= thirty_days_ago,
        Transaction.status == 'COMPLETED'
    ).scalar() or 0
    
    monthly_income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type.in_(['DEPOSIT']),
        Transaction.created_at >= thirty_days_ago,
        Transaction.status == 'COMPLETED'
    ).scalar() or 0
    
    active_accounts = sum(1 for acc in user_accounts if acc.status == 'ACTIVE')
    
    # Determine health
    if total_balance >= 50000:
        health, color = 'Excellent', 'success'
    elif total_balance >= 20000:
        health, color = 'Very Good', 'success'
    elif total_balance >= 10000:
        health, color = 'Good', 'info'
    elif total_balance >= 5000:
        health, color = 'Fair', 'warning'
    else:
        health, color = 'Poor', 'danger'
    
    stats = {
        'total_accounts': len(user_accounts),
        'active_accounts': active_accounts,
        'total_balance': total_balance,
        'monthly_spending': abs(monthly_spending),
        'monthly_income': monthly_income,
        'account_health': health,
        'health_color': color,
        'savings_rate': round((monthly_income - abs(monthly_spending)) / monthly_income * 100, 1) if monthly_income > 0 else 0
    }
    
    return render_template('accounts/dashboard.html', 
                         accounts=user_accounts,
                         stats=stats,
                         recent_transactions=recent_transactions)

@accounts_bp.route('/<int:account_id>')
@login_required
def view_account(account_id):
    """View detailed account information"""
    account = Account.query.get_or_404(account_id)
    
    if account.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('accounts.dashboard'))
    
    # Get transactions for this account
    transactions = Transaction.query.filter_by(user_id=current_user.id).filter(
        db.or_(
            Transaction.from_account == account.account_number,
            Transaction.to_account == account.account_number
        )
    ).order_by(Transaction.created_at.desc()).all()
    
    # Calculate stats
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_spending = db.session.query(db.func.sum(Transaction.amount)).filter(
        db.or_(
            Transaction.from_account == account.account_number,
            Transaction.to_account == account.account_number
        ),
        Transaction.transaction_type.in_(['WITHDRAWAL', 'TRANSFER', 'PAYMENT']),
        Transaction.created_at >= thirty_days_ago,
        Transaction.status == 'COMPLETED'
    ).scalar() or 0
    
    return render_template('accounts/view.html',
                         account=account,
                         transactions=transactions,
                         monthly_spending=abs(monthly_spending),
                         transaction_count=len(transactions))

@accounts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_account():
    """Create a new account"""
    if request.method == 'POST':
        account_name = request.form.get('account_name', '').strip()
        account_type = request.form.get('account_type', 'SAVINGS')
        initial_deposit = request.form.get('initial_deposit', 0, type=float)
        
        # Validation
        if not account_name or len(account_name) < 2:
            flash('Account name must be at least 2 characters', 'danger')
            return render_template('accounts/create.html')
        
        if account_type not in ['SAVINGS', 'CHECKING', 'INVESTMENT']:
            flash('Invalid account type', 'danger')
            return render_template('accounts/create.html')
        
        if initial_deposit < 0:
            flash('Initial deposit cannot be negative', 'danger')
            return render_template('accounts/create.html')
        
        try:
            new_account = Account(
                user_id=current_user.id,
                account_name=account_name,
                account_type=account_type,
                balance=max(initial_deposit, 0),
                account_number=generate_account_number(),
                currency='USD',
                status='ACTIVE'
            )
            db.session.add(new_account)
            db.session.flush()
            
            # Record initial deposit
            if initial_deposit > 0:
                transaction = Transaction(
                    user_id=current_user.id,
                    amount=initial_deposit,
                    transaction_type='DEPOSIT',
                    status='COMPLETED',
                    description=f'Initial deposit to {account_name}',
                    to_account=new_account.account_number
                )
                db.session.add(transaction)
            
            db.session.commit()
            flash(f'✓ Account "{account_name}" created with ${initial_deposit:,.2f}', 'success')
            return redirect(url_for('accounts.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return render_template('accounts/create.html')
    
    return render_template('accounts/create.html')

@accounts_bp.route('/<int:account_id>/transfer', methods=['GET', 'POST'])
@login_required
def transfer(account_id):
    """Transfer funds between accounts"""
    from_account = Account.query.get_or_404(account_id)
    
    if from_account.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('accounts.dashboard'))
    
    to_accounts = Account.query.filter(
        Account.user_id == current_user.id,
        Account.id != account_id,
        Account.status == 'ACTIVE'
    ).all()
    
    if request.method == 'POST':
        to_account_id = request.form.get('to_account_id', type=int)
        amount = request.form.get('amount', 0, type=float)
        description = request.form.get('description', '').strip()
        
        if not to_account_id or amount <= 0 or amount > from_account.balance:
            flash('Invalid transfer details', 'danger')
            return render_template('accounts/transfer.html', from_account=from_account, to_accounts=to_accounts)
        
        to_account = Account.query.get_or_404(to_account_id)
        if to_account.user_id != current_user.id:
            flash('Unauthorized', 'danger')
            return redirect(url_for('accounts.dashboard'))
        
        try:
            from_account.balance -= amount
            to_account.balance += amount
            from_account.updated_at = datetime.utcnow()
            to_account.updated_at = datetime.utcnow()
            
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                transaction_type='TRANSFER',
                status='COMPLETED',
                description=description or f'Transfer to {to_account.account_name}',
                from_account=from_account.account_number,
                to_account=to_account.account_number
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash(f'✓ Transferred ${amount:,.2f}', 'success')
            return redirect(url_for('accounts.view_account', account_id=from_account.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('accounts/transfer.html', from_account=from_account, to_accounts=to_accounts)

@accounts_bp.route('/<int:account_id>/deposit', methods=['GET', 'POST'])
@login_required
def deposit(account_id):
    """Deposit funds"""
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('accounts.dashboard'))
    
    if request.method == 'POST':
        amount = request.form.get('amount', 0, type=float)
        description = request.form.get('description', '').strip()
        
        if amount <= 0:
            flash('Amount must be greater than 0', 'danger')
            return render_template('accounts/deposit.html', account=account)
        
        try:
            account.balance += amount
            account.updated_at = datetime.utcnow()
            
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                transaction_type='DEPOSIT',
                status='COMPLETED',
                description=description or 'Deposit',
                to_account=account.account_number
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash(f'✓ Deposited ${amount:,.2f}', 'success')
            return redirect(url_for('accounts.view_account', account_id=account.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('accounts/deposit.html', account=account)

@accounts_bp.route('/<int:account_id>/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw(account_id):
    """Withdraw funds"""
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('accounts.dashboard'))
    
    if request.method == 'POST':
        amount = request.form.get('amount', 0, type=float)
        description = request.form.get('description', '').strip()
        
        if amount <= 0 or amount > account.balance:
            flash('Invalid amount', 'danger')
            return render_template('accounts/withdraw.html', account=account)
        
        try:
            account.balance -= amount
            account.updated_at = datetime.utcnow()
            
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                transaction_type='WITHDRAWAL',
                status='COMPLETED',
                description=description or 'Withdrawal',
                from_account=account.account_number
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash(f'✓ Withdrew ${amount:,.2f}', 'success')
            return redirect(url_for('accounts.view_account', account_id=account.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('accounts/withdraw.html', account=account)

@accounts_bp.route('/api/balance/<int:account_id>')
@login_required
def api_balance(account_id):
    """Get account balance"""
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        return jsonify({'success': False}), 403
    return jsonify({'balance': round(account.balance, 2)})
