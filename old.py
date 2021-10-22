from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from ui import Ui_MainWindow

if __name__ == "__main__":
    # create application
    app = QtWidgets.QApplication(sys.argv)

    # create form and ini UI
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    # hook logic

    # run main loop
    sys.exit(app.exec_())