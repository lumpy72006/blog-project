from django.shortcuts import render
from .models import Post
from django.views.generic import ListView, DetailView

# Create your views here.
class IndexView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        """
        Return the last five published posts (not including those set to be
        published in the future).
        """
        return Post.objects.filter(status='published').order_by("-pub_date")

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
