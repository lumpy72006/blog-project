from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIRequestFactory

from blog.models import Post
from api.permissions import IsAuthorOrReadOnly

class PermissionTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user('user1', 'pass')
        self.other_user = User.objects.create_user('user2', 'pass')
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            author=self.user
        )
        self.permission = IsAuthorOrReadOnly()

    def test_author_can_edit(self):
        """Test author has write permissions"""
        request = self.factory.patch('/')
        request.user = self.user
        self.assertTrue(self.permission.has_object_permission(request, None, self.post))

    def test_other_user_cannot_edit(self):
        """Test other users have read-only permissions"""
        request = self.factory.patch('/')
        request.user = self.other_user
        self.assertFalse(self.permission.has_object_permission(request, None, self.post))

    def test_safe_methods_allowed(self):
        """Test safe methods are allowed for all users"""
        request = self.factory.get('/')
        request.user = self.other_user
        self.assertTrue(self.permission.has_object_permission(request, None, self.post))
