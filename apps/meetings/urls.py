

from django.urls import path

from .views import (
    MeetingCreateView,
    MeetingListByProjectView,
    MeetingListView,
    MeetingParticipantCreateView,
    MeetingParticipantListView,
    MeetingParticipantUpdateView,
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
    path(
        "<uuid:meeting_pk>/participants/",
        MeetingParticipantListView.as_view(),
        name="participant-list",
    ),
    path(
        "<uuid:meeting_pk>/participants/new/",
        MeetingParticipantCreateView.as_view(),
        name="participant-create",
    ),
    path(
        "<uuid:meeting_pk>/participants/<uuid:pk>/edit/",
        MeetingParticipantUpdateView.as_view(),
        name="participant-update",
    ),
]