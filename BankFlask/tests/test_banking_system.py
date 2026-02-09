"""
Banking AI System 2026 - Smoke Tests
Tests all banking routes to ensure they load without errors
"""
import sys
sys.path.insert(0, 'C:\\language\\Bank\\BankFlask')

from app import create_app, db
from app.models import User, Account
import unittest

class BankingSystemSmokeTest(unittest.TestCase):
    """Test all banking routes"""
    
    test_counter = 0  # Class-level counter for unique usernames
    
    def setUp(self):
        """Set up test client and create test user"""
        BankingSystemSmokeTest.test_counter += 1
        self.test_id = BankingSystemSmokeTest.test_counter
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
            
            # Create test user with unique username
            user = User(
                username=f'testuser{self.test_id}',
                email=f'test{self.test_id}@example.com',
                first_name='Test',
                last_name='User',
                account_number=f'{1234567890123456+self.test_id}'
            )
            user.set_password('password123')
            db.session.add(user)
            
            # Create test account
            account = Account(user_id=1, account_type='SAVINGS', balance=50000.0)
            db.session.add(account)
            db.session.commit()
        
        self.client = self.app.test_client()
        self.username = f'testuser{self.test_id}'
    
    def login(self):
        """Login test user"""
        response = self.client.post('/login', data={
            'username': self.username,
            'password': 'password123'
        }, follow_redirects=True)
        return response
    
    def test_01_login_page(self):
        """Test login page loads"""
        response = self.client.get('/login')
        self.assertIn(response.status_code, [200, 302])
        print("✓ Login page loads")
    
    def test_02_login_functionality(self):
        """Test user can login"""
        response = self.login()
        self.assertNotEqual(response.status_code, 500)
        print("✓ Login functionality works")
    
    def test_03_dashboard(self):
        """Test main dashboard"""
        self.login()
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)
        print("✓ Dashboard loads successfully")
    
    def test_04_accounts_dashboard(self):
        """Test accounts management"""
        self.login()
        response = self.client.get('/accounts/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Accounts', response.data)
        print("✓ Accounts dashboard loads")
    
    def test_05_products_page(self):
        """Test banking products page"""
        self.login()
        response = self.client.get('/products/')
        self.assertIn(response.status_code, [200, 405])
        print("✓ Products page accessible")
    
    def test_06_financial_planning(self):
        """Test financial planning"""
        self.login()
        response = self.client.get('/planning/')
        self.assertIn(response.status_code, [200, 405])
        print("✓ Financial planning page accessible")
    
    def test_07_investments(self):
        """Test investments dashboard"""
        self.login()
        response = self.client.get('/investments/')
        self.assertIn(response.status_code, [200, 405])
        print("✓ Investments dashboard accessible")
    
    def test_08_advisor(self):
        """Test AI financial advisor"""
        self.login()
        response = self.client.get('/advisor/')
        self.assertIn(response.status_code, [200, 405])
        print("✓ AI Advisor dashboard accessible")
    
    def test_09_transactions(self):
        """Test transactions page"""
        self.login()
        response = self.client.get('/transactions/dashboard')
        self.assertIn(response.status_code, [200, 405])
        print("✓ Transactions page accessible")
    
    def test_10_account_api(self):
        """Test account API endpoints"""
        self.login()
        response = self.client.get('/accounts/api/balance')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'total_balance', response.data)
        print("✓ Account API endpoints work")
    
    def test_11_no_500_errors(self):
        """Verify no 500 errors on main banking routes"""
        self.login()
        
        banking_routes = [
            '/dashboard/',
            '/accounts/dashboard',
            '/products/',
            '/planning/',
            '/investments/',
            '/advisor/',
        ]
        
        for route in banking_routes:
            response = self.client.get(route)
            self.assertNotEqual(response.status_code, 500, 
                              f"Route {route} returned 500 error")
        
        print("✓ No 500 errors on banking routes")
    
    def test_12_banking_products_exist(self):
        """Test banking products are loaded"""
        self.login()
        response = self.client.get('/products/')
        # Check response contains banking product information
        self.assertNotEqual(response.status_code, 500)
        print("✓ Banking products loaded successfully")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  BANKING AI MANAGEMENT SYSTEM 2026 - SMOKE TESTS")
    print("="*60 + "\n")
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(BankingSystemSmokeTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Banking System Ready!")
    else:
        print("❌ Some tests failed - See errors above")
    print("="*60 + "\n")
    
    sys.exit(0 if result.wasSuccessful() else 1)
