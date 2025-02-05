from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import IndexView, PostDetailView, create_post, signup, like_post

app_name = 'blog'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('signup/', signup, name='signup'),
    path('accounts/login/', LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('new-post/', create_post, name='create_post'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/like/', like_post, name='like_post'),
]
