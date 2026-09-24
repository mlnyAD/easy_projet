from django.urls import path

from .views import (
    MeetingCreateView,
    MeetingListByProjectView,
    MeetingListView,
    MeetingProjectUsersView,
    MeetingSendInvitationsView,
    MeetingUpdateView,
)


app_name = "meetings"


urlpatterns = [
    path("", MeetingListView.as_view(), name="list"),
    path("new/", MeetingCreateView.as_view(), name="create"),
    path(
        "project-users/",
        MeetingProjectUsersView.as_view(),
        name="project-users",
    ),
    path(
        "projects/<uuid:project_pk>/",
        MeetingListByProjectView.as_view(),
        name="list-by-project",
    ),
    path(
        "<uuid:pk>/send-invitations/",
        MeetingSendInvitationsView.as_view(),
        name="send-invitations",
    ),
    path("<uuid:pk>/edit/", MeetingUpdateView.as_view(), name="update"),
]
