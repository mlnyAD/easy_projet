

from django.urls import path

from .views import (
    TodoActionCreateView,
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
]