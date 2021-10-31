import sys
import sqlite3
from PyQt5 import uic, QtCore
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from datetime import datetime
from loguru import logger

# TODO: проверка ком-порта

logger.add("main.log", format="{time} {level} {message}", level="DEBUG")

@logger.catch
class robot_form(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.modes = (5, 16, 17, 18, 19, 20, 21, 24, 48)
        self.mode = ""

        # подключение к БД
        self.serial_port = QSerialPort(readyRead=self.receive)
        self.con = sqlite3.connect('main.db')
        self.cur = self.con.cursor()
        self.read_db()

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
            if self.settings_result is not None and self.port_name == self.settings_result[1]:
                print(self.settings_result[1])
                self.form.cmbxPorts.setCurrentText(self.settings_result[1])

        if self.settings_result is not None:
            self.form.cmbxBaudRate.setCurrentText(self.settings_result[2])
            self.form.checkBoxReconnect.setCheckState(self.settings_result[3])
            if self.form.checkBoxReconnect.isChecked():
                self.open_close_port()
            self.form.EditINI.setText(self.settings_result[4])
            self.form.EditCFG.setText(self.settings_result[5])


        # кнопка Открыть/Закрыть порт
        self.form.btnOpenClose.clicked.connect(lambda: self.open_close_port())
        # кнопка Сохранить
        self.form.btnSave.clicked.connect(lambda: self.save_port())
        # кнопка Set 0
        self.form.btnSetZero.clicked.connect(lambda: self.set_0())
        # кнопка Clear
        self.form.actionClear_2.triggered.connect(self.clear_list)
        # кнопка J1-
        self.form.btnJ1minus.pressed.connect(lambda: self.j_minus_pressed("1"))
        self.form.btnJ1minus.released.connect(lambda: self.j_released("1"))
        # кнопка J1+
        self.form.btnJ1plus.pressed.connect(lambda: self.j_plus_pressed("1"))
        self.form.btnJ1plus.released.connect(lambda: self.j_released("1"))
        # кнопка J2-
        self.form.btnJ2minus.pressed.connect(lambda: self.j_minus_pressed("2"))
        self.form.btnJ2minus.released.connect(lambda: self.j_released("2"))
        # кнопка J2+
        self.form.btnJ2plus.pressed.connect(lambda: self.j_plus_pressed("2"))
        self.form.btnJ2plus.released.connect(lambda: self.j_released("2"))
        # кнопка J3-
        self.form.btnJ3minus.pressed.connect(lambda: self.j_minus_pressed("3"))
        self.form.btnJ3minus.released.connect(lambda: self.j_released("3"))
        # кнопка J3+
        self.form.btnJ3plus.pressed.connect(lambda: self.j_plus_pressed("3"))
        self.form.btnJ3plus.released.connect(lambda: self.j_released("3"))
        # кнопка J4-
        self.form.btnJ4minus.pressed.connect(lambda: self.j_minus_pressed("4"))
        self.form.btnJ4minus.released.connect(lambda: self.j_released("4"))
        # кнопка J4+
        self.form.btnJ4plus.pressed.connect(lambda: self.j_plus_pressed("4"))
        self.form.btnJ4plus.released.connect(lambda: self.j_released("4"))
        # кнопка J5-
        self.form.btnJ5minus.pressed.connect(lambda: self.j_minus_pressed("5"))
        self.form.btnJ5minus.released.connect(lambda: self.j_released("5"))
        # кнопка J5+
        self.form.btnJ5plus.pressed.connect(lambda: self.j_plus_pressed("5"))
        self.form.btnJ5plus.released.connect(lambda: self.j_released("5"))
        # кнопка J6-
        self.form.btnJ6minus.pressed.connect(lambda: self.j_minus_pressed("6"))
        self.form.btnJ6minus.released.connect(lambda: self.j_released("6"))
        # кнопка J6+
        self.form.btnJ6plus.pressed.connect(lambda: self.j_plus_pressed("6"))
        self.form.btnJ6plus.released.connect(lambda: self.j_released("6"))

        # для работы с режимами
        # self.modes = (([5], "<ENQ>"), ([16], "<DLE>"), ([17], "<DC1>"), ([18], "<DC2>"), ([19], "<DC3>"),
        #              ([20], "<DC4>"), ([21], "<NAK>"), ([24], "<CAN>"), ([48], "0"))

        # кнопка Stop 30H
        self.form.btn30H.clicked.connect(lambda: self.change_mode(8))
        # кнопка Idle 10H
        self.form.btn10H.clicked.connect(lambda: self.change_mode(1))
        # кнопка Teach 14H
        self.form.btn14H.clicked.connect(lambda: self.change_mode(5))
        # кнопка Query 05H
        self.form.btn05H.clicked.connect(lambda: self.change_mode(0))
        # кнопка Restart 18H
        self.form.btn18H.clicked.connect(lambda: self.change_mode(7))
        # кнопка Zero 15H
        self.form.btn15H.clicked.connect(lambda: self.change_mode(6))
        # кнопка File 11H
        self.form.btn11H.clicked.connect(lambda: self.change_mode(2))
        # кнопка Reset 12H
        self.form.btn12H.clicked.connect(lambda: self.change_mode(3))
        # кнопка Run 13H
        self.form.btn13H.clicked.connect(lambda: self.change_mode(4))

        # кнопка Browse INI
        self.form.btnINI.clicked.connect(lambda: self.choose_ini_file())
        # кнопка Browse CFG
        self.form.btnCFG.clicked.connect(lambda: self.choose_cfg_file())

    def read_db(self):
        self.cur.execute("SELECT * FROM settings")
        self.settings_result = self.cur.fetchone()


    def clear_list(self):
        self.form.listWidget.clear()

    def _createActions(self):
        pass

    def _createToolBars(self):
        pass

    def _createContextMenu(self):
        pass

    # Buttons func
    @logger.catch
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
                self.change_mode(0)
            except Exception as e:
                logger.info("error_open_serial_port" + str(e))

    # сохранение параметров подключения к порту
    @logger.catch
    def save_port(self):
        try:
            for_save = (self.form.cmbxPorts.currentText(), self.form.cmbxBaudRate.currentText(),
                        self.form.checkBoxReconnect.checkState(), self.form.EditINI.text(), self.form.EditCFG.text())
            if self.settings_result is None:
                query = "INSERT INTO settings (ps_port_name, ps_speed, ps_reconnect, fs_ini, fs_cfg) VALUES (?,?,?,?,?)"
            else:
                query = "UPDATE settings SET ps_port_name = ?, ps_speed = ?, ps_reconnect = ?, fs_ini = ?, fs_cfg = ?"
            self.cur.execute(query, for_save)
            self.con.commit()
            self.form.listWidget.addItem("success_save_settings_db")

            self.read_db()
        except Exception as e:
            logger.error("error_save_port_db" + str(e))


    @QtCore.pyqtSlot()
    @logger.catch
    def receive(self):
        # TODO: line = str(line).strip().strip('b').strip('\'').strip('n').strip('\\').strip('r').strip('\\')
        pack = ""
        try:
            while self.serial_port.canReadLine():
                pack += self.serial_port.readLine().data().decode()

            if self.mode in range(0, 7):
                size = self.serial_port.bytesAvailable()
                pack += self.serial_port.read(size).decode()
            pack = pack.strip().strip('b').strip('\'').strip('n').strip('\\').strip('r').strip('\\')

            if pack.isprintable:
                lblText = pack.encode('unicode_escape').decode('ascii')
            else:
                lblText = pack
            pack = "RX " + str(datetime.now()) + ":\r\n" + lblText
            self.form.listWidget.addItem(pack)
            self.form.lblMode.setText(lblText)
            logger.info(pack)
        except Exception as e:
            logger.error("error_receive_port " + str(e))

    @QtCore.pyqtSlot()
    @logger.catch
    def set_0(self):
        try:
            # stop
            self.change_mode(8)
            # exit
            self.change_mode(1)
            #reset
            self.change_mode(3)


            # stop
            self.change_mode(8)
            # exit
            self.change_mode(1)
            # teach
            self.change_mode(5)
            # joint print
            pack = "G07 GCM=0\r\n"
            self.serial_port.write(pack.encode())
            # stop
            self.change_mode(8)
        except Exception as e:
            logger.error("error_set0 " + str(e))


        # teach


    @logger.catch
    def j_minus_pressed(self, axis):
        pack = "J" + axis + "-\r\n"
        self.serial_port.write(pack.encode())
        pack = "TX " + str(datetime.now()) + ":\r\n" + pack
        self.form.listWidget.addItem(pack)
        logger.info(pack)

    @logger.catch
    def j_released(self, axis):
        pack = "J" +axis + "0\r\n"
        self.serial_port.write(pack.encode())
        pack = "TX " + str(datetime.now()) + ":\r\n" + pack
        self.form.listWidget.addItem(pack)
        logger.info(pack)

    @logger.catch
    def j_plus_pressed(self, axis):
        # self.teach_mode()
        pack = "J" + axis + "+\r\n"
        self.serial_port.write(pack.encode())
        pack = "TX " + str(datetime.now()) + ":\r\n" + pack
        self.form.listWidget.addItem(pack)
        logger.info(pack)

    @logger.catch
    def change_mode(self, id):
        self.mode = id
        try:
            pack = bytes([self.modes[id]])
            self.serial_port.write(pack)
            #self.form.listWidget.addItem("TX " + str(datetime.now()) + ":\r\n" + self.modes[id][1])
            #if chr(self.modes[id]).isprintable:
            pack = "TX " + str(datetime.now()) + ":\r\n" + chr(self.modes[id]).encode('unicode_escape').decode('ascii')
            self.form.listWidget.addItem(pack)
            logger.info(pack)
        except Exception as e:
            logger.error("error_printable " + str(e))

    # Выбор ини-файла
    @logger.catch
    def choose_ini_file(self):
        try:
            fname = QFileDialog.getOpenFileNames(self, "Open file", "SJ602-A parameter.txt", "TXT files (*.txt)")
            self.form.EditINI.setText(fname[0][0])
        except Exception as e:
            logger.error("error_choose_ini " + str(e))

    # Выбор cfg-файла
    @logger.catch
    def choose_cfg_file(self):
        try:
            fname = QFileDialog.getOpenFileNames(self, "Open file", "SJ603-A Reset parameter.txt", "TXT files (*.txt)")
            self.form.EditCFG.setText(fname[0][0])
        except Exception as e:
            logger.error("error_choose_ini " + str(e))

    def closeEvent(self, event):
        if self.status_port:
            self.open_close_port()
        QMainWindow.close(self)

@logger.catch
def main():
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = robot_form()
        window.show()
        sys.exit(app.exec_())


main()
