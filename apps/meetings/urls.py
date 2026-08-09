

from django.urls import path

from .views import (
    MeetingCreateView,
    MeetingListByProjectView,
    MeetingListView,
    MeetingUpdateView,
)


app_name = "meetings"


urlpatterns = [
    path(
        "",
        MeetingListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        MeetingCreateView.as_view(),
        name="create",
    ),
    path(
        "projects/<uuid:project_pk>/",
        MeetingListByProjectView.as_view(),
        name="list-by-project",
    ),
    path(
        "<uuid:pk>/edit/",
        MeetingUpdateView.as_view(),
        name="update",
    ),
]