# Fix Traslapes - Plugin para QGIS

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-589632?style=flat&logo=qgis)](https://qgis.org)
[![Version](https://img.shields.io/badge/version-2.4-blue.svg)](https://github.com/viquezr-dev/fix_traslapes)
[![License](https://img.shields.io/badge/license-GPLv2-green.svg)](https://www.gnu.org/licenses/gpl-2.0.html)
[![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)](https://www.python.org/)

**Fix Traslapes** es un plugin para QGIS que detecta y corrige automáticamente traslapes (superposiciones) en capas de polígonos, generando capas de resultados limpias y editables.

## ✨ Características principales

- 🔍 **Detección precisa** de traslapes entre polígonos
- ⚙️ **Umbral configurable** para ignorar traslapes muy pequeños
- 🔧 **Corrección automática** mediante recorte geométrico
- 🗺️ **Capas de visualización** (polígonos de traslape en rojo + centroides)
- 📊 **Capa resultante** editable y lista para continuar trabajando
- 💻 **Interfaz intuitiva** con barra de progreso y log detallado

## 📋 Requisitos

- **QGIS** versión 3.0 o superior
- **Python** 3.9+
- Capas de **polígonos** (no puntos ni líneas)

## 🚀 Instalación

### Desde el repositorio oficial de QGIS (próximamente)
1. Abrir QGIS → Complementos → Administrar e instalar complementos
2. Buscar "Fix Traslapes"
3. Hacer clic en "Instalar"

### Instalación manual desde GitHub
1. Descargar el repositorio como ZIP
https://github.com/viquezr-dev/fix_traslapes/archive/main.zip

2. Descomprimir en la carpeta de plugins de QGIS:
- **Windows**: `C:\Users\TU_USUARIO\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
- **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
- **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Renombrar la carpeta a `fix_traslapes`
4. Reiniciar QGIS
5. Activar el plugin en Complementos → Administrar complementos

## 🎯 Cómo usar

### Paso a paso
1. **Cargar** una capa de polígonos en QGIS
2. **Abrir el plugin**: Botón en la barra de herramientas o menú `Complementos → Fix Traslapes`
3. **Seleccionar** la capa en el desplegable
4. **Configurar el umbral** (opcional):
- Valor pequeño (0.0001): detecta casi todos los traslapes
- Valor más grande: ignora traslapes muy pequeños
5. **Opcional**: Marcar/desmarcar "Crear capas de traslapes" según necesidad
6. **Hacer clic en "Iniciar"**
7. **Revisar** resultados en el panel de log y en el mapa

### Visualización de resultados

| Capa generada | Descripción |
|---------------|-------------|
| `nombre_capa_TRASLAPES` | Polígonos rojos semitransparentes que muestran las áreas corregidas |
| `nombre_capa_CENTROIDES` | Puntos rojos en el centro de cada traslape para inspección rápida |
| `nombre_capa_CORREGIDO` | **Capa final** con geometrías limpias, editable y seleccionable |

> 💡 **Nota**: La capa corregida se agrega automáticamente al proyecto y queda lista para editar o guardar.

## ⚙️ Configuración avanzada

### Umbral de detección
- **0.0001** (por defecto): Detecta traslapes mínimos (recomendado para datos georreferenciados)
- **0.001 - 0.01**: Para ignorar micro-traslapes menores a 1m²/10m² según tu unidad
- Ajusta según la escala y precisión de tus datos

## 🛠️ Desarrollo

### Estructura del plugin
fix_traslapes/
├── init.py # Inicialización del plugin
├── fix_traslapes_main.py # Código principal
├── metadata.txt # Metadatos para QGIS
└── icon.png # Ícono del plugin (64x64)

### Tecnologías utilizadas
- **PyQt5** - Interfaz gráfica
- **QGIS Python API** - Manipulación de capas y geometrías
- **QThread** - Procesamiento en segundo plano

## 🐛 Reporte de errores

Si encuentras algún problema o tienes sugerencias:
1. Revisa los [issues existentes](https://github.com/viquezr-dev/fix_traslapes/issues)
2. Abre un nuevo issue describiendo:
   - Versión de QGIS
   - Tipo de capa (formato, CRS)
   - Pasos para reproducir el error
   - Capturas de pantalla (si aplica)

## 📝 Changelog

### Versión 2.4 (2026-04-15)
- ✨ Interfaz mejorada con estilos profesionales
- 🐛 Corrección de errores en detección de capas
- ⚡ Optimización del rendimiento en capas grandes
- 📊 Barra de progreso más precisa
- 💡 Mensajes de log más informativos

### Versión 1.0
- 🚀 Lanzamiento inicial
- Detección básica de traslapes
- Corrección geométrica automática

## 👨‍💻 Autor

**Raúl Viquez**
- GitHub: [@viquezr-dev](https://github.com/viquezr-dev)
- Email: viquezr@gmail.com

## 📄 Licencia

Este plugin está bajo la licencia **GNU General Public License v2.0**.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Comunidad de QGIS por su excelente documentación
- Contribuidores que reportan issues y sugieren mejoras

---

**¿Te gusta el plugin?**  
⭐ ¡Dale una estrella en GitHub!  
🐛 ¿Encontraste un bug? Abre un [issue](https://github.com/viquezr-dev/fix_traslapes/issues)