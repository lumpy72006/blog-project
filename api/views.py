# type: ignore
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, viewsets, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import  AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserRegistrationSerializer,
)
from blog.models import Comment, Post
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.core.cache import cache

# Create your views here.
@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root - Discover all available endpoints.
    """
    response_data = {
        'users': {
            'list_all_users': reverse('api:user-list', request=request, format=format),
        },
        'current_user': {},
        'posts': {
            'all_posts': reverse('api:post-list', request=request, format=format),
            'search_posts': reverse('api:post-list', request=request, format=format) + '?search=',
            'filter_by_status': reverse('api:post-list', request=request, format=format) + '?status=published',
        },
        'authentication': {
            'register': reverse('api:register', request=request, format=format),
            'obtain_token': reverse('api:token_obtain_pair', request=request, format=format),
            'refresh_token': reverse('api:token_refresh', request=request, format=format),
        },
        'documentation': reverse('api:swagger-ui', request=request, format=format),
    }

    if request.user.is_authenticated:
        response_data['current_user']['me'] = reverse('api:user-profile',
                                            request=request, format=format)
        response_data['current_user']['my_profile'] = reverse('api:user-detail',
                                                     kwargs={'username': request.user.username},
                                                     request=request, format=format)
        response_data['current_user']['my_posts'] = reverse('api:user-posts',
                                            kwargs={'username': request.user.username},
                                            request=request, format=format)
                                                

    return Response(response_data)


class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserListView(generics.ListAPIView):
    """"
    GET /api/users/ - List all users
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/me/ - Get current user's profile
    PUT /api/users/me/ - Update current user's profile
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /api/users/<username>/ - Public User Profile
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'username'



class UserPostsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list posts by a specific user.
    GET /api/users/{username}/posts/ - List user's published posts
    """
    serializer_class = PostListSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')
        return(Post.objects.filter(
            author__username=username,
            status='published',
            pub_date__lte=timezone.now()
        ).select_related('author'))


# POST
@extend_schema_view(
    list=extend_schema(
        description="List all published posts. Authenticated users can also see their own drafts.",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                enum=['draft', 'published'],
                description='Filter posts by status'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search in title, content, or author username'
            ),
            OpenApiParameter(
                name='author__username',
                type=OpenApiTypes.STR,
                description='Filter posts by author username'
            ),
        ]
    ),
    retrieve=extend_schema(
        description="Retrieve a single published post. Authors can also retrieve their own drafts. View count is incremented."
    ),
    create=extend_schema(
        description="Create a new post. Requires authentication. Author is automatically set to the current user."
    ),
    update=extend_schema(
        description="Fully update an existing post. Requires authentication and authorship."
    ),
    partial_update=extend_schema(
        description="Partially update an existing post. Requires authentication and authorship."
    ),
    destroy=extend_schema(
        description="Delete a post. Requires authentication and authorship."
    ),
    like=extend_schema(
        request=None,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'liked': {'type': 'boolean'},
                    'likes_count': {'type': 'integer'}
                }
            }
        },
        description="Toggle like/unlike on a post. Requires authentication."
    ),
    comment=extend_schema(
        request=CommentCreateSerializer,
        responses={
            200: CommentSerializer(many=True),
            201: CommentSerializer,
        },
        description="List comments (GET) or create a comment (POST). Comment creation requires authentication."
    )
)
class PostViewSet(viewsets.ModelViewSet):
    """
    Provides:
    - GET /posts/ - List all published posts
    - POST /posts/ - Create a new post (authenticated)
    - GET /posts/{slug}/ - Retrieve a single post
    - PUT /posts/{slug}/ - Update a post (author only)
    - DELETE /posts/{slug}/ - Delete a post (author only)
    - POST /posts/{slug}/like/ - Toggle like on a post
    - GET /posts/{slug}/comments/ - List comments for a post
    - POST /posts/{slug}/comments/ - Add a comment to a post
    """
    lookup_field = 'slug'

    # enable filtering, searchin, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'author__username']
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['pub_date', 'views_count', 'likes', 'reading_time']
    ordering = ['-pub_date']

    @method_decorator(cache_page(60 * 15, key_prefix='post_list'))
    @method_decorator(vary_on_headers('Authorization'))  # For JWT/Token Auth
    @method_decorator(vary_on_cookie)                    # For Session Auth
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    def get_queryset(self):
        """
        Return queryset based on user and action.
        - List: Only published posts (unless user is author)
        - Detail: Published posts OR user's own drafts
        """
        base_queryset = Post.objects.select_related('author', 'author__profile').prefetch_related(
            'comments', 'liked_by'
        )

        if self.action == 'list':
            if not self.request.user.is_authenticated:
                return base_queryset.filter(
                    status='published',
                    pub_date__lte=timezone.now()
                )
            
            # single query with Q objects for authenticated users.
            return base_queryset.filter(
                Q(status='published', pub_date__lte=timezone.now()) |
                Q(author=self.request.user, status='draft')
            ).distinct()

        # for detail views
        return base_queryset.prefetch_related('comments__author')

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on action.
        """
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_permissions(self):
        """
        Set permissions based on action.
        - List/Retrieve: Anyone can read 
        - Create: Must be authenticated
        - Update/Delete: Must be author
        """

        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        # like, comment, etc.
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        """
        Set author to current user when creating a post.
        """
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Get single post and increment view count.
        """
        instance = self.get_object()

        is_published = (instance.status == 'published' and instance.pub_date <= timezone.now())
        is_author = (request.user.is_authenticated and request.user == instance.author)

        if not(is_published or is_author):
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        instance.increment_views()

        cache_key = f"post_detail{instance.slug}"

        serialized_data = cache.get(cache_key)

        if not serialized_data:
            # cache miss; cache and skip next timee 
            serializer = self.get_serializer(instance)
            serialized_data = serializer.data

            cache.set(cache_key, serialized_data, 60 * 5)

        # inject the fresh view count
        serialized_data['views_count'] = instance.views_count

        if request.user.is_authenticated:
            serialized_data['is_liked'] = instance.liked_by.filter(id=request.user.id).exists()
            serialized_data['is_author'] = (instance.author == request.user)
        else:
            serialized_data['is_liked'] = False
            serialized_data['is_author'] = False

        return Response(serialized_data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        """
        Toggle like on a post.
        POST /posts/{slug}/like/
        """

        post = self.get_object()
        user = request.user

        if user in post.liked_by.all():
            post.liked_by.remove(user)
            post.likes -= 1
            liked = False
        else:
            post.liked_by.add(user)
            post.likes += 1
            liked = True

        post.save()

        return Response({
            'liked': liked,
            'likes_count': post.likes
        })

    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comment(self, request, slug=None):
        """
        List or create comments for a post.
        GET /posts/{slug}/comments/ - List comments
        POST /posts/{slug}/comments/ - Create comment (authenticated)
        """

        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.filter(approved=True).select_related('author')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            # DRF permissions already ensure user is authenticated here
            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(post=post, author=request.user)

                # return full comment data
                comment = Comment.objects.select_related('author').get(
                    id=serializer.instance.id
                )
                return Response(
                    CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
