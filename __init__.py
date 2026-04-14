# -*- coding: utf-8 -*-
"""
Fix Traslapes - Plugin para QGIS
"""

def classFactory(iface):
    """Carga el plugin"""
    from .fix_traslapes_main import FixTraslapesPlugin
    return FixTraslapesPlugin(iface)
