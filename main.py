import sys
import sqlite3
from PyQt5 import uic, QtCore
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow
from datetime import datetime

# TODO: проверка ком-порта


class robot_form(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # подключение к БД
        self.serial_port = QSerialPort(readyRead=self.receive)
        self.con = sqlite3.connect('main_db.db')
        self.cur = self.con.cursor()
        self.cur.execute("SELECT * FROM port_settings")
        self.ps_settings_result = self.cur.fetchone()

        form, base = uic.loadUiType('main.ui')
        self.form = form()
        self.form.setupUi(self)

        self.status_port = False

        # заполнение списка доступных ком-портов
        self.serial = QSerialPortInfo.availablePorts()
        if len(self.serial) > 0:
            self.form.btnOpenClose.setEnabled(True)
        for port in self.serial:
            self.port_name = port.portName()
            self.form.cmbxPorts.addItem(self.port_name)
            if self.ps_settings_result is not None and self.port_name == self.ps_settings_result[1]:
                print(self.ps_settings_result[1])
                self.form.cmbxPorts.setCurrentText(self.ps_settings_result[1])

        if self.ps_settings_result is not None:
            self.form.cmbxBaudRate.setCurrentText(self.ps_settings_result[2])
            self.form.checkBoxReconnect.setCheckState(self.ps_settings_result[3])
            if self.form.checkBoxReconnect.isChecked():
                self.open_close_port()

        # кнопка Открыть/Закрыть порт
        self.form.btnOpenClose.clicked.connect(self.open_close_port)
        # кнопка Сохранить
        self.form.btnSave.clicked.connect(self.save_port)
        # кнопка Set 0
        self.form.btnSetZero.clicked.connect(self.set_0)
        # кнопка Clear
        self.form.actionClear_2.triggered.connect(self.clear_list)
        # кнопка J1-
        self.form.btnJ1minus.pressed.connect(self.j1_minus_pressed)
        self.form.btnJ1minus.released.connect(self.j1_released)
        # кнопка J1+
        self.form.btnJ1plus.pressed.connect(self.j1_plus_pressed)
        self.form.btnJ1plus.released.connect(self.j1_released)

        # кнопка Stop 30H
        self.form.btn30H.clicked.connect(self.h30_mode)
        # кнопка Idle 10H
        self.form.btn10H.clicked.connect(self.h10_mode)
        # кнопка Teach 14H
        self.form.btn14H.clicked.connect(self.h14_mode)
        # кнопка Query 05H
        self.form.btn05H.clicked.connect(self.h05_mode)
        # кнопка Restart 18H
        self.form.btn18H.clicked.connect(self.h18_mode)
        # кнопка Zero 15H
        self.form.btn15H.clicked.connect(self.h15_mode)
        # кнопка File 11H
        self.form.btn11H.clicked.connect(self.h11_mode)
        # кнопка Reset 12H
        self.form.btn12H.clicked.connect(self.h12_mode)
        # кнопка Run 13H
        self.form.btn13H.clicked.connect(self.h13_mode)

    def clear_list(self):
        self.form.listWidget.clear()

    def _createActions(self):
        pass

    def _createToolBars(self):
        pass

    def _createContextMenu(self):
        pass

    # Buttons func
    def open_close_port(self):
        # кнопка Закрыть порт
        if self.status_port:
            try:
                self.serial_port.close()
                self.form.cmbxPorts.setEnabled(True)
                self.form.cmbxBaudRate.setEnabled(True)
                self.form.btnOpenClose.setText("OPEN")
                self.form.listWidget.addItem("success_close_port")
                print("success_close_port")
                self.status_port = False
            except Exception as e:
                self.form.listWidget.addItem("error_close_serial_port", e)
                print("error_close_serial_port", e)

        # кнопка Открыть порт
        else:
            try:
                # self.serial_port = QSerialPort()
                port = self.form.cmbxPorts.currentText()
                self.serial_port.setPortName(port)
                speed = int(self.form.cmbxBaudRate.currentText())
                self.serial_port.setBaudRate(speed)
                self.serial_port.setParity(QSerialPort.NoParity)
                self.serial_port.setStopBits(QSerialPort.OneStop)
                self.serial_port.setDataBits(QSerialPort.Data8)
                self.serial_port.setFlowControl(QSerialPort.NoFlowControl)
                self.serial_port.open(QSerialPort.ReadWrite)
                self.form.listWidget.addItem("success_open_port")
                print("success_open_port")
                self.status_port = True
                self.form.cmbxPorts.setEnabled(False)
                self.form.cmbxBaudRate.setEnabled(False)
                self.form.btnOpenClose.setText("CLOSE")
            except Exception as e:
                print("error_open_serial_port", e)

    # сохранение параметров подключения к порту
    def save_port(self):
        try:
            for_save = (self.form.cmbxPorts.currentText(), self.form.cmbxBaudRate.currentText(),
                        self.form.checkBoxReconnect.checkState())
            if self.ps_settings_result is None:
                query = "INSERT INTO port_settings (ps_port_name, ps_speed, ps_reconnect) VALUES (?,?,?)"
            else:
                query = "UPDATE port_settings SET ps_port_name = ?, ps_speed = ?, ps_reconnect = ?"
            self.cur.execute(query, for_save)
            self.con.commit()
            self.form.listWidget.addItem("success_save_port_db")
        except Exception as e:
            print("error_save_port_db", e)

    @QtCore.pyqtSlot()
    def receive(self):
        pack = ""
        try:
            while self.serial_port.canReadLine():
                pack = pack + self.serial_port.readLine().data().decode()
            self.form.listWidget.addItem("RX " + str(datetime.now()) + "\r\n" + pack)
        except Exception as e:
            print("error_receive_port", e)

    def set_0(self):
        # stop
        pack = bytes([48])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n0")
        # exit
        pack = bytes([16])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DLE>")
        # teach
        pack = bytes([20])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DC4>")
        # joint print
        pack = "G07 GCM=0\r\n"
        self.serial_port.write(pack.encode())
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n" + pack)

    def j1_minus_pressed(self):
        # self.teach_mode()
        pack = "J1-\r\n"
        self.serial_port.write(pack.encode())
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n" + pack)

    def j1_released(self):
        pack = "J10\r\n"
        self.serial_port.write(pack.encode())
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n" + pack)

    def j1_plus_pressed(self):
        # self.teach_mode()
        pack = "J1+\r\n"
        self.serial_port.write(pack.encode())
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n" + pack)

    def h30_mode(self):
        # stop 30H
        pack = bytes([48])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n0")


    def h10_mode(self):
        # exit (idle mode 10H)
        pack = bytes([16])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DLE>")

    def h14_mode(self):
        # teach (teach mode 14H)
        pack = bytes([20])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DC4>")

    def h05_mode(self):
        # query (query mode 05H)
        pack = bytes([5])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<ENQ>")

    def h18_mode(self):
        # restart (18H)
        pack = bytes([24])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<CAN>")

    def h15_mode(self):
        # zero (15H)
        pack = bytes([21])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<NAK>")

    def h11_mode(self):
        # file (file mode 11H)
        pack = bytes([17])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DC1>")

    def h12_mode(self):
        # reset (reset mode 12H)
        pack = bytes([18])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DC2>")

    def h13_mode(self):
        # run (run mode 13H)
        pack = bytes([19])
        self.serial_port.write(pack)
        self.form.listWidget.addItem("TX " + str(datetime.now()) + "\r\n<DC3>")

    def closeEvent(self, event):
        if self.status_port:
            self.open_close_port()
        QMainWindow.close(self)


def main():
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = robot_form()
        window.show()
        sys.exit(app.exec_())

main()
