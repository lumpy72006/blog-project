# type: iganore
# type: ignore
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from blog.models import Post


class PostViewSetTestCase(APITestCase):
    """
    Test PostViewSet endpoints - /api/posts/
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', 
            password='testpass123'
        )
        
        # Create test posts
        self.published_post = Post.objects.create(
            title='Published Post',
            slug='published-post',
            content='This is a published post content with enough words.',
            author=self.user,
            status='published',
            pub_date=timezone.now()
        )
        
        self.draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post', 
            content='This is a draft post content.',
            author=self.user,
            status='draft'
        )
        
        self.future_post = Post.objects.create(
            title='Future Post',
            slug='future-post',
            content='This is a future post content.',
            author=self.user,
            status='published',
            pub_date=timezone.now() + timedelta(days=1)
        )

    def test_list_posts_unauthenticated(self):
        """
        Test GET /api/posts/ - unauthenticated users see only published posts
        """
        response = self.client.get('/api/posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see the published post (not draft, not future)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Published Post')

    def test_list_posts_authenticated(self):
        """
        Test GET /api/posts/ - authenticated users see published + their drafts
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/posts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see published post + own draft (2 total)
        self.assertEqual(len(response.data['results']), 2)
        titles = [post['title'] for post in response.data['results']]
        self.assertIn('Published Post', titles)
        self.assertIn('Draft Post', titles)

    def test_retrieve_published_post_unauthenticated(self):
        """
        Test GET /api/posts/{slug}/ - anyone can see published posts
        """
        response = self.client.get(f'/api/posts/{self.published_post.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Published Post')

    def test_retrieve_draft_post_as_author(self):
        """
        Test authors can retrieve their own draft posts
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/posts/{self.draft_post.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Draft Post')

    def test_retrieve_draft_post_as_other_user(self):
        """
        Test other users cannot retrieve draft posts
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/posts/{self.draft_post.slug}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_future_post_returns_404(self):
        """
        Test future posts return 404 even if published
        """
        response = self.client.get(f'/api/posts/{self.future_post.slug}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_post_authenticated(self):
        """
        Test POST /api/posts/ - authenticated users can create posts
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New API Created Post',
            'content': 'This is a new test post content created via API.',
            'status': 'published'
        }

        intial_count = Post.objects.count()
        response = self.client.post('/api/posts/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), intial_count + 1)  # 3 existing + 1 new

        new_post = Post.objects.get(title=data['title'])
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.status, 'published')

    def test_create_post_unauthenticated(self):
        """
        Test POST /api/posts/ - unauthenticated users get 401
        """
        data = {
            'title': 'Should Fail Post',
            'content': 'This should fail without authentication.',
            'status': 'published'
        }
        response = self.client.post('/api/posts/', data, format='json')
        
        # is authenticated or read only permissons make it return 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_own_post(self):
        """
        Test authors can update their own posts
        """
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Title'}
        response = self.client.patch(
            f'/api/posts/{self.published_post.slug}/', 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.title, 'Updated Title')

    def test_update_other_users_post(self):
        """
        Test users cannot update other users' posts
        """
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Hacked Title'}
        response = self.client.patch(
            f'/api/posts/{self.published_post.slug}/', 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_functionality(self):
        """Test comment creation and listing"""
        
        self.client.force_authenticate(user=self.user)
        
        # Create comment
        data = {'content': 'Test comment via API'}
        response = self.client.post(
            f'/api/posts/{self.published_post.slug}/comments/', 
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # List comments
        response = self.client.get(f'/api/posts/{self.published_post.slug}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_user_posts_endpoint(self):
        """Test user-specific posts endpoint"""
        response = self.client.get(f'/api/users/{self.user.username}/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only published post

    def test_search_functionality(self):
        """Test post search"""
        response = self.client.get('/api/posts/?search=Published')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

#    def test_debug_authentication(self):
#        """
#        Debug test to see authentication behavior
#        """
#        from rest_framework.settings import api_settings
#        print("Authentication classes:", api_settings.DEFAULT_AUTHENTICATION_CLASSES)
#        print("Permission classes:", api_settings.DEFAULT_PERMISSION_CLASSES)
#        
#        # Test both endpoints
#        response_get = self.client.get('/api/posts/')
#        response_post = self.client.post('/api/posts/', {})
#        
#        print(f"GET status: {response_get.status_code}")
#        print(f"POST status: {response_post.status_code}")
#        print(f"POST data: {response_post.data}")
#

    def test_post_list_query_performance(self):
        """Test post list has optimized query count"""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        # Create test data
        for i in range(5):
            Post.objects.create(
                title=f'Test Post {i}', slug=f'test-{i}',
                content='Content', author=self.user, status='published'
            )
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/posts/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Count only application queries (exclude Silk, EXPLAIN, etc.)
            app_queries = [
                q for q in context.captured_queries 
                if not any(x in q['sql'] for x in ['silk_', 'EXPLAIN', 'SAVEPOINT', 'RELEASE'])
            ]
            
            # With 6 posts, should be 3-4 queries (not 6*N)
            self.assertLessEqual(len(app_queries), 4)
            print(f"✅ Optimized: {len(app_queries)} queries for {len(response.data['results'])} posts")

class LikePostTestCase(APITestCase):
    """
    Test post like/unlike functionality
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post for Likes',
            slug='test-likes-post',
            content='Content for likes test.',
            author=self.user,
            status='published'
        )
    
    def test_like_post_authenticated(self):
        """
        Test POST /api/posts/{slug}/like/ - authenticated users can like posts
        """
        self.client.force_authenticate(user=self.user)
        
        # Like the post
        response = self.client.post(f'/api/posts/{self.post.slug}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['liked'], True)
        self.assertEqual(response.data['likes_count'], 1)
        
        # Verify in database
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, 1)
        self.assertTrue(self.post.liked_by.filter(id=self.user.id).exists())
    
    def test_unlike_post(self):
        """
        Test liking then unliking a post
        """
        self.client.force_authenticate(user=self.user)  # Use force_authenticate
        
        # Like then unlike
        self.client.post(f'/api/posts/{self.post.slug}/like/')
        response = self.client.post(f'/api/posts/{self.post.slug}/like/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
    
    def test_like_post_unauthenticated(self):
        """
        Test unauthenticated users cannot like posts
        """
        initial_likes =self.post.likes
        response = self.client.post(f'/api/posts/{self.post.slug}/like/')

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, initial_likes)
        
        # With SessionAuthentication, unauthenticated users get 403
        # Both 401 and 403 mean "access denied" - test for either
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED, 
            status.HTTP_403_FORBIDDEN
        ])
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
