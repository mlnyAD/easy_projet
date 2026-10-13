

from django.urls import path

from apps.integrations.services.ai_views import AIAssistantView
from .views import (
    ExternalIntegrationCreateView,
    ExternalIntegrationListView,
    ExternalIntegrationUpdateView,
)


app_name = "integrations"


urlpatterns = [
    path(
        "",
        ExternalIntegrationListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        ExternalIntegrationCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        ExternalIntegrationUpdateView.as_view(),
        name="update",
    ),
    path(
        "ai/assistant/",
        AIAssistantView.as_view(),
        name="ai-assistant",
    ),
]