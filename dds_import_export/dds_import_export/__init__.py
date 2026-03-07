import os
import sys

_EXPECTED_PYTHON = (3, 10)


def _deps_path():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "krita", "python-deps")
    return os.path.expanduser("~/.local/share/krita/python-deps")


if sys.version_info[:2] != _EXPECTED_PYTHON:
    from PyQt5.QtWidgets import QMessageBox

    QMessageBox.warning(
        None,
        "DDS Import/Export",
        f"Krita's Python version changed from {'.'.join(map(str, _EXPECTED_PYTHON))} "
        f"to {sys.version_info[0]}.{sys.version_info[1]}.\n"
        f"Reinstall Pillow:\n"
        f'pip install --target="{_deps_path()}" '
        f"--python-version={sys.version_info[0]}.{sys.version_info[1]} --only-binary=:all: Pillow",
    )

# Add persistent Pillow install to path
_path = _deps_path()
if _path not in sys.path:
    sys.path.insert(0, _path)

from .dds_import_export import DDSImportExport

Krita.instance().addExtension(DDSImportExport(Krita.instance()))
