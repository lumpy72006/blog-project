# type: igrore
import tempfile
from PIL import Image
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Profile

def get_temporary_image(name='test_image.png'):
    """
    Helper to generate a temporary image for upload tests
    """
    file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    image = Image.new('RGB', (100, 100), 'red')
    image.save(file, format='PNG')
    file.seek(0)
    return file

class UserRegistrationTestCase(APITestCase):
    """
    Test user registration and automatic profile creation
    """
    def test_registration_success(self):
        """
        Test that registering creates a User AND a Profile (via signal)
        """
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        response = self.client.post('/api/register/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify User created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        
        # Verify Profile created (via signals.py)
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_registration_password_mismatch(self):
        data = {
            'username': 'mismatch',
            'email': 'mismatch@example.com',
            'password': 'password123',
            'password_confirm': 'password321'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_email_duplicate(self):
        # Create existing user
        User.objects.create_user('existing', 'exist@example.com', 'pass')
        
        data = {
            'username': 'newuser2',
            'email': 'exist@example.com', # Duplicate email
            'password': 'password123',
            'password_confirm': 'password123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserProfileTestCase(APITestCase):
    """
    Test /api/users/me/ (Private) and /api/users/<username>/ (Public)
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='old@example.com', 
            password='password123'
        )
        # Profile is created automatically by signal, so we just get it
        self.profile = self.user.profile
        self.profile.bio = "Old Bio"
        self.profile.save()

    def test_get_my_profile_authenticated(self):
        """
        Test GET /api/users/me/ retrieves full details
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'old@example.com')
        self.assertEqual(response.data['profile']['bio'], 'Old Bio')

    def test_get_my_profile_unauthenticated(self):
        """
        Test GET /api/users/me/ requires login
        """
        response = self.client.get('/api/users/me/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_profile_mixed_fields(self):
        """
        Test PATCH /api/users/me/ updates BOTH User (email) and Profile (bio) models
        Verifies the custom update() method in UserDetailSerializer
        """
        self.client.force_authenticate(user=self.user)
        
        data = {
            'email': 'new@example.com',
            'profile': {
                'bio': 'New Updated Bio'
            }
        }
        
        response = self.client.patch('/api/users/me/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        
        # Check User model update
        self.assertEqual(self.user.email, 'new@example.com')
        # Check Profile model update
        self.assertEqual(self.user.profile.bio, 'New Updated Bio')


    def test_get_public_profile(self):
        """
        Test GET /api/users/<username>/
        """
        response = self.client.get(f'/api/users/{self.user.username}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        # Ensure private data like Email is NOT exposed (if your serializer logic hides it)
        # Based on your logic, you might or might not have hidden it. 
        # If you implemented the conditional email field:
        # self.assertIsNone(response.data.get('email')) 

    def test_get_public_profile_not_found(self):
        response = self.client.get('/api/users/nonexistent/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UserListTestCase(APITestCase):
    def test_list_users(self):
        User.objects.create_user('u1', 'e1@e.com', 'pass')
        User.objects.create_user('u2', 'e2@e.com', 'pass')
        
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
