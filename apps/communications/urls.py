

from django.urls import path

from .views import (
    CommunicationAttachmentDownloadView,
    ProjectCommunicationMessageCreateView,
    ProjectCommunicationMarkReadView
)


app_name = "communications"


urlpatterns = [
    path(
        "projects/<uuid:project_pk>/messages/",
        ProjectCommunicationMessageCreateView.as_view(),
        name="project-message-create",
    ),
    path(
        "attachments/<uuid:pk>/download/",
        CommunicationAttachmentDownloadView.as_view(),
        name="attachment-download",
    ),
    path(
        "projects/<uuid:project_pk>/read/",
        ProjectCommunicationMarkReadView.as_view(),
        name="project-mark-read",
    ),
]