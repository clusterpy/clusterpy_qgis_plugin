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
from qgis.gui import QgsMessageBar
import resources_rc
from clusterpy_lightdialog import maxpDialog, minpDialog, aboutDialog
import os.path

from clusterpy import ClusterpyFeature, execmaxp, validtopology
from plugin_utils import addShapeToCanvas
import workers

class clusterpy_light:
    CLSP_MENU = u"&Clusterpy - Spatially constrained clustering"
    ERROR_MSG = u"There are features from the shapefile that are disconnected. \
                Check the following areas for errors in the geometry: "
    DONE_MSG = "Finish"

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
        result = self.maxpdlg.exec_()
        layerindex = self.maxpdlg.layer_combo.currentIndex()
        if result == 1 and layerindex > -1:
            layerindex = self.maxpdlg.layer_combo.currentIndex()
            info = {
                'attrname' : self.maxpdlg.attribute_combo.currentText(),
                'thresholdattr' :
                               self.maxpdlg.threshold_attr_combo.currentText(),
                'threshold' : self.maxpdlg.threshold_spin.value(),
                'maxit' : self.maxpdlg.maxit_spin.value(),
                'tabumax' : self.maxpdlg.tabumax_spin.value(),
                'tabusize' : self.maxpdlg.tabulength_spin.value(),
                'output_path' : self.maxpdlg.layer_path.text(),
                'layer' : self.mc.layer(layerindex),
                'addoutput' : self.maxpdlg.addToCanvas()
            }
            worker = MaxPWorker(info)
            Broker.startWorker(worker)

    def showMessage(self, msgtype, msgtext, level=QgsMessageBar.INFO,
                                            duration=None):
        messagebar = self.iface.messageBar()
        messagebar.pushMessage(msgtype, msgtext, level=level, duration=duration)

    def addShape(self, shapefilepath):
        addShapeToCanvas(shapefilepath)

    #def minp(self):
    #    # show the dialog
    #    self.minpdlg.show()
    #    # Run the dialog event loop
    #    result = self.minpdlg.exec_()
    #    # See if OK was pressed
    #    if result == 1:
    #        pass
