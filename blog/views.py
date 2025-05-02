import os
import uuid
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

from .forms import CommentForm, PostForm, SignupForm, SearchForm
from .models import Post


# Create your views here.
class IndexView(ListView):
    template_name = "blog/index.html"
    context_object_name = "post_list"

    def get_queryset(self):
        """
        Return published posts; order by: -pub_date(most recent appear first)
        """

        return Post.objects.filter(status="published").order_by("-pub_date")


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

    # override get method to increment views when a post is viewed
    def get(self, request, *args, **kwargs):
        # Call the parent class's get method to set up the response
        response = super().get(request, *args, **kwargs)

        # Increment the views count for the post
        self.object.increment_views()

        return response

    # override get_context_data method to add additional context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context["likes"] = post.likes
        context["reading_time"] = post.reading_time
        context["user_has_liked"] = self.request.user in post.liked_by.all()
        context["comments"] = post.comments.filter(approved=True).order_by('-created_date')
        context["comment_form"] = CommentForm()

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post 
    form_class = PostForm
    template_name = "blog/create_post.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.request.META.get('HTTP_REFERER', reverse_lazy('blog:index'))
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        return response

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={'slug':self.object.slug})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/edit_post.html"

    def test_func(self):
        """Ensure only the author can edit the post"""
        post = self.get_object()

        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/delete_post.html"
    success_url = "/"  # Redirect to the home page after deletion

    def test_func(self):
        """Ensure only the author can delete the post."""
        post = self.get_object()

        return self.request.user == post.author

class SearchView(ListView):
    template_name = "blog/search_results.html"
    context_object_name = "post_list"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        if query:
            return Post.objects.filter(
                Q(status="published") &
                (Q(title__icontains=query) |
                 Q(content__icontains=query) |
                 Q(author__username__icontains=query))
            ).distinct().order_by("pub_date")

        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        context['form'] = SearchForm(self.request.GET)
        return context
    

@csrf_exempt
def trix_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'uploads'), exist_ok=True)

            #Generate unique filename to prevent collisions
            file_ext = os.path.splitext(file.name)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            file_path = default_storage.save(f"uploads/{file_name}", file)

            file_url = f"{settings.MEDIA_URL}{file_path}"
            return JsonResponse({'url': file_url})
    return JsonResponse({'error': 'Upload failed'}, status=400)


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("blog:index")
    else:
        form = SignupForm()

    return render(request, "blog/signup.html", {"form": form})


@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        post.likes -= 1
    else:
        post.liked_by.add(request.user)
        post.likes += 1
    post.save()

    return JsonResponse(
        {
            "likes": post.likes,
            "user_has_liked": request.user in post.liked_by.all(),
        }
    )


@login_required
def comment(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            return JsonResponse({
                'success': True,
                'author': request.user.username,
                'created_date': comment.created_date.strftime("%B %d, %Y %H:%M"),
                'content': comment.content,
                'comments_count': post.comments.filter(approved=True).count()
            })

    return JsonResponse({'success': False}, status=400)
