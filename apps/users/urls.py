

from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from .views import (
    AccountUpdateView,
    UserCreateView,
    UserListView,
    UserLoginView,
    UserTemporaryPasswordResendView,
    UserUpdateView,
    RequiredPasswordChangeView
)

app_name = "users"

urlpatterns = [
    path(
        "login/",
        UserLoginView.as_view(),
        name="login",
    ),
    path(
        "password/change-required/",
        RequiredPasswordChangeView.as_view(),
        name="password-change-required",
    ),
    path(
        "logout/",
        LogoutView.as_view(
            next_page=reverse_lazy(
                "users:login"
            ),
        ),
        name="logout",
    ),
    path(
        "",
        UserListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        UserCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        UserUpdateView.as_view(),
        name="update",
    ),
    path(
        "<uuid:pk>/temporary-password/resend/",
        UserTemporaryPasswordResendView.as_view(),
        name="temporary-password-resend",
    ),
    path(
        "account/",
        AccountUpdateView.as_view(),
        name="account",
    ),
]