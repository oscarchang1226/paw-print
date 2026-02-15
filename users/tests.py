from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

class UserModelTest(TestCase):
    def test_user_model_is_custom(self):
        """Test that the custom user model is used."""
        User = get_user_model()
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')
        self.assertEqual(User.__name__, 'User')
        self.assertEqual(User._meta.app_label, 'users')

    def test_create_user(self):
        """Test creating a normal user."""
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
