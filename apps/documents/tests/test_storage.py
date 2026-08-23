

from io import BytesIO
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from apps.documents.storage import FileSystemDocumentStorage


class FileSystemDocumentStorageTests(SimpleTestCase):

    def setUp(self):
        self.temporary_directory = TemporaryDirectory()

        self.storage = FileSystemDocumentStorage(
            self.temporary_directory.name
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_save_file(self):
        content = BytesIO(b"Easy Projet GED")

        self.storage.save(
            "project/document/v1/test.txt",
            content,
        )

        self.assertTrue(
            self.storage.exists(
                "project/document/v1/test.txt"
            )
        )

    def test_open_file(self):
        storage_key = "project/document/v1/test.txt"

        self.storage.save(
            storage_key,
            BytesIO(b"Easy Projet GED"),
        )

        with self.storage.open(storage_key) as file:
            content = file.read()

        self.assertEqual(
            content,
            b"Easy Projet GED",
        )

    def test_existing_file_cannot_be_overwritten(self):
        storage_key = "project/document/v1/test.txt"

        self.storage.save(
            storage_key,
            BytesIO(b"Version 1"),
        )

        with self.assertRaises(FileExistsError):
            self.storage.save(
                storage_key,
                BytesIO(b"Version 2"),
            )

    def test_delete_file(self):
        storage_key = "project/document/v1/test.txt"

        self.storage.save(
            storage_key,
            BytesIO(b"Easy Projet GED"),
        )

        self.storage.delete(storage_key)

        self.assertFalse(
            self.storage.exists(storage_key)
        )

    def test_delete_unknown_file_is_allowed(self):
        self.storage.delete(
            "unknown/file.txt"
        )

    def test_empty_storage_key_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.get_path("")

    def test_parent_directory_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.get_path(
                "../../settings.py"
            )

    def test_absolute_path_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.get_path(
                "C:/Windows/System32/test.txt"
            )