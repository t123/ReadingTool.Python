# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\gitrepository\ReadingTool.Python\qtdesigner\items.ui'
#
# Created: Wed May  7 13:26:01 2014
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

class Ui_Items(object):
    def setupUi(self, Items):
        Items.setObjectName(_fromUtf8("Items"))
        Items.resize(723, 470)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Items)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.splitter = QtGui.QSplitter(Items)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tvFilter = QtGui.QTreeView(self.widget)
        self.tvFilter.setObjectName(_fromUtf8("tvFilter"))
        self.verticalLayout.addWidget(self.tvFilter)
        self.pbAdd = QtGui.QPushButton(self.widget)
        self.pbAdd.setObjectName(_fromUtf8("pbAdd"))
        self.verticalLayout.addWidget(self.pbAdd)
        self.widget1 = QtGui.QWidget(self.splitter)
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.leFilter = QtGui.QLineEdit(self.widget1)
        self.leFilter.setObjectName(_fromUtf8("leFilter"))
        self.verticalLayout_2.addWidget(self.leFilter)
        self.tItems = QtGui.QTableWidget(self.widget1)
        self.tItems.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tItems.setAlternatingRowColors(True)
        self.tItems.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tItems.setShowGrid(True)
        self.tItems.setObjectName(_fromUtf8("tItems"))
        self.tItems.setColumnCount(0)
        self.tItems.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tItems)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pbEdit = QtGui.QPushButton(self.widget1)
        self.pbEdit.setObjectName(_fromUtf8("pbEdit"))
        self.horizontalLayout.addWidget(self.pbEdit)
        self.pbCopy = QtGui.QPushButton(self.widget1)
        self.pbCopy.setObjectName(_fromUtf8("pbCopy"))
        self.horizontalLayout.addWidget(self.pbCopy)
        self.pbDelete = QtGui.QPushButton(self.widget1)
        self.pbDelete.setObjectName(_fromUtf8("pbDelete"))
        self.horizontalLayout.addWidget(self.pbDelete)
        self.pbRead = QtGui.QPushButton(self.widget1)
        self.pbRead.setObjectName(_fromUtf8("pbRead"))
        self.horizontalLayout.addWidget(self.pbRead)
        self.pbReadParallel = QtGui.QPushButton(self.widget1)
        self.pbReadParallel.setObjectName(_fromUtf8("pbReadParallel"))
        self.horizontalLayout.addWidget(self.pbReadParallel)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addWidget(self.splitter)

        self.retranslateUi(Items)
        QtCore.QMetaObject.connectSlotsByName(Items)

    def retranslateUi(self, Items):
        Items.setWindowTitle(_translate("Items", "Form", None))
        self.pbAdd.setText(_translate("Items", "Add", None))
        self.tItems.setSortingEnabled(True)
        self.pbEdit.setText(_translate("Items", "Edit", None))
        self.pbCopy.setText(_translate("Items", "Copy", None))
        self.pbDelete.setText(_translate("Items", "Delete", None))
        self.pbRead.setText(_translate("Items", "Read", None))
        self.pbReadParallel.setText(_translate("Items", "Parallel", None))

