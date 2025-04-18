from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from .forms import CommentForm, PostForm, SignupForm
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
def create_post(request):
    if request.method == "POST":
        # Include request.FILES for file uploads
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            # Set the author to the logged-in user
            post.author = request.user
            post.save()
            form.save_m2m()  # Save many-to-many data for the form (e.g., tags)

            return redirect("blog:post_detail", slug=post.slug)
    else:
        form = PostForm()

    return render(request, "blog/create_post.html", {"form": form})


@login_required
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user in post.liked_by.all():
        # user already liked the post, so unlike it
        post.liked_by.remove(request.user)
        post.likes -= 1
    else:
        # user is liking the post
        post.liked_by.add(request.user)
        post.likes += 1
    post.save()

    # Return updated like count and a flag for whether the user has liked it

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
