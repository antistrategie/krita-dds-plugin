import os
import sys


def _deps_path():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "krita", "python-deps")
    return os.path.expanduser("~/.local/share/krita/python-deps")


# Add persistent Pillow install to path
_path = _deps_path()
if _path not in sys.path:
    sys.path.insert(0, _path)

try:
    import PIL.Image  # noqa: F401
except ImportError:
    from PyQt5.QtWidgets import QMessageBox

    py = f"{sys.version_info[0]}.{sys.version_info[1]}"
    QMessageBox.warning(
        None,
        "DDS Import/Export",
        f"Pillow could not be imported for Python {py} "
        f"(Krita's Python version may have changed).\n"
        f"Reinstall Pillow:\n"
        f'pip install --target="{_path}" '
        f"--python-version={py} --only-binary=:all: Pillow",
    )
    raise

from .dds_import_export import DDSImportExport

Krita.instance().addExtension(DDSImportExport(Krita.instance()))
