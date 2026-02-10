#!/usr/bin/env python
import sys
sys.path.insert(0, 'BankFlask')

from app import create_app
from app.models import User

app = create_app()

with app.app_context():
    # Try to get existing admin
    admin = User.query.filter_by(username='johndoe').first()
    
    if admin:
        print(f"Found existing admin: {admin.username} (ID: {admin.id})")
        admin.set_password('admin@2005')
        from app import db
        db.session.commit()
        print("✓ Password reset to: admin@2005")
    else:
        print("Admin user not found. Creating new admin...")
        new_admin = User(
            username='johndoe',
            email='john@example.com',
            first_name='John',
            last_name='Doe',
            is_admin=True
        )
        new_admin.set_password('admin@2005')
        from app import db
        db.session.add(new_admin)
        db.session.commit()
        print(f"✓ New admin created: johndoe (ID: {new_admin.id})")
        print("✓ Password: admin@2005")
