

from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from .views import (
    AccountUpdateView,
    UserCreateView,
    UserListView,
    UserUpdateView,
)


app_name = "users"

urlpatterns = [
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
        "logout/",
        LogoutView.as_view(
            next_page=reverse_lazy("home"),
        ),
        name="logout",
    ),
    path(
        "account/",
        AccountUpdateView.as_view(),
        name="account",
    ),
]