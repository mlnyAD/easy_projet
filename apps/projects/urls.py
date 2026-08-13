

from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectListView,
    ProjectLocationView,
    ProjectUpdateView,
    ProjectWorkspaceView,
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
]