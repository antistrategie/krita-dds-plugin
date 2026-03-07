import os
import struct
import tempfile

from krita import Extension, Krita
from PIL import Image
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
)

# DDS header constants
_DDS_MAGIC = b"DDS "
_DDS_HEADER_SIZE = 128
_DDPF_RGB = 0x40
_DDPF_ALPHAPIXELS = 0x01


def _parse_uncompressed_dds(path):
    """Fallback parser for uncompressed DDS files that Pillow can't handle."""
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic != _DDS_MAGIC:
            return None

        header = f.read(124)
        height = struct.unpack_from("<I", header, 8)[0]
        width = struct.unpack_from("<I", header, 12)[0]

        # Pixel format starts at offset 72 in the header
        pf_flags = struct.unpack_from("<I", header, 76)[0]
        pf_bitcount = struct.unpack_from("<I", header, 84)[0]
        r_mask = struct.unpack_from("<I", header, 88)[0]
        g_mask = struct.unpack_from("<I", header, 92)[0]
        b_mask = struct.unpack_from("<I", header, 96)[0]
        a_mask = struct.unpack_from("<I", header, 100)[0]

        if not (pf_flags & _DDPF_RGB):
            return None

        has_alpha = bool(pf_flags & _DDPF_ALPHAPIXELS)
        bpp = pf_bitcount // 8

        if bpp not in (3, 4):
            return None

        # Work out channel positions from bitmasks
        def _shift(mask):
            if mask == 0:
                return 0
            s = 0
            while (mask >> s) & 1 == 0:
                s += 1
            return s

        r_shift = _shift(r_mask)
        g_shift = _shift(g_mask)
        b_shift = _shift(b_mask)
        a_shift = _shift(a_mask) if has_alpha else 0

        # Read only the first mip level
        pixel_data = f.read(width * height * bpp)

    pixels = bytearray(width * height * (4 if has_alpha else 3))
    out_bpp = 4 if has_alpha else 3

    for i in range(width * height):
        raw = int.from_bytes(pixel_data[i * bpp : (i + 1) * bpp], "little")
        pixels[i * out_bpp] = (raw >> r_shift) & 0xFF
        pixels[i * out_bpp + 1] = (raw >> g_shift) & 0xFF
        pixels[i * out_bpp + 2] = (raw >> b_shift) & 0xFF
        if has_alpha:
            pixels[i * out_bpp + 3] = (raw >> a_shift) & 0xFF

    mode = "RGBA" if has_alpha else "RGB"
    return Image.frombytes(mode, (width, height), bytes(pixels))


def _open_dds(path):
    """Open a DDS file, falling back to manual parsing if Pillow fails."""
    try:
        return Image.open(path)
    except Exception:
        img = _parse_uncompressed_dds(path)
        if img is not None:
            return img
        raise


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
            img = _open_dds(input_file)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            img.save(tmp_path, "PNG")

            doc = Krita.instance().openDocument(tmp_path)
            Krita.instance().activeWindow().addView(doc)
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

        dialog = QDialog()
        dialog.setWindowTitle("DDS Export Options")
        layout = QVBoxLayout(dialog)
        flip_check = QCheckBox("Flip vertically")
        layout.addWidget(flip_check)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() != QDialog.Accepted:
            return

        try:
            original_path = doc.fileName()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            doc.saveAs(tmp_path)
            doc.setFileName(original_path)

            img = Image.open(tmp_path)
            if flip_check.isChecked():
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img.save(save_file, "DDS")
            os.unlink(tmp_path)

            QMessageBox.information(None, "DDS Export", f"Saved: {save_file}")
        except Exception as e:
            QMessageBox.critical(None, "DDS Export Error", str(e))
