from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    IndexView,
    PostDetailView,
    PostCreateView,
    signup,
    like_post,
    PostUpdateView,
    PostDeleteView,
    SearchView,
    comment,
)

app_name = "blog"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("signup/", signup, name="signup"),
    path(
        "accounts/login/",
        LoginView.as_view(template_name="blog/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("search/", SearchView.as_view(), name="search"),
    path("new-post/", PostCreateView.as_view(), name="create_post"),
    path("<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("<slug:slug>/edit/", PostUpdateView.as_view(), name="edit_post"),
    path("<slug:slug>/delete/", PostDeleteView.as_view(), name="delete_post"),
    path("<slug:slug>/like/", like_post, name="like_post"),
    path("<slug:slug>/comment/", comment, name="comment"),
]
