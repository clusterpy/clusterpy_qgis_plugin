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
from ui_maxp import Ui_maxp_ui
from ui_minp import Ui_minp_ui

class minpDialog(QtGui.QDialog, Ui_minp_ui):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

class maxpDialog(QtGui.QDialog, Ui_maxp_ui):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.threshold_attr_combo,
                        QtCore.SIGNAL("currentIndexChanged(int)"),
                        self.updateThresholdLimits)

        self.connect(self.layer_combo,
                        QtCore.SIGNAL("currentIndexChanged(int)"),
                        self.updateAttrCombo)

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
            self.threshold_spin.setValue((maximum - minimum)/2.0)

