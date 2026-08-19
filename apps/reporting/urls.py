

from django.urls import path

from .views import (
    ActivityReportReviewDetailView,
    ActivityReportReviewListView,
    ActivityReportView,
)

app_name = "reporting"


urlpatterns = [
    path(
        "",
        ActivityReportView.as_view(),
        name="week",
    ),
    path(
        "reviews/",
        ActivityReportReviewListView.as_view(),
        name="review-list",
    ),
    path(
        "reviews/<uuid:pk>/",
        ActivityReportReviewDetailView.as_view(),
        name="review-detail",
    ),
]