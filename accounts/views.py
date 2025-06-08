from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView

from .forms import SignupForm
from .models import Profile

# Create your views here.
class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile.html"
    context_object_name = 'profile_obj' # Renamed to avoid conflict with 'profile' context

    def get_object(self, queryset=None):
        # Check if a username is provided in the URL
        username = self.kwargs.get('username')
        if username:
            # If username is provided, fetch the User and then their Profile
            user = get_object_or_404(User, username=username)
            return user.profile
        else:
            # If no username, return the logged-in user's profile
            return self.request.user.profile

    # override get_context_data method to add additional context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = self.object.user.posts.all()
        return context


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("blog:index")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})
