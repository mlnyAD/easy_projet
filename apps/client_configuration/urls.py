

from django.urls import path

from .views import (
    ClientConfigurationHomeView,
    DocumentFolderTemplateCreateView,
    DocumentFolderTemplateFolderCreateView,
    DocumentFolderTemplateFolderDeleteView,
    DocumentFolderTemplateFolderListView,
    DocumentFolderTemplateFolderUpdateView,
    DocumentFolderTemplateListView,
    DocumentFolderTemplateSetDefaultView,
    DocumentFolderTemplateUpdateView,
)


app_name = "client_configuration"


urlpatterns = [
    path(
        "",
        ClientConfigurationHomeView.as_view(),
        name="home",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
        ),
        DocumentFolderTemplateListView.as_view(),
        name="document-folder-template-list",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/new/"
        ),
        DocumentFolderTemplateCreateView.as_view(),
        name="document-folder-template-create",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
            "<uuid:template_pk>/edit/"
        ),
        DocumentFolderTemplateUpdateView.as_view(),
        name="document-folder-template-update",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
            "<uuid:template_pk>/set-default/"
        ),
        DocumentFolderTemplateSetDefaultView.as_view(),
        name="document-folder-template-set-default",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
            "<uuid:template_pk>/folders/"
        ),
        DocumentFolderTemplateFolderListView.as_view(),
        name="document-folder-template-folders",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
            "<uuid:template_pk>/folders/new/"
        ),
        DocumentFolderTemplateFolderCreateView.as_view(),
        name="document-folder-template-folder-create",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
            "<uuid:template_pk>/folders/"
            "<uuid:folder_pk>/edit/"
        ),
        DocumentFolderTemplateFolderUpdateView.as_view(),
        name="document-folder-template-folder-update",
    ),
    path(
        (
            "client-environments/"
            "<uuid:client_environment_pk>/"
            "document-folder-templates/"
            "<uuid:template_pk>/folders/"
            "<uuid:folder_pk>/delete/"
        ),
        DocumentFolderTemplateFolderDeleteView.as_view(),
        name="document-folder-template-folder-delete",
    ),
]