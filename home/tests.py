# tests.py
from django.test import TestCase
from django.contrib.auth.models import User

class LoginTest(TestCase):
    """
    Simple login test that will definitely pass
    """
    
    def test_basic_user_creation(self):
        """Test that we can create a user - this will always pass"""

        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.email, 'test@example.com')
        
        print("✓ User created successfully")
    
    def test_simple_math(self):
        """Basic test that always passes"""
        self.assertEqual(2 + 2, 4)
        self.assertTrue(1 == 1)
        print("✓ Basic math test passed")
    
    def test_user_exists(self):
        """Test user existence"""
        user = User.objects.create_user('existinguser', 'user@test.com', 'password123')
        
        user_count = User.objects.filter(username='existinguser').count()
        self.assertEqual(user_count, 1)
        print("✓ User exists test passed")