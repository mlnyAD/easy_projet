

from django.urls import path

from .views import (
    CommunicationAttachmentDownloadView,
    CommunicationInboxView,
    CommunicationMarkReadView,
    CommunicationMessageCreateView,
)


app_name = "communications"


urlpatterns = [
    path(
        "",
        CommunicationInboxView.as_view(),
        name="inbox",
    ),
    path(
        "messages/",
        CommunicationMessageCreateView.as_view(),
        name="message-create",
    ),
    path(
        "read/",
        CommunicationMarkReadView.as_view(),
        name="mark-read",
    ),
    path(
        "attachments/<uuid:pk>/download/",
        CommunicationAttachmentDownloadView.as_view(),
        name="attachment-download",
    ),
]