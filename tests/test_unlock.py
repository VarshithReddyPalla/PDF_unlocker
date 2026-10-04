import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from pypdf import PdfReader, PdfWriter

from unlock import PDFUnlockerApp


class ProcessingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.pdf = self.directory / "document.pdf"
        self.backups = self.directory / "backups"
        self.app = PDFUnlockerApp.__new__(PDFUnlockerApp)
        self.app.backup_folder = str(self.backups)
        self.app.password_var = Mock()
        self.app.password_var.get.return_value = "test-password"
        self.app.password_entry = Mock()
        self.app.status = Mock()
        self.app.root = Mock()
        self.dialogs = patch("unlock.messagebox").start()
        self.addCleanup(patch.stopall)
        self.dialogs.askyesno.return_value = True

    def create_pdf(self, encrypted=True):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        if encrypted:
            writer.encrypt("test-password", algorithm="AES-256")
        with self.pdf.open("wb") as output:
            writer.write(output)
        return self.pdf.read_bytes()

    def test_unlock_preserves_original_backup_and_pages(self):
        original = self.create_pdf()
        self.app.process_pdfs([str(self.pdf)])
        self.assertEqual((self.backups / self.pdf.name).read_bytes(), original)
        reader = PdfReader(self.pdf)
        self.assertFalse(reader.is_encrypted)
        self.assertEqual(len(reader.pages), 1)
        self.dialogs.showinfo.assert_called_once()

    def test_wrong_password_leaves_original_unchanged(self):
        original = self.create_pdf()
        self.app.password_var.get.return_value = "wrong-password"
        self.app.process_pdfs([str(self.pdf)])
        self.assertEqual(self.pdf.read_bytes(), original)
        self.assertEqual(list(self.backups.iterdir()), [])
        self.dialogs.showwarning.assert_called_once()

    def test_existing_backup_is_not_overwritten(self):
        original = self.create_pdf()
        self.backups.mkdir()
        existing = self.backups / self.pdf.name
        existing.write_bytes(b"previous backup")
        self.app.process_pdfs([str(self.pdf)])
        self.assertEqual(existing.read_bytes(), b"previous backup")
        self.assertEqual(
            (self.backups / "document_backup_1.pdf").read_bytes(), original
        )

    def test_unencrypted_pdf_is_unchanged(self):
        original = self.create_pdf(encrypted=False)
        self.app.process_pdfs([str(self.pdf)])
        self.assertEqual(self.pdf.read_bytes(), original)
        self.assertEqual(list(self.backups.iterdir()), [])

    def test_failed_write_preserves_original_and_cleans_temporary_file(self):
        original = self.create_pdf()
        with patch("unlock.PdfWriter.write", side_effect=OSError("Disk full")):
            self.app.process_pdfs([str(self.pdf)])
        self.assertEqual(self.pdf.read_bytes(), original)
        self.assertEqual((self.backups / self.pdf.name).read_bytes(), original)
        self.assertEqual(list(self.directory.glob("*.pdf")), [self.pdf])
        self.dialogs.showwarning.assert_called_once()

    def test_cancel_leaves_original_and_creates_no_backup(self):
        original = self.create_pdf()
        self.dialogs.askyesno.return_value = False
        self.app.process_pdfs([str(self.pdf)])
        self.assertEqual(self.pdf.read_bytes(), original)
        self.assertEqual(list(self.backups.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
