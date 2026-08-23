

from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from apps.documents.services import DocumentTemplateService


class DocumentTemplateServiceTests(SimpleTestCase):

    def setUp(self):
        self.temporary_directory = TemporaryDirectory()

        self.template_root = Path(
            self.temporary_directory.name
        )

        (
            self.template_root
            / "empty.docx"
        ).write_bytes(
            b"DOCX TEST"
        )

        (
            self.template_root
            / "empty.xlsx"
        ).write_bytes(
            b"XLSX TEST"
        )

        (
            self.template_root
            / "empty.pptx"
        ).write_bytes(
            b"PPTX TEST"
        )

        self.service = DocumentTemplateService(
            template_root=self.template_root
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_get_word_definition(self):
        definition = self.service.get_definition(
            "word"
        )

        self.assertEqual(
            definition["filename"],
            "empty.docx",
        )

        self.assertEqual(
            definition["extension"],
            ".docx",
        )

    def test_get_excel_definition(self):
        definition = self.service.get_definition(
            "excel"
        )

        self.assertEqual(
            definition["filename"],
            "empty.xlsx",
        )

        self.assertEqual(
            definition["extension"],
            ".xlsx",
        )

    def test_get_powerpoint_definition(self):
        definition = self.service.get_definition(
            "powerpoint"
        )

        self.assertEqual(
            definition["filename"],
            "empty.pptx",
        )

        self.assertEqual(
            definition["extension"],
            ".pptx",
        )

    def test_format_is_case_insensitive(self):
        definition = self.service.get_definition(
            "WORD"
        )

        self.assertEqual(
            definition["filename"],
            "empty.docx",
        )

    def test_unknown_format_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.get_definition(
                "pdf"
            )

    def test_open_word_template(self):
        with self.service.open_template(
            "word"
        ) as content:
            data = content.read()

        self.assertEqual(
            data,
            b"DOCX TEST",
        )

    def test_missing_template_is_rejected(self):
        (
            self.template_root
            / "empty.docx"
        ).unlink()

        with self.assertRaises(FileNotFoundError):
            self.service.open_template(
                "word"
            )