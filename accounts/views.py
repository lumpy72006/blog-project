import logging
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from .forms import ProfileForm, SignupForm
from .models import Profile

logger = logging.getLogger(__name__)

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

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/edit_profile.html"
    context_object_name = 'profile_obj' # Renamed to avoid conflict with 'profile' context

    # Override get_object to ensure we are editing the logged-in user's profile
    def get_object(self, queryset=None):
        return self.request.user.profile

    # Define where to redirect after successful update
    def get_success_url(self):
        return reverse('accounts:own_profile')


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
