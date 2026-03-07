import os
import sys

_EXPECTED_PYTHON = (3, 10)

if sys.version_info[:2] != _EXPECTED_PYTHON:
    from PyQt5.QtWidgets import QMessageBox

    QMessageBox.warning(
        None,
        "DDS Import/Export",
        f"Krita's Python version changed from {'.'.join(map(str, _EXPECTED_PYTHON))} "
        f"to {sys.version_info[0]}.{sys.version_info[1]}.\n"
        f"Reinstall Pillow: pip install --target=~/.local/lib/python-krita-deps "
        f"--python-version={sys.version_info[0]}.{sys.version_info[1]} --only-binary=:all: Pillow",
    )

# Add persistent Pillow install to path
_deps_path = os.path.expanduser("~/.local/lib/python-krita-deps")
if _deps_path not in sys.path:
    sys.path.insert(0, _deps_path)

from .dds_import_export import DDSImportExport

Krita.instance().addExtension(DDSImportExport(Krita.instance()))
