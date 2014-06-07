# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uifiles/ui_about.ui'
#
# Created: Fri Jun  6 21:56:18 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_about(object):
    def setupUi(self, about):
        about.setObjectName(_fromUtf8("about"))
        about.resize(422, 578)
        about.setMinimumSize(QtCore.QSize(422, 578))
        about.setMaximumSize(QtCore.QSize(422, 578))
        self.buttonBox = QtGui.QDialogButtonBox(about)
        self.buttonBox.setGeometry(QtCore.QRect(120, 530, 166, 33))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.help_browser = QtGui.QTextBrowser(about)
        self.help_browser.setGeometry(QtCore.QRect(10, 20, 401, 501))
        self.help_browser.setHtml(_fromUtf8("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.help_browser.setAcceptRichText(False)
        self.help_browser.setOpenExternalLinks(True)
        self.help_browser.setObjectName(_fromUtf8("help_browser"))

        self.retranslateUi(about)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), about.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), about.reject)
        QtCore.QMetaObject.connectSlotsByName(about)

    def retranslateUi(self, about):
        about.setWindowTitle(_translate("about", "clusterpy_light", None))

