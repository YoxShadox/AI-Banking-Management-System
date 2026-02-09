from app import create_app, db
from app.models import User
from app.routes.auth import generate_account_number

app = create_app()
with app.app_context():
    db.create_all()
    # Check if user with id=1 exists
    existing = User.query.get(1)
    if existing:
        print(f"Admin already exists: id={existing.id}, username={existing.username}, email={existing.email}")
    else:
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            account_number=generate_account_number()
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print('Created admin id=', admin.id)
        print('Username: admin')
        print('Password: Admin@123')
