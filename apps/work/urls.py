

from django.urls import path

from .views import (
    WorkPackageCreateView,
    WorkPackageListView,
    WorkPackageUpdateView,
)

app_name = "work"

urlpatterns = [
    path(
        "",
        WorkPackageListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        WorkPackageCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        WorkPackageUpdateView.as_view(),
        name="update",
    ),
]