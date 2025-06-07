from django.urls import path

from .views import (
    IndexView,
    PostDetailView,
    PostCreateView,
    like_post,
    PostUpdateView,
    PostDeleteView,
    SearchView,
    comment,
    trix_upload,
)

app_name = "blog"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("search/", SearchView.as_view(), name="search"),
    path("new-post/", PostCreateView.as_view(), name="create_post"),
    path("trix-upload/", trix_upload, name="trix_upload"),
    path("<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("<slug:slug>/edit/", PostUpdateView.as_view(), name="edit_post"),
    path("<slug:slug>/delete/", PostDeleteView.as_view(), name="delete_post"),
    path("<slug:slug>/like/", like_post, name="like_post"),
    path("<slug:slug>/comment/", comment, name="comment"),
]
