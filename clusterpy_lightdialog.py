# -*- coding: utf-8 -*-
"""
/***************************************************************************
 clusterpy_lightDialog
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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from qgis.gui import QgsMessageBar
from uifiles.ui_maxp import Ui_maxp_ui
from uifiles.ui_about import Ui_about
from plugin_utils import saveDialog
from os import path
from plugin_utils import addShapeToCanvas
import workers

class aboutDialog(QtGui.QDialog, Ui_about):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        aboutfile = path.dirname(__file__) + '/uifiles/about.html'
        abouthtml = open(aboutfile).read()
        self.help_browser.setHtml(abouthtml)

class maxpDialog(QtGui.QDialog, Ui_maxp_ui):
    ERROR_MSG = u"There are features from the shapefile that are disconnected. \
                Check the following areas for errors in the geometry: "
    DONE_MSG = "Finish"

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.threshold_attr_combo,
                        QtCore.SIGNAL("currentIndexChanged(int)"),
                        self.updateThresholdLimits)

        self.connect(self.layer_combo,
                        QtCore.SIGNAL("currentIndexChanged(int)"),
                        self.updateAttrCombo)

        self.connect(self.browse_button,
                        QtCore.SIGNAL("clicked()"),
                        self.openOutputDialog)

        maxpfile = path.dirname(__file__) + '/uifiles/maxphelp.html'
        maxphtml = open(maxpfile).read()
        self.help_browser.setHtml(maxphtml)

    def updateAttrCombo(self, newindex):
        if newindex > -1:
            self.attribute_combo.clear()
            self.threshold_attr_combo.clear()

            fieldList = self.mc.layer(newindex).dataProvider().fields()

            fieldNames = []
            fieldNames2= []
            for item in list(fieldList):
                if item.typeName() != "String":
                    fieldNames.append(item.name())
                    fieldNames2.append(item.name())

            self.attribute_combo.addItems(fieldNames)
            self.threshold_attr_combo.addItems(fieldNames2)

    def updateThresholdLimits(self, newindex):
        if newindex > -1:
            layerIndex = self.layer_combo.currentIndex()
            fiterator = self.mc.layer(layerIndex).dataProvider().getFeatures()
            attributeName = self.threshold_attr_combo.currentText()

            maximum = 0
            minimum = 99999
            for feature in fiterator:
                val = feature.attribute(attributeName)
                minimum = val if val < minimum else minimum
                maximum += val

            self.threshold_spin.setMinimum(minimum)
            self.threshold_spin.setMaximum(maximum)
            self.threshold_spin.setValue((maximum - minimum)/3.0)

    def openOutputDialog(self):
        self.layer_path.clear()
        fileName, encoding = saveDialog(self)
        if fileName is None or encoding is None:
            return
        self.layer_path.setText(fileName)

    def addToCanvas(self):
        if self.add_canvas.checkState() == Qt.Checked:
            addShapeToCanvas(self.layer_path.text())

    def accept(self):
        layerindex = self.layer_combo.currentIndex()
        if layerindex < 0:
            return
        layer = self.mc.layer(layerindex)
        info = {
            'attrname' : self.attribute_combo.currentText(),
            'thresholdattr' : self.threshold_attr_combo.currentText(),
            'threshold' : self.threshold_spin.value(),
            'maxit' : self.maxit_spin.value(),
            'tabumax' : self.tabumax_spin.value(),
            'tabusize' : self.tabulength_spin.value(),
            'output_path' : self.layer_path.text(),
            'layer' : layer
        }
        worker = workers.MaxPWorker(info)
        thread = QtCore.QThread(self)
        worker.moveToThread(thread)
        worker.finished.connect(self.finishRun)
        worker.progress.connect(self.updateProgress)
        thread.started.connect(worker.run)
        self.thread = thread
        self.worker = worker
        thread.start()

    def finishRun(self, success, outputmsg):
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        if success:
            self.addToCanvas()
            self.showMessage("Clusterpy", "Success. File:" + outputmsg )
        else:
            self.showMessage("Clusterpy: Error",
                                        outputmsg,
                                        level=QgsMessageBar.CRITICAL)

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def showMessage(self, msgtype, msgtext, level=QgsMessageBar.INFO,
                                            duration=5):
        messagebar = self.iface.messageBar()
        messagebar.pushMessage(msgtype, msgtext, level=level, duration=duration)

