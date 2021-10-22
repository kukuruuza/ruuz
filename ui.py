# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Robo\!!!\main.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(376, 440)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 261, 231))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.comboBox_port = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_port.setObjectName("comboBox_port")
        self.horizontalLayout_5.addWidget(self.comboBox_port)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.bt_openport = QtWidgets.QPushButton(self.groupBox)
        self.bt_openport.setObjectName("bt_openport")
        self.horizontalLayout_7.addWidget(self.bt_openport)
        self.bt_closeport = QtWidgets.QPushButton(self.groupBox)
        self.bt_closeport.setObjectName("bt_closeport")
        self.horizontalLayout_7.addWidget(self.bt_closeport)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        spacerItem = QtWidgets.QSpacerItem(20, 21, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.comboBox_baudrate = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_baudrate.setObjectName("comboBox_baudrate")
        self.horizontalLayout_6.addWidget(self.comboBox_baudrate)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_8.addWidget(self.label_5)
        self.comboBox_parity = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_parity.setObjectName("comboBox_parity")
        self.horizontalLayout_8.addWidget(self.comboBox_parity)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_9.addWidget(self.label_6)
        self.comboBox_flcntrl = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_flcntrl.setObjectName("comboBox_flcntrl")
        self.horizontalLayout_9.addWidget(self.comboBox_flcntrl)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.bt_apply = QtWidgets.QPushButton(self.groupBox)
        self.bt_apply.setObjectName("bt_apply")
        self.horizontalLayout_10.addWidget(self.bt_apply)
        self.bt_cancel = QtWidgets.QPushButton(self.groupBox)
        self.bt_cancel.setObjectName("bt_cancel")
        self.horizontalLayout_10.addWidget(self.bt_cancel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_10)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 376, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "PORT SETTINGS"))
        self.label_2.setText(_translate("MainWindow", "Port"))
        self.bt_openport.setStatusTip(_translate("MainWindow", "Open port"))
        self.bt_openport.setText(_translate("MainWindow", "OPEN"))
        self.bt_closeport.setStatusTip(_translate("MainWindow", "Close port"))
        self.bt_closeport.setText(_translate("MainWindow", "CLOSE"))
        self.label_3.setText(_translate("MainWindow", "Baudrate"))
        self.label_5.setText(_translate("MainWindow", "Parity"))
        self.label_6.setText(_translate("MainWindow", "Flowcontrol"))
        self.bt_apply.setStatusTip(_translate("MainWindow", "Apply port settings"))
        self.bt_apply.setText(_translate("MainWindow", "APPLY"))
        self.bt_cancel.setStatusTip(_translate("MainWindow", "Cancel new settings "))
        self.bt_cancel.setText(_translate("MainWindow", "CANCEL"))



