

from django.urls import path

from apps.documents.views import (
    DocumentCreateView,
    DocumentEditorView,
    DocumentExplorerView,
    DocumentFolderCreateView,
    DocumentFolderDeleteView,
    DocumentFolderRenameView,
    DocumentVersionCallbackView,
    DocumentVersionContentView,
    DocumentImportView,
    DocumentVersionDownloadView,
    DocumentVersionView,
    DocumentRenameView,
    DocumentMoveView,
    DocumentCopyView,
    DocumentFavoriteAddView,
    DocumentFavoriteRemoveView,
    DocumentFavoriteListView,
    DocumentDeleteView,
)


app_name = "documents"


urlpatterns = [
    path(
        "projects/<uuid:project_id>/",
        DocumentExplorerView.as_view(),
        name="explorer",
    ),

    path(
        (
            "projects/<uuid:project_id>/"
            "folders/<uuid:folder_id>/"
        ),
        DocumentExplorerView.as_view(),
        name="folder",
    ),

    path(
        "projects/<uuid:project_id>/new/",
        DocumentCreateView.as_view(),
        name="create",
    ),

    path(
        (
            "projects/<uuid:project_id>/"
            "folders/create/"
        ),
        DocumentFolderCreateView.as_view(),
        name="folder-create",
    ),

    path(
        (
            "projects/<uuid:project_id>/"
            "folders/<uuid:folder_id>/rename/"
        ),
        DocumentFolderRenameView.as_view(),
        name="folder-rename",
    ),

    path(
        (
            "projects/<uuid:project_id>/"
            "folders/<uuid:folder_id>/delete/"
        ),
        DocumentFolderDeleteView.as_view(),
        name="folder-delete",
    ),

    path(
        "versions/<uuid:version_id>/edit/",
        DocumentEditorView.as_view(),
        name="version-edit",
    ),

    path(
        "versions/<uuid:version_id>/content/",
        DocumentVersionContentView.as_view(),
        name="version-content",
    ),

    path(
        "versions/<uuid:version_id>/callback/",
        DocumentVersionCallbackView.as_view(),
        name="version-callback",
    ),
    path(
        (
            "projects/<uuid:project_id>/"
            "folders/<uuid:folder_id>/import/"
        ),
        DocumentImportView.as_view(),
        name="import",
    ),
    path(
        "versions/<uuid:version_id>/view/",
        DocumentVersionView.as_view(),
        name="version-view",
    ),

    path(
        "versions/<uuid:version_id>/download/",
        DocumentVersionDownloadView.as_view(),
        name="version-download",
    ),  
    path(
        (
            "projects/<uuid:project_id>/"
            "documents/<uuid:document_id>/rename/"
        ),
        DocumentRenameView.as_view(),
        name="document-rename",
    ),  
    path(
        (
            "projects/<uuid:project_id>/"
            "documents/<uuid:document_id>/move/"
        ),
        DocumentMoveView.as_view(),
        name="document-move",
    ),
    path(
        (
            "projects/<uuid:project_id>/"
            "documents/<uuid:document_id>/copy/"
        ),
        DocumentCopyView.as_view(),
        name="document-copy",
    ),
    path(
        (
            "projects/<uuid:project_id>/"
            "documents/<uuid:document_id>/favorite/add/"
        ),
        DocumentFavoriteAddView.as_view(),
        name="document-favorite-add",
    ),

    path(
        (
            "projects/<uuid:project_id>/"
            "documents/<uuid:document_id>/favorite/remove/"
        ),
        DocumentFavoriteRemoveView.as_view(),
        name="document-favorite-remove",
    ),
    path(
        "favorites/",
        DocumentFavoriteListView.as_view(),
        name="favorites",
    ),
    path(
        (
            "projects/<uuid:project_id>/"
            "documents/<uuid:document_id>/delete/"
        ),
        DocumentDeleteView.as_view(),
        name="document-delete",
    ),
]