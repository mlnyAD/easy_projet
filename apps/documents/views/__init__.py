

from .cadviewer import DocumentCadViewerView
from .content import (
    DocumentFolderDownloadView,
    DocumentVersionCallbackView,
    DocumentVersionContentView,
    DocumentVersionDownloadView,
    DocumentVersionView,
)
from .create import DocumentCreateView
from .doe import DoeGenerateView
from .document import (
    DocumentCopyView,
    DocumentDeleteView,
    DocumentFavoriteAddView,
    DocumentFavoriteRemoveView,
    DocumentMoveView,
    DocumentPropertiesView,
    DocumentRenameView,
    DocumentRestoreView,
    DocumentPermanentDeleteView
)
from .editor import (
    DocumentEditLockRefreshView,
    DocumentEditorView,
)
from .explorer import DocumentExplorerView
from .favorites import DocumentFavoriteListView
from .folder import (
    DocumentFolderCreateView,
    DocumentFolderDeleteView,
    DocumentFolderDoeSelectionView,
    DocumentFolderMoveView,
    DocumentFolderRenameView,
)
from .import_view import DocumentImportView
from .photo_album import ProjectPhotoAlbumView
from .signature import SignatureRequestCreateView
from .trash import DocumentTrashListView


__all__ = [
    "DocumentCadViewerView",
    "DocumentCopyView",
    "DocumentCreateView",
    "DocumentDeleteView",
    "DocumentEditLockRefreshView",
    "DocumentEditorView",
    "DocumentExplorerView",
    "DocumentFavoriteAddView",
    "DocumentFavoriteListView",
    "DocumentFavoriteRemoveView",
    "DocumentFolderCreateView",
    "DocumentFolderDeleteView",
    "DocumentFolderDoeSelectionView",
    "DocumentFolderDownloadView",
    "DocumentFolderMoveView",
    "DocumentFolderRenameView",
    "DocumentImportView",
    "DocumentMoveView",
    "DocumentPropertiesView",
    "DocumentRenameView",
    "DocumentRestoreView",
    "DocumentTrashListView",
    "DocumentVersionCallbackView",
    "DocumentVersionContentView",
    "DocumentVersionDownloadView",
    "DocumentVersionView",
    "DoeGenerateView",
    "ProjectPhotoAlbumView",
    "SignatureRequestCreateView",
    "DocumentPermanentDeleteView,"
]