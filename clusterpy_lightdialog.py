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

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.threshold_attr_combo,
                        QtCore.SIGNAL("currentIndexChanged(int)"),
                        self.updateThresholdLimits)

        self.connect(self.attribute_combo,
                QtCore.SIGNAL("currentIndexChanged(int)"),
                self.checkAttrValues)

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

    def checkAttrValues(self, newindex):
        if newindex > -1:
            attributeName = self.attribute_combo.currentText()
            self.checkAllValues(attributeName)

    def checkAllValues(self, attributeName):
        layerIndex = self.layer_combo.currentIndex()
        fiterator = self.mc.layer(layerIndex).dataProvider().getFeatures()

        valid = True
        maximum = 0
        minimum = 99999
        for feature in fiterator:
            val = feature.attribute(attributeName)
            try:
                minimum = val if val < minimum else minimum
                maximum += val
            except TypeError:
                valid = False

        if not valid:
            null_message  = "Some values are missing.\n" +\
            "Check the Attribute Table for NULL or empty values.\n" +\
            "Column: " + str(attributeName) + "\n" +\
            "Please update the Attribute Table in order to run Max-p."

            # Showing a message box might be better to get the user's attention
            QtGui.QMessageBox.warning(self, "Clusterpy", null_message)
            #self.showMessage("Clusterpy Error", "NULL or Empty Attrs",
            #    level=QgsMessageBar.CRITICAL)

        return minimum, maximum

    def updateThresholdLimits(self, newindex):
        if newindex > -1:
            layerIndex = self.layer_combo.currentIndex()
            fiterator = self.mc.layer(layerIndex).dataProvider().getFeatures()
            attributeName = self.threshold_attr_combo.currentText()

            minimum, maximum = self.checkAllValues(attributeName)

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
        if self.layer_path.text() == "":
            QtGui.QMessageBox.warning(self,
                                "Clusterpy",
                                "Please specify output shapefile")
        else:
            self.okbutton = self.buttonBox.button( QtGui.QDialogButtonBox.Ok )
            self.okbutton.setEnabled(False)
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
        self.okbutton.setEnabled(True)
        if success:
            self.addToCanvas()
            msg = "Success. New column added to attribute table. " + outputmsg
            self.showMessage("Clusterpy", msg, duration=0 )
        else:
            self.showMessage("Clusterpy Error",
                                        outputmsg,
                                        level=QgsMessageBar.CRITICAL)
        self.layer_path.clear()
        self.add_canvas.setChecked(Qt.Unchecked)
        self.updateProgress(0)

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def showMessage(self, msgtype, msgtext, level=QgsMessageBar.INFO,
                                            duration=30):
        messagebar = self.iface.messageBar()
        messagebar.pushMessage(msgtype, msgtext, level=level, duration=duration)
