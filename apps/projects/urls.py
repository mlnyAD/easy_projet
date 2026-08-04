

from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectListView,
    ProjectUpdateView,
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
        "<uuid:pk>/edit/",
        ProjectUpdateView.as_view(),
        name="update",
    ),
]