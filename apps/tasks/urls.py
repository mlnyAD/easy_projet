

from django.urls import path

from .views import (
    TaskCreateView,
    TaskListByWorkPackageView,
    TaskListView,
    TaskUpdateView,
)


app_name = "tasks"

urlpatterns = [
    path(
        "",
        TaskListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        TaskCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        TaskUpdateView.as_view(),
        name="update",
    ),
    path(
        "work-packages/<uuid:work_package_pk>/",
        TaskListByWorkPackageView.as_view(),
        name="list-by-work-package",
    ),
]