import os
import tempfile

from krita import Extension, Krita
from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QMessageBox


class DDSImportExport(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action_import = window.createAction(
            "DDS_PIL_IMPORT", "Import DDS", "tools/scripts"
        )
        action_import.triggered.connect(self.import_dds)

        action_export = window.createAction(
            "DDS_PIL_EXPORT", "Export DDS", "tools/scripts"
        )
        action_export.triggered.connect(self.export_dds)

    def import_dds(self):
        input_file, _ = QFileDialog.getOpenFileName(
            caption="Import DDS", filter="DDS files (*.dds)"
        )
        if not input_file:
            return

        try:
            img = Image.open(input_file)
            # Save as temporary PNG for Krita to open
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            img.save(tmp_path, "PNG")

            doc = Krita.instance().openDocument(tmp_path)
            Krita.instance().activeWindow().addView(doc)
            # Set the document name to the original DDS filename
            doc.setFileName("")
            doc.setDocumentInfo(
                doc.documentInfo().replace(
                    "<title></title>", f"<title>{os.path.basename(input_file)}</title>"
                )
            )
            os.unlink(tmp_path)
        except Exception as e:
            QMessageBox.critical(None, "DDS Import Error", str(e))

    def export_dds(self):
        doc = Krita.instance().activeDocument()
        if not doc:
            QMessageBox.warning(None, "DDS Export", "No active document to export.")
            return

        save_file, _ = QFileDialog.getSaveFileName(
            caption="Export DDS", filter="DDS files (*.dds)"
        )
        if not save_file:
            return
        if not save_file.lower().endswith(".dds"):
            save_file += ".dds"

        try:
            # Save current document as temporary PNG
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            doc.saveAs(tmp_path)

            # Open with Pillow and save as DDS
            img = Image.open(tmp_path)
            img.save(save_file, "DDS")
            os.unlink(tmp_path)

            QMessageBox.information(None, "DDS Export", f"Saved: {save_file}")
        except Exception as e:
            QMessageBox.critical(None, "DDS Export Error", str(e))
