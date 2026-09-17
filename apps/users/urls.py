

from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from .client_environment_membership_views import (
    ClientEnvironmentMembershipCreateView,
    ClientEnvironmentMembershipListView,
    ClientEnvironmentMembershipUpdateView,
)
from .views import (
    AccountUpdateView,
    RequiredPasswordChangeView,
    UserCreateView,
    UserListView,
    UserLoginView,
    UserTemporaryPasswordResendView,
    UserUpdateView,
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
        "<uuid:user_pk>/client-environments/",
        ClientEnvironmentMembershipListView.as_view(),
        name="client-environment-membership-list",
    ),
    path(
        "<uuid:user_pk>/client-environments/new/",
        ClientEnvironmentMembershipCreateView.as_view(),
        name="client-environment-membership-create",
    ),
    path(
        (
            "<uuid:user_pk>/client-environments/"
            "<uuid:pk>/edit/"
        ),
        ClientEnvironmentMembershipUpdateView.as_view(),
        name="client-environment-membership-update",
    ),
    path(
        "account/",
        AccountUpdateView.as_view(),
        name="account",
    ),
]