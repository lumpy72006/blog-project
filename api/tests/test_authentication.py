# type: ignore
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class AuthenticationTestCase(APITestCase):
    """
    Test JWT Authentication endpoints
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_obtain_token_valid_credentials(self):
        """
        Test POST /api/token/ with valid credentials
        """
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_obtain_token_invalid_credentials(self):
        """
        Test POST /api/token/ with invalid credentials
        """
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test JWT token refresh"""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        refresh_token = response.data['refresh']

        response = self.client.post('/api/token/refresh/', {
            'refresh': refresh_token
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token"""
        response = self.client.post('/api/token/refresh/', {
            'refresh': 'invalid-token'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
