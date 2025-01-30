from django.urls import path

from .views import IndexView, PostDetailView

app_name = 'blog'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
]
