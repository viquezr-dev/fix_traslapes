# -*- coding: utf-8 -*-
"""
Fix Traslapes - Plugin para QGIS
Desarrollado por Raul Viquez
Version: 2.4 - Estable
"""

import os
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal, QVariant
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import (QAction, QDialog, QVBoxLayout, QHBoxLayout,
                                 QLabel, QComboBox, QPushButton, QProgressBar,
                                 QTextEdit, QGroupBox, QMessageBox, QDoubleSpinBox,
                                 QCheckBox)
from qgis.utils import iface
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
                      QgsWkbTypes, QgsField, QgsSymbol, QgsSingleSymbolRenderer)


class ProcesadorTraslapes(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str, str)
    finished = pyqtSignal(dict)
    
    def __init__(self, layer, umbral, crear_capas_traslape=True):
        super().__init__()
        self.layer = layer
        self.umbral = umbral
        self.crear_capas_traslape = crear_capas_traslape
        self.is_running = True
        
    def stop(self):
        self.is_running = False
        
    def crear_capa_centroides(self, traslapes, nombre):
        crs = self.layer.crs().authid()
        capa = QgsVectorLayer(f"Point?crs={crs}", nombre, "memory")
        provider = capa.dataProvider()
        provider.addAttributes([
            QgsField("poligono_A", QVariant.Int),
            QgsField("poligono_B", QVariant.Int),
            QgsField("area", QVariant.Double)
        ])
        capa.updateFields()
        for t in traslapes:
            feat = QgsFeature()
            centroide = t['geom'].centroid()
            if centroide and not centroide.isEmpty():
                feat.setGeometry(centroide)
                feat.setAttributes([t['id_i'], t['id_j'], t['area']])
                provider.addFeature(feat)
        symbol = QgsSymbol.defaultSymbol(capa.geometryType())
        symbol.setColor(QColor(255, 0, 0))
        symbol.setSize(3)
        capa.setRenderer(QgsSingleSymbolRenderer(symbol))
        return capa
    
    def crear_capa_poligonos(self, traslapes, nombre):
        crs = self.layer.crs().authid()
        capa = QgsVectorLayer(f"Polygon?crs={crs}", nombre, "memory")
        provider = capa.dataProvider()
        provider.addAttributes([
            QgsField("poligono_A", QVariant.Int),
            QgsField("poligono_B", QVariant.Int),
            QgsField("area", QVariant.Double)
        ])
        capa.updateFields()
        for t in traslapes:
            feat = QgsFeature()
            feat.setGeometry(t['geom'])
            feat.setAttributes([t['id_i'], t['id_j'], t['area']])
            provider.addFeature(feat)
        symbol = QgsSymbol.defaultSymbol(capa.geometryType())
        symbol.setColor(QColor(255, 0, 0, 100))
        if symbol.symbolLayerCount() > 0:
            symbol.symbolLayer(0).setStrokeColor(QColor(255, 0, 0))
            symbol.symbolLayer(0).setStrokeWidth(0.5)
        capa.setRenderer(QgsSingleSymbolRenderer(symbol))
        return capa
        
    def run(self):
        try:
            features = list(self.layer.getFeatures())
            num = len(features)
            
            self.log.emit(f"📊 Analizando {num} polígonos...", "info")
            
            # Detectar traslapes
            traslapes = []
            for i in range(num):
                if not self.is_running:
                    return
                geom_i = features[i].geometry()
                if not geom_i:
                    continue
                for j in range(i + 1, num):
                    geom_j = features[j].geometry()
                    if not geom_j:
                        continue
                    if geom_i.intersects(geom_j):
                        inter = geom_i.intersection(geom_j)
                        area = inter.area()
                        if area > self.umbral:
                            traslapes.append({
                                'i': i, 'j': j, 'area': area,
                                'id_i': features[i].id(), 'id_j': features[j].id(),
                                'geom': inter
                            })
                self.progress.emit(int((i + 1) / num * 30))
            
            if not traslapes:
                self.progress.emit(100)
                self.log.emit("✅ Capa limpia - Sin traslapes", "success")
                self.finished.emit({'success': True, 'corregidos': 0, 'iniciales': 0})
                return
            
            self.log.emit(f"⚠ {len(traslapes)} traslapes encontrados", "warning")
            
            # Capas de visualización
            if self.crear_capas_traslape:
                capa_pol = self.crear_capa_poligonos(traslapes, f"{self.layer.name()}_TRASLAPES")
                QgsProject.instance().addMapLayer(capa_pol)
                capa_cen = self.crear_capa_centroides(traslapes, f"{self.layer.name()}_CENTROIDES")
                QgsProject.instance().addMapLayer(capa_cen)
                self.log.emit("🗺️ Capas de traslapes creadas", "info")
            
            # Corregir
            geoms = []
            for feat in features:
                if feat.geometry():
                    geoms.append(QgsGeometry(feat.geometry()))
                else:
                    geoms.append(None)
                    
            total_corregidos = 0
            iteracion = 0
            
            while True:
                iteracion += 1
                actuales = []
                for i in range(num):
                    if not geoms[i] or geoms[i].isEmpty():
                        continue
                    for j in range(i + 1, num):
                        if not geoms[j] or geoms[j].isEmpty():
                            continue
                        if geoms[i].intersects(geoms[j]):
                            inter = geoms[i].intersection(geoms[j])
                            if inter.area() > self.umbral:
                                actuales.append((i, j, inter))
                
                if not actuales:
                    break
                
                corregidos = 0
                for i, j, inter in actuales:
                    if geoms[i].area() <= geoms[j].area():
                        nueva = geoms[i].difference(inter)
                        if nueva and not nueva.isEmpty():
                            geoms[i] = nueva
                            corregidos += 1
                    else:
                        nueva = geoms[j].difference(inter)
                        if nueva and not nueva.isEmpty():
                            geoms[j] = nueva
                            corregidos += 1
                    total_corregidos += corregidos
                
                self.progress.emit(30 + min(iteracion * 15, 60))
                if corregidos == 0:
                    break
            
            # Capa corregida (editable)
            crs = self.layer.crs().authid()
            nueva_capa = QgsVectorLayer(f"Polygon?crs={crs}", f"{self.layer.name()}_CORREGIDO", "memory")
            provider = nueva_capa.dataProvider()
            provider.addAttributes(self.layer.fields())
            nueva_capa.updateFields()
            
            nuevas_feats = []
            for i, geom in enumerate(geoms):
                if geom and not geom.isEmpty():
                    feat = QgsFeature()
                    feat.setGeometry(geom)
                    feat.setAttributes(features[i].attributes())
                    nuevas_feats.append(feat)
            provider.addFeatures(nuevas_feats)
            
            # Selección automática habilitada
            nueva_capa.commitChanges()
            
            # Agregar al proyecto y activar
            QgsProject.instance().addMapLayer(nueva_capa)
            
            # Iniciar modo edición
            # Selección automática habilitada
            iface.setActiveLayer(nueva_capa)
            
            # Configurar para selección
            nueva_capa.setReadOnly(False)
            self.log.emit(f"💡 Capa '{nueva_capa.name()}' lista para editar", "info")
            # La capa activa se selecciona automáticamente al agregarla

            self.progress.emit(100)
            self.log.emit(f"✅ Corregidos: {total_corregidos} | Capa: {nueva_capa.name()}", "success")
            
            self.finished.emit({
                'success': True, 'corregidos': total_corregidos,
                'iniciales': len(traslapes), 'nombre_capa': nueva_capa.name()
            })
            
        except Exception as e:
            self.log.emit(f"❌ Error: {str(e)}", "error")
            self.finished.emit({'error': str(e)})


class FixTraslapesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.procesador = None
        self.setup_ui()
        # Retrasar la carga de capas para evitar errores de acceso
        from qgis.PyQt.QtCore import QTimer
        QTimer.singleShot(100, self.cargar_capas)
        # Conectar señal para actualizar capas cuando cambia el proyecto
        
        QgsProject.instance().layersAdded.connect(self.actualizar_capas)
        QgsProject.instance().layersRemoved.connect(self.actualizar_capas)
        
    def setup_ui(self):
        self.setWindowTitle("Fix Traslapes")
        self.setFixedSize(450, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Estilo compacto profesional
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QGroupBox { font-weight: bold; border: 1px solid #d0d0d0; border-radius: 6px; margin-top: 8px; padding-top: 8px; background-color: white; }
            QGroupBox::title { color: #2c3e50; left: 10px; }
            QLabel { color: #2c3e50; }
            QComboBox, QDoubleSpinBox { background: white; border: 1px solid #d0d0d0; border-radius: 3px; padding: 4px; min-height: 18px; }
            QComboBox:hover, QDoubleSpinBox:hover { border-color: #3498db; }
            QCheckBox { color: #2c3e50; }
            QPushButton { background: #3498db; border: none; border-radius: 3px; padding: 6px 12px; color: white; font-weight: bold; min-width: 90px; }
            QPushButton:hover { background: #2980b9; }
            QPushButton#btnCerrar { background: #95a5a6; }
            QPushButton#btnCerrar:hover { background: #7f8c8d; }
            QProgressBar { border: 1px solid #d0d0d0; border-radius: 3px; text-align: center; background: white; height: 18px; }
            QProgressBar::chunk { background: #3498db; border-radius: 2px; }
            QTextEdit { background: #fafafa; border: 1px solid #d0d0d0; border-radius: 3px; font-family: monospace; font-size: 9pt; }
            QLabel#firma { color: #7f8c8d; font-size: 8pt; }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Título
        titulo = QLabel("🛠️ SISTEMA CORRECTOR DE TRASLAPES")
        titulo.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2c3e50; padding: 5px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Grupo capa
        g_capa = QGroupBox("📁 Capa")
        l_capa = QVBoxLayout()
        self.capa_combo = QComboBox()
        self.capa_combo.setEditable(False)
        self.capa_combo.setMaxVisibleItems(8)
        self.capa_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                padding: 5px;
                font-size: 11px;
                background-color: transparent;
                min-height: 20px;
                selection-background-color: #e2e8f0;
                selection-color: black;
            }
            QComboBox:hover {
                border: 1px solid #3b82f6;
                background-color: rgba(59, 130, 246, 0.1);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #64748b;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #cbd5e0;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #e2e8f0;
                selection-color: black;
                outline: none;
            }
            QComboBox::item:selected {
                color: black;
                background-color: #e2e8f0;
            }
        """)
        l_capa.addWidget(self.capa_combo)
        self.lbl_validacion = QLabel("")
        self.lbl_validacion.setStyleSheet("color: #e67e22; font-size: 8pt;")
        l_capa.addWidget(self.lbl_validacion)
        g_capa.setLayout(l_capa)
        layout.addWidget(g_capa)
        
        # Grupo configuración
        g_config = QGroupBox("⚙️ Configuración")
        l_config = QHBoxLayout()
        l_config.addWidget(QLabel("Umbral:"))
        self.umbral_spin = QDoubleSpinBox()
        self.umbral_spin.setDecimals(6)
        self.umbral_spin.setMinimum(0.000001)
        self.umbral_spin.setMaximum(1000000)
        self.umbral_spin.setSingleStep(0.0001)
        self.umbral_spin.setValue(0.0001)
        self.umbral_spin.setToolTip("Áreas menores se ignoran")
        l_config.addWidget(self.umbral_spin)
        l_config.addStretch()
        g_config.setLayout(l_config)
        layout.addWidget(g_config)
        
        # Opción capas visualización
        self.chk_crear_capas = QCheckBox("🗺️ Crear capas de traslapes")
        self.chk_crear_capas.setChecked(True)
        layout.addWidget(self.chk_crear_capas)
        
        # Progreso
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Log
        g_log = QGroupBox("📋 Resultados")
        l_log = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        l_log.addWidget(self.log_text)
        g_log.setLayout(l_log)
        layout.addWidget(g_log)
        
        # Firma
        firma = QLabel("Desarrollado por: Raul Viquez")
        firma.setObjectName("firma")
        firma.setAlignment(Qt.AlignCenter)
        layout.addWidget(firma)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_iniciar = QPushButton("▶ Iniciar")
        self.btn_iniciar.clicked.connect(self.iniciar)
        btn_layout.addWidget(self.btn_iniciar)
        self.btn_cerrar = QPushButton("✖ Cerrar")
        self.btn_cerrar.setObjectName("btnCerrar")
        self.btn_cerrar.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cerrar)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.agregar_log("🎯 Selecciona una capa de polígonos", "info")
        
    def cargar_capas(self):
        """Cargar capas de polígonos - Con protección contra errores"""
        try:
            self.capa_combo.blockSignals(True)
            # Guardar la capa actualmente seleccionada
            current_layer = self.capa_combo.currentData() if self.capa_combo.count() > 0 else None
            self.capa_combo.clear()
            self.capa_combo.addItem("-- Seleccionar --", None)
            
            for layer in QgsProject.instance().mapLayers().values():
                if isinstance(layer, QgsVectorLayer):
                    if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                        self.capa_combo.addItem(layer.name(), layer)
            
            # Restaurar selección si la capa aún existe
            if current_layer:
                for i in range(self.capa_combo.count()):
                    if self.capa_combo.itemData(i) == current_layer:
                        self.capa_combo.setCurrentIndex(i)
                        break
            else:
                # Si no hay capa seleccionada, seleccionar la primera si existe
                if self.capa_combo.count() > 1:
                    self.capa_combo.setCurrentIndex(1)
            
            self.capa_combo.blockSignals(False)
            
            if self.capa_combo.count() <= 1:
                self.lbl_validacion.setText("⚠ No hay capas de polígonos")
                self.btn_iniciar.setEnabled(False)
            else:
                self.btn_iniciar.setEnabled(True)
                self.validar_capa()
        except Exception as e:
            self.agregar_log(f"Error cargando capas: {str(e)}", "error")
    
    def actualizar_capas(self):
        """Actualizar la lista de capas cuando se agregan o eliminan capas"""
        self.cargar_capas()
    
    def validar_capa(self):
        """Validar la capa seleccionada - Con protección"""
        try:
            idx = self.capa_combo.currentIndex()
            if idx < 0:
                return
            capa = self.capa_combo.itemData(idx)
            
            if capa is None:
                self.lbl_validacion.setText("⚠ Selecciona una capa")
                self.btn_iniciar.setEnabled(False)
            elif not isinstance(capa, QgsVectorLayer):
                self.lbl_validacion.setText("❌ Capa inválida")
                self.btn_iniciar.setEnabled(False)
            elif capa.geometryType() != QgsWkbTypes.PolygonGeometry:
                self.lbl_validacion.setText("❌ Debe ser capa de POLÍGONOS")
                self.btn_iniciar.setEnabled(False)
            else:
                self.lbl_validacion.setText(f"✅ {capa.featureCount()} polígonos")
                self.btn_iniciar.setEnabled(True)
        except Exception as e:
            self.lbl_validacion.setText(f"Error: {str(e)[:30]}")
            self.btn_iniciar.setEnabled(False)
    
    def agregar_log(self, msg, tipo="info"):
        colores = {"info": "#2c3e50", "success": "#27ae60", "warning": "#e67e22", "error": "#e74c3c"}
        prefix = {"success": "✅ ", "warning": "⚠️ ", "error": "❌ "}.get(tipo, "")
        self.log_text.append(f'<span style="color:{colores.get(tipo, "#2c3e50")};">{prefix}{msg}</span>')
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def iniciar(self):
        try:
            idx = self.capa_combo.currentIndex()
            if idx < 0:
                QMessageBox.warning(self, "Error", "Selecciona una capa")
                return
            capa = self.capa_combo.itemData(idx)
            
            if not capa:
                QMessageBox.warning(self, "Error", "Selecciona una capa")
                return
            if capa.geometryType() != QgsWkbTypes.PolygonGeometry:
                QMessageBox.warning(self, "Error", "La capa debe ser de polígonos")
                return
            
            self.log_text.clear()
            self.progress.setValue(0)
            self.btn_iniciar.setEnabled(False)
            
            self.agregar_log("🚀 Iniciando corrección...", "success")
            
            self.procesador = ProcesadorTraslapes(capa, self.umbral_spin.value(), self.chk_crear_capas.isChecked())
            self.procesador.progress.connect(self.progress.setValue)
            self.procesador.log.connect(self.agregar_log)
            self.procesador.finished.connect(self.finalizar)
            self.procesador.start()
        except Exception as e:
            self.agregar_log(f"Error: {str(e)}", "error")
            self.btn_iniciar.setEnabled(True)
    
    def finalizar(self, resultado):
        self.btn_iniciar.setEnabled(True)
        self.procesador = None
        if 'error' in resultado:
            self.agregar_log(f"Error: {resultado['error']}", "error")
        elif resultado.get('corregidos', 0) == 0 and resultado.get('iniciales', 0) == 0:
            self.agregar_log("✅ Capa limpia - Sin traslapes", "success")
        else:
            self.agregar_log(f"✅ Proceso finalizado", "success")
            self.agregar_log("💡 Recuerda guardar la capa corregida para poder editarla", "error")
        # No mantener referencia al procesador
    
    def closeEvent(self, event):
        if self.procesador and self.procesador.isRunning():
            self.procesador.stop()
            self.procesador.quit()
            self.procesador.wait(1000)
        event.accept()


class FixTraslapesPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dialog = None
        
    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.action = QAction(icon, "Fix Traslapes", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Complementos", self.action)
        
    def unload(self):
        """Eliminar el plugin de la interfaz"""
        self.iface.removePluginMenu("&Complementos", self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dialog:
            try:
                self.dialog.close()
                self.dialog.deleteLater()
            except:
                pass
            self.dialog = None
    
    def run(self):
        """Ejecutar el plugin - Crea un diálogo nuevo cada vez"""
        # Cerrar diálogo anterior si existe
        if self.dialog is not None:
            try:
                self.dialog.close()
                self.dialog.deleteLater()
            except:
                pass
        # Crear nuevo diálogo
        self.dialog = FixTraslapesDialog()
        self.dialog.show()
        self.dialog.raise_()
