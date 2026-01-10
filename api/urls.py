from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.views import (
    PostViewSet,
    UserPostsViewSet,
    api_root, 
    UserListView,
    RegisterView,
    UserDetailView,
    UserProfileView,
)

app_name = 'api'

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),

    path('users/', UserListView.as_view(), name='user-list'),
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<str:username>/posts/',
         UserPostsViewSet.as_view({'get': 'list'}),
         name='user-posts'
         ),

    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
]
