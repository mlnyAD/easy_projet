

from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectListView,
    ProjectLocationView,
    ProjectPhotoUpdateView,
    ProjectUpdateView,
    ProjectWorkspaceView,
    ProjectDashboardView,
)


app_name = "projects"

urlpatterns = [
    path(
        "",
        ProjectListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        ProjectCreateView.as_view(),
        name="create",
    ),
    path(
        "locations/",
        ProjectLocationView.as_view(),
        name="locations",
    ),
    path(
        "<uuid:pk>/",
        ProjectWorkspaceView.as_view(),
        name="workspace",
    ),
    path(
        "<uuid:pk>/edit/",
        ProjectUpdateView.as_view(),
        name="update",
    ),
    path(
        "<uuid:pk>/photo/",
        ProjectPhotoUpdateView.as_view(),
        name="photo",
    ),
    path(
        "<uuid:pk>/dashboard/",
        ProjectDashboardView.as_view(),
        name="dashboard",
    ),
]