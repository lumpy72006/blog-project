from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import DetailView

from .forms import SignupForm
from .models import Profile

# Create your views here.
class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    # override get_context_data method to add additional context data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = self.request.user.posts.all()

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
