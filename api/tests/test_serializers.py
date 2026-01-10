from django.test import TestCase
from api.serializers import PostCreateUpdateSerializer, CommentCreateSerializer

class SerializerTestCase(TestCase):
    def test_post_serializer_validation(self):
        """Test PostCreateUpdateSerializer validation"""
        # Valid data
        serializer = PostCreateUpdateSerializer(data={
            'title': 'Valid Title',
            'content': 'This is valid content with enough length.',
            'status': 'published'
        })
        self.assertTrue(serializer.is_valid())
        
        # Invalid - title too short
        serializer = PostCreateUpdateSerializer(data={
            'title': 'ab',
            'content': 'Valid content length.',
            'status': 'published'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # Invalid - content too short
        serializer = PostCreateUpdateSerializer(data={
            'title': 'Valid Title',
            'content': 'Short',
            'status': 'published'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_comment_serializer_validation(self):
        """Test CommentCreateSerializer validation"""
        # Valid
        serializer = CommentCreateSerializer(data={
            'content': 'This is a valid comment content.'
        })
        self.assertTrue(serializer.is_valid())
        
        # Invalid - empty content
        serializer = CommentCreateSerializer(data={'content': ''})
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)
