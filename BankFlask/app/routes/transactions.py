from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Transaction, Account, User
from app import db
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('transactions/history.html', transactions=transactions)

@transactions_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        recipient = request.form.get('recipient', '').strip()
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', '').strip()
        
        # Validation
        if not recipient or not amount:
            flash('Recipient and amount are required', 'danger')
            return render_template('transactions/transfer.html')
        
        if amount <= 0:
            flash('Amount must be greater than 0', 'danger')
            return render_template('transactions/transfer.html')
        
        # Find recipient
        recipient_user = User.query.filter_by(account_number=recipient).first()
        if not recipient_user:
            flash('Recipient account not found', 'danger')
            return render_template('transactions/transfer.html')
        
        if recipient_user.id == current_user.id:
            flash('Cannot transfer to your own account', 'danger')
            return render_template('transactions/transfer.html')
        
        # Check balance
        account = Account.query.filter_by(user_id=current_user.id).first()
        if account.balance < amount:
            flash('Insufficient balance', 'danger')
            return render_template('transactions/transfer.html')
        
        # Create transaction
        try:
            # Debit from sender
            account.balance -= amount
            
            # Credit to recipient
            recipient_account = Account.query.filter_by(user_id=recipient_user.id).first()
            recipient_account.balance += amount
            
            # Create transaction records
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                transaction_type='TRANSFER',
                status='COMPLETED',
                description=description or f'Transfer to {recipient_user.full_name}',
                from_account=current_user.account_number,
                to_account=recipient
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash('Transfer completed successfully', 'success')
            return redirect(url_for('transactions.history'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during the transfer', 'danger')
            return render_template('transactions/transfer.html')
    
    return render_template('transactions/transfer.html')

@transactions_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = request.form.get('amount', type=float)
        description = request.form.get('description', '').strip()
        
        if not amount or amount <= 0:
            flash('Please enter a valid amount', 'danger')
            return render_template('transactions/deposit.html')
        
        try:
            account = Account.query.filter_by(user_id=current_user.id).first()
            account.balance += amount
            
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                transaction_type='DEPOSIT',
                status='COMPLETED',
                description=description or 'Account deposit',
                to_account=current_user.account_number
            )
            db.session.add(transaction)
            db.session.commit()
            
            flash('Deposit successful', 'success')
            return redirect(url_for('transactions.history'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred', 'danger')
    
    return render_template('transactions/deposit.html')

@transactions_bp.route('/api/recent')
@login_required
def api_recent():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'type': t.transaction_type,
        'description': t.description,
        'created_at': t.created_at.isoformat()
    } for t in transactions])
