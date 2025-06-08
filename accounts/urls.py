from django.urls import path
from .views import ProfileView, signup
from django.contrib.auth.views import LoginView, LogoutView

app_name = "accounts"
urlpatterns = [
    path(
        "login/",
        LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Original path for logged-in user's own profile (no argument)
    path("profile/", ProfileView.as_view(), name="own_profile"),
    # Path for viewing a profile by username
    path("profile/<str:username>/", ProfileView.as_view(), name="profile"),
    path("signup/", signup, name="signup"),
]
