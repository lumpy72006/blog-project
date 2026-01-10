# type: ignore
from rest_framework.reverse import reverse
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from accounts.models import Profile
from blog.models import Comment, Post


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Profile model (bio, picture)
    """
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Replicates logic from accounts/forms.py SignupForm
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': "This email is already registered."})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        user = User.objects.create_user(**validated_data)

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for User
    """
    bio = serializers.CharField(source='profile.bio', allow_blank=True, required=False)
    profile_picture = serializers.ImageField(source='profile.profile_picture', allow_null=True, required=False)
    posts_count = serializers.SerializerMethodField()
    posts_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'profile_picture', 'date_joined', 'last_login', 'posts_url', 'posts_count']
        read_only_fields = ['username', 'email', 'last_login', 'date_joined']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published', pub_date__lte=timezone.now()).count()

    def get_posts_url(self, obj):
        request = self.context.get('request')
        if request:
            return reverse('api:user-posts', 
                         kwargs={'username': obj.username}, 
                         request=request)
        return None

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        profile = instance.profile

        if 'bio' in profile_data:
            profile.bio = profile_data['bio']

        if 'profile_picture' in profile_data:
            profile.profile_picture = profile_data['profile_picture']

        profile.save()

        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used when we need to show author info in posts/comments.
    """
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['username', 'profile']


class UserListSerializer(serializers.ModelSerializer):
    """
    Simple serializer for listing users
    """
    profile = ProfileSerializer(read_only=True)
    profile_url = serializers.SerializerMethodField()
    posts_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['username', 'profile', 'profile_url', 'posts_url']
    
    def get_posts_url(self, obj):
        request = self.context.get('request')
        if request:
            return reverse('api:user-posts', 
                         kwargs={'username': obj.username}, 
                         request=request)
        return None

    def get_profile_url(self, obj):
        request = self.context.get('request')
        if request:
            return reverse('api:user-detail',
                           kwargs={'username': obj.username},
                           request=request)
        return None

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    author is read-only because we set it automatically from request.user
    """
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['content', 'author', 'created_date', 'approved']
        read_only_fields = ['created_date', 'approved']


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    post and author are set in the view, not by user input.
    """
    class Meta:
        model = Comment
        fields = ['content']

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment cannot be empty")
        return value


class PostListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing posts.
    Does not include full content or comments
    """
    author = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name='api:post-detail',
        lookup_field='slug',
        lookup_url_kwarg='slug'
    )

    class Meta:
        model = Post
        fields = [
            'url',
            'title',
            'slug',
            'excerpt', # short preview instead of full content
            'author',
            'status',
            'pub_date',
            'views_count',
            'reading_time',
            'likes',
            'comments_count',
            'featured_image',
        ]

    def get_comments_count(self, obj) -> int:
        """Count approved comments only"""
        return len([comment for comment in obj.comments.all() if comment.approved])

    def get_excerpt(self, obj) -> str:
        """Get the first 100 characters of the content as preview"""
        # Strip HTML tags for clean excerpt
        from django.utils.html import strip_tags
        cleaned_content = strip_tags(obj.content)

        if len(cleaned_content) > 100:
            return cleaned_content[:100] + '...'
        return cleaned_content


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for a single post view.
    Includes full content, comments, etc.
    """
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'title', 
            'slug', 
            'content',
            'author',
            'status', 
            'created_date', 
            'pub_date', 
            'last_updated',
            'reading_time', 
            'views_count', 
            'likes',
            'is_liked',
            'is_author',
            'featured_image', 
            'comments',
            'comments_count'
        ]
        read_only_fields = [
            'slug', 
            'created_date', 
            'last_updated',
            'reading_time', 
            'views_count', 
            'likes'
        ]

    def get_comments_count(self, obj) -> int:
        return len([comment for comment in obj.comments.all() if comment.approved])

    def get_is_liked(self, obj) -> bool:
        """Check if current user has liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False

    def get_is_author(self, obj) -> bool:
        """Check if current user is the author (for edit/delete permissions)"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating posts.
    Only includes fields the user should be able to set.
    """
    class Meta:
        model = Post
        fields = ['title', 'content', 'status', 'featured_image']

    def validate_title(self, value):
        """Ensure title is not empty or just whitespace"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters")
        return value.strip()

    def validate_content(self, value):
        """Ensure content has minimum length"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters")
        return value
