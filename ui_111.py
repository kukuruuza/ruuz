# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\PycharmProjects\robotanno\main.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        MainWindow.setMinimumSize(QtCore.QSize(640, 480))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.horizontalLayout.addWidget(self.listWidget)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_port = QtWidgets.QWidget()
        self.tab_port.setObjectName("tab_port")
        self.layoutWidget = QtWidgets.QWidget(self.tab_port)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 158, 196))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(self.layoutWidget)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 0, 0, 1, 1)
        self.cmbxPorts = QtWidgets.QComboBox(self.layoutWidget)
        self.cmbxPorts.setObjectName("cmbxPorts")
        self.gridLayout.addWidget(self.cmbxPorts, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.layoutWidget)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 1, 0, 1, 1)
        self.cmbxBaudRate = QtWidgets.QComboBox(self.layoutWidget)
        self.cmbxBaudRate.setObjectName("cmbxBaudRate")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.cmbxBaudRate.addItem("")
        self.gridLayout.addWidget(self.cmbxBaudRate, 1, 1, 1, 1)
        self.btnOpenClose = QtWidgets.QPushButton(self.layoutWidget)
        self.btnOpenClose.setEnabled(False)
        self.btnOpenClose.setCheckable(False)
        self.btnOpenClose.setChecked(False)
        self.btnOpenClose.setObjectName("btnOpenClose")
        self.gridLayout.addWidget(self.btnOpenClose, 2, 0, 1, 1)
        self.btnSave = QtWidgets.QPushButton(self.layoutWidget)
        self.btnSave.setEnabled(False)
        self.btnSave.setObjectName("btnSave")
        self.gridLayout.addWidget(self.btnSave, 2, 1, 1, 1)
        self.btnSetZero = QtWidgets.QPushButton(self.tab_port)
        self.btnSetZero.setEnabled(True)
        self.btnSetZero.setGeometry(QtCore.QRect(10, 240, 75, 23))
        self.btnSetZero.setObjectName("btnSetZero")
        self.tabWidget.addTab(self.tab_port, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "555"))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.label_8.setText(_translate("MainWindow", "Port"))
        self.label_10.setText(_translate("MainWindow", "BaudRate"))
        self.cmbxBaudRate.setCurrentText(_translate("MainWindow", "300"))
        self.cmbxBaudRate.setItemText(0, _translate("MainWindow", "300"))
        self.cmbxBaudRate.setItemText(1, _translate("MainWindow", "600"))
        self.cmbxBaudRate.setItemText(2, _translate("MainWindow", "1200"))
        self.cmbxBaudRate.setItemText(3, _translate("MainWindow", "2400"))
        self.cmbxBaudRate.setItemText(4, _translate("MainWindow", "4800"))
        self.cmbxBaudRate.setItemText(5, _translate("MainWindow", "9600"))
        self.cmbxBaudRate.setItemText(6, _translate("MainWindow", "19200"))
        self.cmbxBaudRate.setItemText(7, _translate("MainWindow", "38400"))
        self.cmbxBaudRate.setItemText(8, _translate("MainWindow", "56800"))
        self.cmbxBaudRate.setItemText(9, _translate("MainWindow", "115200"))
        self.btnOpenClose.setText(_translate("MainWindow", "OPEN"))
        self.btnSave.setText(_translate("MainWindow", "SAVE"))
        self.btnSetZero.setText(_translate("MainWindow", "Set 0"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_port), _translate("MainWindow", "Port"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
