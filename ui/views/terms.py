# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\gitrepository\ReadingTool.Python\qtdesigner\terms.ui'
#
# Created: Wed May  7 13:26:03 2014
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

class Ui_Terms(object):
    def setupUi(self, Terms):
        Terms.setObjectName(_fromUtf8("Terms"))
        Terms.resize(726, 528)
        self.verticalLayout = QtGui.QVBoxLayout(Terms)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.leFilter = QtGui.QLineEdit(Terms)
        self.leFilter.setObjectName(_fromUtf8("leFilter"))
        self.horizontalLayout.addWidget(self.leFilter)
        self.cbCollections = QtGui.QComboBox(Terms)
        self.cbCollections.setObjectName(_fromUtf8("cbCollections"))
        self.horizontalLayout.addWidget(self.cbCollections)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tTerms = QtGui.QTableWidget(Terms)
        self.tTerms.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tTerms.setAlternatingRowColors(True)
        self.tTerms.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tTerms.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tTerms.setObjectName(_fromUtf8("tTerms"))
        self.tTerms.setColumnCount(0)
        self.tTerms.setRowCount(0)
        self.verticalLayout.addWidget(self.tTerms)

        self.retranslateUi(Terms)
        QtCore.QMetaObject.connectSlotsByName(Terms)

    def retranslateUi(self, Terms):
        Terms.setWindowTitle(_translate("Terms", "Form", None))
        self.tTerms.setSortingEnabled(True)

