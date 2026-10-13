

from django.urls import path

from .ai_views import PlanningAIAnalysisView
from .views import PlanningHomeView


app_name = "planning"


urlpatterns = [
    path(
        "",
        PlanningHomeView.as_view(),
        name="home",
    ),
    path(
        "ai-analysis/",
        PlanningAIAnalysisView.as_view(),
        name="ai-analysis",
    ),
]