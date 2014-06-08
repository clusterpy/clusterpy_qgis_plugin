# -*- coding: utf-8 -*-
"""
/***************************************************************************
 clusterpy_light
                                 A QGIS plugin
 Clusterpy plugin version for QGIS
                              -------------------
        begin                : 2014-01-24
        copyright            : (C) 2014 by RISE Group Universidad EAFIT
        email                : software@rise-group.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import resources_rc
from clusterpy_lightdialog import maxpDialog, aboutDialog
import os.path

class clusterpy_light:
    CLSP_MENU = u"&Clusterpy - Spatially constrained clustering"

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir,
                                    'i18n',
                                    'clusterpy_light_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.mc = self.iface.mapCanvas()
        self.maxpdlg = maxpDialog()
        self.maxpdlg.mc = self.mc
        self.maxpdlg.iface = self.iface

        self.aboutdlg = aboutDialog()

    def initGui(self):
        default_icon = QIcon(":/uifiles/clusterpy.png")
        rise_icon = QIcon(":/uifiles/rise1.png")

        self.maxpaction = QAction(default_icon, u"Max-p Algorithm",
                                                    self.iface.mainWindow())
        self.maxpaction.triggered.connect(self.maxp)

        self.aboutaction = QAction(rise_icon, u"About RISE",
                                                    self.iface.mainWindow())
        self.aboutaction.triggered.connect(self.about)

        self.iface.addPluginToMenu(self.CLSP_MENU, self.maxpaction)
        self.iface.addPluginToMenu(self.CLSP_MENU, self.aboutaction)

    def unload(self):
        self.iface.removePluginMenu(self.CLSP_MENU, self.maxpaction)
        self.iface.removePluginMenu(self.CLSP_MENU, self.aboutaction)

    def about(self):
        self.aboutdlg.show()

    def maxp(self):
        self.maxpdlg.show()
        self.maxpdlg.layer_combo.clear()
        self.maxpdlg.layer_combo.addItems([x.name() for x in self.mc.layers()])
        self.maxpdlg.exec_()
