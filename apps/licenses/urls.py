

from django.urls import path

from .views import (
    LicenseCreateView,
    LicenseListView,
    LicenseUpdateView,
)


app_name = "licenses"

urlpatterns = [
    path(
        "",
        LicenseListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        LicenseCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        LicenseUpdateView.as_view(),
        name="update",
    ),
]