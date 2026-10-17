

from django.urls import path

from .views import (
    TodoActionCreateView,
    TodoActionDeleteView,
    TodoActionUpdateView,
    TodoListView,
)


app_name = "todos"


urlpatterns = [
    path(
        "",
        TodoListView.as_view(),
        name="list",
    ),
    path(
        "new/",
        TodoActionCreateView.as_view(),
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        TodoActionUpdateView.as_view(),
        name="update",
    ),
    path(
        "<uuid:pk>/delete/",
        TodoActionDeleteView.as_view(),
        name="delete",
    ),
]