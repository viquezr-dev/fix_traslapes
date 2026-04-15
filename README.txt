# Fix Traslapes - QGIS Plugin

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-589632?style=flat&logo=qgis)](https://qgis.org)
[![Version](https://img.shields.io/badge/version-2.4-blue.svg)](https://github.com/viquezr-dev/fix_traslapes)
[![License](https://img.shields.io/badge/license-GPLv2-green.svg)](https://www.gnu.org/licenses/gpl-2.0.html)
[![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)](https://www.python.org/)

**Fix Traslapes** is a QGIS plugin that detects and automatically fixes overlaps in polygon layers, generating clean and editable result layers.

## ✨ Key Features

- 🔍 **Accurate detection** of overlaps between polygons
- ⚙️ **Configurable threshold** to ignore very small overlaps
- 🔧 **Automatic correction** through geometric clipping
- 🗺️ **Visualization layers** (red overlap polygons + centroids)
- 📊 **Editable result layer** ready for further work
- 💻 **Intuitive interface** with progress bar and detailed log

## 📋 Requirements

- **QGIS** version 3.0 or higher
- **Python** 3.9+
- **Polygon** layers (not points or lines)

## 🚀 Installation

### From the official QGIS repository (coming soon)
1. Open QGIS → Plugins → Manage and Install Plugins
2. Search for "Fix Traslapes"
3. Click "Install"

### Manual installation from GitHub
1. Download the repository as ZIP
https://github.com/viquezr-dev/fix_traslapes/archive/main.zip

2. Extract to the QGIS plugins folder:
- **Windows**: `C:\Users\YOUR_USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
- **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
- **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Rename the folder to `fix_traslapes`
4. Restart QGIS
5. Activate the plugin in Plugins → Manage Plugins

## 🎯 How to Use

### Step by step
1. **Load** a polygon layer in QGIS
2. **Open the plugin**: Toolbar button or `Plugins → Fix Traslapes` menu
3. **Select** the layer from the dropdown
4. **Configure the threshold** (optional):
- Small value (0.0001): detects almost all overlaps
- Larger value: ignores very small overlaps
5. **Optional**: Check/uncheck "Create overlap layers" as needed
6. **Click "Start"**
7. **Review** results in the log panel and on the map

### Results visualization

| Generated layer | Description |
|-----------------|-------------|
| `layer_name_OVERLAPS` | Semi-transparent red polygons showing corrected areas |
| `layer_name_CENTROIDS` | Red points at the center of each overlap for quick inspection |
| `layer_name_FIXED` | **Final layer** with clean geometries, editable and selectable |

> 💡 **Note**: The corrected layer is automatically added to the project and ready to edit or save.

## ⚙️ Advanced Configuration

### Detection threshold
- **0.0001** (default): Detects minimal overlaps (recommended for georeferenced data)
- **0.001 - 0.01**: To ignore micro-overlaps smaller than 1m²/10m² depending on your units
- Adjust according to your data scale and precision

## 🛠️ Development

### Plugin structure

fix_traslapes/
├── init.py # Plugin initialization
├── fix_traslapes_main.py # Main code
├── metadata.txt # Metadata for QGIS
└── icon.png # Plugin icon (64x64)


### Technologies used
- **PyQt5** - Graphical interface
- **QGIS Python API** - Layer and geometry manipulation
- **QThread** - Background processing

## 🐛 Bug Reporting

If you find any issues or have suggestions:
1. Check the [existing issues](https://github.com/viquezr-dev/fix_traslapes/issues)
2. Open a new issue describing:
   - QGIS version
   - Layer type (format, CRS)
   - Steps to reproduce the error
   - Screenshots (if applicable)

## 📝 Changelog

### Version 2.4 (2026-04-15)
- ✨ Improved interface with professional styles
- 🐛 Fixed layer detection errors
- ⚡ Performance optimization for large layers
- 📊 More accurate progress bar
- 💡 More informative log messages

### Version 1.0
- 🚀 Initial release
- Basic overlap detection
- Automatic geometric correction

## 👨‍💻 Author

**Raúl Viquez**
- GitHub: [@viquezr-dev](https://github.com/viquezr-dev)
- Email: viquezr@gmail.com

## 📄 License

This plugin is licensed under the **GNU General Public License v2.0**.  
See the [LICENSE](LICENSE) file for more details.

## 🙏 Acknowledgments

- QGIS community for their excellent documentation
- Contributors who report issues and suggest improvements

---

**Do you like the plugin?**  
⭐ Give it a star on GitHub!  
🐛 Found a bug? Open an [issue](https://github.com/viquezr-dev/fix_traslapes/issues)
