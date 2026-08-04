

"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import include, path

from apps.core.views import HomeView


urlpatterns = [
    path(
        "",
        HomeView.as_view(),
        name="home",
    ),
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "catalogs/",
        include("apps.catalogs.urls"),
    ),
    path(
        "companies/",
        include("apps.companies.urls"),
    ),
    path(
        "users/",
        include("apps.users.urls"),
    ),
    path(
        "licenses/",
        include("apps.licenses.urls"),
    ),
    path(
        "projects/",
        include("apps.projects.urls"),
    ),
]