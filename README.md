# krita-dds-plugin

A Krita plugin for importing and exporting DDS files using Pillow. Works with Krita's Steam/AppImage builds without needing ImageMagick or other external binaries.

## Dependencies

- [Pillow](https://pillow.readthedocs.io/)

## Install

1. Install Pillow for Krita's Python:

**Linux:**
```sh
pip install --target=~/.local/share/krita/python-deps --python-version=3.10 --only-binary=:all: Pillow
```

**Windows:**
```powershell
pip install --target="%APPDATA%\krita\python-deps" --python-version=3.10 --only-binary=:all: Pillow
```

2. Download the latest `dds_import_export.zip` from [releases](https://github.com/antistrategie/krita-dds-plugin/releases), then in Krita go to **Tools > Scripts > Import Python Plugins...** and select the zip.

3. Restart Krita.
4. Go to **Settings > Configure Krita > Python Plugin Manager** and enable **DDS Import/Export**.
5. Restart Krita.

## Usage

Go to **Tools > Scripts** and use **Import DDS** or **Export DDS**.

## Licence

MIT
