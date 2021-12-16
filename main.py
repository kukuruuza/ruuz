import sys
import sqlite3
from PyQt5 import uic, QtCore
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from datetime import datetime
from loguru import logger
import os.path

# TODO: проверка ком-порта

logger.add("main.log", format="{time} {level} {message}", level="DEBUG")


@logger.catch
class robot_form(QMainWindow):

    @logger.catch
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.modes = (5, 16, 17, 18, 19, 20, 21, 24, 48)
        self.mode = ""
        self.pack = ""
        self.set_0_ready = False
        self.mode_reset_read = 0
        self.len_Reset_Read = 0
        self.text_Reset_Read = ""
        self.mode_joint_print = 0
        self.text_joint_print = ""
        self.g09_offset = [0] * 6
        self.reset_file_name = "reset parameter.txt"
        self.mode_download = 0



        # self.serial_port = QSerialPort(readyRead=self.receive)
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.receive)
        # подключение к БД
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
        try:
            self.form.btnSetZero.clicked.connect(lambda: self.set_zero())
        except Exception as e:
            logger.error("error_set_0 " + str(e))
        # кнопка Clear
        self.form.actionClear_2.triggered.connect(self.clear_list)
        # кнопка J1-
        """ try:
            for i in range(1, 2):
                lcTmp = "self.form.btnJ" + str(i) + "minus.pressed.connect(lambda: self.j_minus_pressed(\"" + str(i) + "\"))"
                print(lcTmp)
                exec(lcTmp)
                lcTmp = "self.form.btnJ" + str(i) + "minus.released.connect(lambda: self.j_released(\"" + str(i) + "\"))"
                print(lcTmp)
                exec(lcTmp)
        except Exception as e:
            self.form.listWidget.addItem("error_axis", e)
            print("error_axis", e)
        """
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

        # режимы:
        # 0 - 05H - Query
        # 1 - 10H - Idle, Exit
        # 2 - 11H - File
        # 3 - 12H - Reset
        # 4 - 13H - Run
        # 5 - 14H - Teach
        # 6 - 15H - Zero
        # 7 - 18H - Restart
        # 8 - 30H - Stop
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

        # кнопка Joint Print
        self.form.btnJP.clicked.connect(lambda: self.proc_joint_print())
        # кнопка Reset Read
        self.form.btnResetRead1.clicked.connect(lambda: self.reset_read1())
        self.form.btnResetRead2.clicked.connect(lambda: self.reset_read2())
        # кнопка Calc Offset
        self.form.btnCalcOffset.clicked.connect(lambda: self.calc_offset())

        # кнопка Download
        self.form.btnDownload.clicked.connect(lambda: self.proc_download())

        # кнопка Browse INI
        self.form.btnINI.clicked.connect(lambda: self.choose_ini_file())
        # кнопка Browse CFG
        self.form.btnCFG.clicked.connect(lambda: self.choose_cfg_file())

    @logger.catch
    def calc_offset(self):
        # try:
        #     self.file_reset_parameter.close()
        # except:
        #     logger.error("Не удалось закрыть файл reset parameter.txt")
        # разбор self.text_joint_print
        if self.text_joint_print == "":
            logger.error("Нарушена последовательность вызовов, нет координат (joint print)")
        else:
            self.form.listWidget_offsets.clear()
            # parsing = {x[0]: x[1] for x in [y.split("=") for y in self.text_joint_print.split(" ") if len(y)]}
            y = self.text_joint_print.split(" ")
            # for y in self.text_joint_print.split(" "):
            for i in range(0, 6):
                logger.debug("self.text_joint_print_parsing1: " + str(y[i]))
                x = y[i].split("=")
                logger.debug("self.text_joint_print_parsing2: " + x[0] + ", " + x[1])
                if i == 2 or i == 4:
                    max = -90
                else:
                    max = 0
                logger.debug("max: " + str(max))
                offset = max - float(x[1]) - self.g09_offset[i]
                self.form.listWidget_offsets.addItem("OFFSET" + str(i+1) + " = " + str(offset))


    @logger.catch
    def proc_download(self):
        self.mode_download = 1
        lcFile = open(self.reset_file_name, "w+")
        lcText = self.form.textEdit.toPlainText()
        lnSize = len(lcText)
        lcFile.write(lcText)
        lcFile.close() # закрыли, чтоб сохранить
        # self.change_mode(2) # 11H
        lcFile = open(self.reset_file_name)
        # lcFile1 = open(self.reset_file_name+"1", "w+")
        # i = 0
        # for line in lcFile:
        #     i = i + 1
        #     # lcText = lcFile.readline()
        #     if i > 3:
        #         lcFile1.write(line)
        # lcFile.close()
        # lcFile1.close()
        # # lcFile1 = open(self.reset_file_name + "1")
        # lnSize = os.path.getsize(self.reset_file_name + "1")
        # logger.debug("lnSizeof: " + str(lnSize))

        # # lcText1 = lcFile.read()
        for i in range(2): # отправляем первые 2 строки в порт
            lcText = lcFile.readline().rstrip("\n")
            logger.debug("Первые 2 строки: " + str(lcText))
            self.command_to_port_encode(lcText+ "\r\n")

        lcText = lcFile.readline().rstrip("\n")
        logger.debug("!!!" + lcText + ", " + str(lnSize) + ", " + str(len(str(lnSize))) + ", " + str(len(lcText)))
        lnSize += len(str(lnSize)) - len(lcText) # + lcText1.count("\n")
        logger.debug("3я строка: " + str(lnSize))
        self.command_to_port_encode(str(lnSize) + "\r\n")
        lcText = lcFile.readlines()
        logger.debug("4я и дальше строки: " + str(lcText))
        self.commands_to_port_encode(lcText)





    @logger.catch
    def proc_joint_print(self):
        if self.mode == 5:
            self.mode_joint_print = 1
            self.command_to_port_encode("G07 GCM=0\r\n")
        else:
            logger.error("JointPrint можно выполнить только в режиме 14H")

    @logger.catch
    def reset_read1(self):
        if self.mode == 2:
            self.mode_reset_read = 1
            self.command_to_port_encode("WR=Q,50\r\n")
        else:
            logger.error("ResetRead можно выполнить только в режиме 11H")

    @logger.catch
    def reset_read2(self):
        if self.mode == 2:
            if self.mode_reset_read == 1:
                if self.len_Reset_Read > 0:
                    self.form.textEdit.clear()
                    # self.file_reset_parameter = open("reset parameter.txt", "w+")
                    # self.file_reset_parameter.write("FILE=OQ\n")
                    self.form.textEdit.append("FILE=OQ")
                    self.mode_reset_read = 2
                    pack = "WR=Q," + str(self.len_Reset_Read+13) + "\r\n"
                    self.command_to_port_encode(pack)
                else:
                    logger.error("Была ошибка при нажатии ResetRead1")
            else:
                logger.error("ResetRead2 можно выполнить только после ResetRead1")
        else:
            logger.error("ResetRead можно выполнить только в режиме 11H")

    def clear_list(self):
        self.form.listWidget.clear()

    def read_db(self):
        self.cur.execute("SELECT * FROM settings")
        self.settings_result = self.cur.fetchone()

    # Buttons func
    @QtCore.pyqtSlot(bool)
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
                logger.error("error_close_serial_port" + e)
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
                logger.info("success_open_port")
                self.status_port = True
                self.form.cmbxPorts.setEnabled(False)
                self.form.cmbxBaudRate.setEnabled(False)
                self.form.btnOpenClose.setText("CLOSE")
                self.change_mode(0)
            except Exception as e:
                logger.error("error_open_serial_port" + str(e))

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
        self.pack = ""
        try:
            while self.serial_port.canReadLine():
                self.pack += self.serial_port.readLine().data().decode()

            if self.mode in [0, 1, 2, 4, 5, 6, 7]:
                size = self.serial_port.bytesAvailable()
                self.pack += self.serial_port.read(size).decode()

            # self.pack = self.pack.strip().strip('b').strip('\'').strip('n').strip('\\').strip('r').strip('\\')

            if self.pack.isprintable:
                lblText = self.pack.encode('unicode_escape').decode('ascii')
            else:
                lblText = self.pack
            lblText = lblText.split("\\r\\n")
            llReset_read = False
            for i in range(len(lblText)):
                lcTmp = "RX " + str(datetime.now()) + ":\r\n" + lblText[i]
                self.form.listWidget.addItem(lcTmp)
                if self.mode in [0, 1, 2, 5] and self.mode_reset_read == 0: # меняем lblMode - режим
                    self.form.lblMode.setText(lblText[i])

                if self.mode_reset_read > 0:
                    llReset_read = self.reset_read_receive(lblText[i], llReset_read) # обработка результатов нажатия ResetRead

                self.joint_print_receive(lblText[i]) # после нажатия joint print

                self.button_enabled_receive(lblText[i]) # доступность доп кнопок в зависимости от режима и пришедшего ответа

                logger.info(lcTmp)

            # if self.mode != 0:  # доступность доп кнопок в зависимости от режима
            #     self.form.btnJP.setEnabled(False)
            #     self.form.btnResetRead1.setEnabled(False)
            #     self.form.btnResetRead2.setEnabled(False)
        except Exception as e:
            logger.error("error_receive_port " + str(e))

    @logger.catch
    def reset_read_receive(self, lcText, llReset_read):
        if self.mode_reset_read == 1:  # после нажатия Reset Read1
            self.text_Reset_Read = ""
            if llReset_read is True:
                try:
                    self.len_Reset_Read = int(lcText)
                    self.form.btnResetRead2.setEnabled(True)
                    logger.info("self.len_Reset_Read: " + str(self.len_Reset_Read))
                except Exception as e:
                    logger.error("Ошибка после Reset Read1 " + str(e))
                llReset_read = False
            if lcText == "AM.ST":
                llReset_read = True
        if self.mode_reset_read == 2:  # после нажатия Reset Read2
            if lcText.find("G09 ENC OFFSET") == 0:
                i = int(lcText[14:15]) - 1
                self.g09_offset[i] = float(lcText[16:]) # сохраняем оффсеты в массив self.g09_offset
                logger.info("g09_offset[" + str(i) + "]: " + str(self.g09_offset[i]))
            self.text_Reset_Read += lcText
            self.form.textEdit.append(lcText)
            # self.file_reset_parameter.write(lcText + "\n")
            self.form.btnCalcOffset.setEnabled(True)
        logger.debug("llReset_read: " + str(llReset_read))
        logger.debug("self.text_Reset_Read: " + self.text_Reset_Read)
        return llReset_read

    # доступность доп кнопок в зависимости от режима
    @logger.catch
    def button_enabled_receive(self, lcText):
        if self.mode == 5 and lcText == "\\x14":  # teach
            self.form.btnJP.setEnabled(True)
        if self.mode == 2 and lcText == "\\x11":  # file
            # self.mode_reset_read = 0
            self.form.btnResetRead1.setEnabled(True)
            self.form.btnResetRead2.setEnabled(True)
            self.form.btnDownload.setEnabled(True)

    def joint_print_receive(self, lcText):
        if self.mode == 8 and self.mode_joint_print == 1 and lcText != "":
            self.text_joint_print = lcText
            self.mode_joint_print = 0
            logger.debug("self.text_joint_print: " + self.text_joint_print)

    @QtCore.pyqtSlot()
    @logger.catch
    def write_port(self, pack):
        self.serial_port.write(pack)


    @QtCore.pyqtSlot()
    @logger.catch
    def set_zero(self):
        try:
            self.cur.execute("SELECT * FROM commands_spec WHERE id_header = 1 ORDER BY spec_num")
            self.settings_result = self.cur.fetchall()
            for command in self.settings_result:
                self.command_to_port(command[3])
                # logger.info(command[3])
            # self.set_0_ready = True
            # # stop
            # self.change_mode(8)
            # # exit
            # self.change_mode(1)
            # # reset
            # self.change_mode(3)
        except Exception as e:
            logger.error("error_set0 " + str(e))


    @QtCore.pyqtSlot()
    @logger.catch
    def set_zero_1(self):
        # stop
        self.change_mode(8)
        # exit
        self.change_mode(1)
        # teach
        self.change_mode(5)
        # # joint print
        # pack = "G07 GCM=0\r\n"
        # self.serial_port.write(pack.encode())
        # pack = "TX " + str(datetime.now()) + ":\r\n" + pack
        # self.form.listWidget.addItem(pack)
        # # stop
        # self.change_mode(8)

    def command_to_port(self, text):
        if text[0:1] == "#":
            text_char = int(text[1:4])
            pack = bytes([text_char])
            self.serial_port.write(pack)
            self.pack = "TX " + str(datetime.now()) + ":\r\n" + chr(text_char).encode('unicode_escape').decode(
                'ascii')
            self.form.listWidget.addItem(self.pack)

    @logger.catch
    # отправляем одну строку  в порт
    def command_to_port_encode(self, text):
        try:
            self.serial_port.write(text.encode())
            self.pack = "TX " + str(datetime.now()) + ":\r\n" + text
            self.form.listWidget.addItem(self.pack)
        except Exception as e:
            logger.error("error_command_to_port_encode " + str(e))

    @logger.catch
    # отправляем несоклько строк  в порт
    def commands_to_port_encode(self, text):
        try:
            for i in range(len(text)):
                lcText = text[i].rstrip('\n') + "\r\n"
                self.serial_port.write(lcText.encode())
                lcPack = "TX " + str(datetime.now()) + ":\r\n" + lcText
                self.form.listWidget.addItem(lcPack)
        except Exception as e:
            logger.error("error_command_to_port_encode " + str(e))

    @QtCore.pyqtSlot()
    @logger.catch
    def j_minus_pressed(self, axis):
        try:
            pack = "J" + axis + "-\r\n"
            self.write_port(pack.encode())
            pack = "TX " + str(datetime.now()) + ":\r\n" + pack
            self.form.listWidget.addItem(pack)
            logger.info(pack)
        except Exception as e:
            logger.error("error_axis_pressed " + str(e))

    @QtCore.pyqtSlot()
    @logger.catch
    def j_released(self, axis):
        try:
            pack = "J" + axis + "0\r\n"
            self.serial_port.write(pack.encode())
            pack = "TX " + str(datetime.now()) + ":\r\n" + pack
            self.form.listWidget.addItem(pack)
            logger.info(pack)
        except Exception as e:
            logger.error("error_axis_released " + str(e))

    @QtCore.pyqtSlot()
    @logger.catch
    def j_plus_pressed(self, axis):
        # self.teach_mode()
        pack = "J" + axis + "+\r\n"
        self.serial_port.write(pack.encode())
        pack = "TX " + str(datetime.now()) + ":\r\n" + pack
        self.form.listWidget.addItem(pack)
        logger.info(pack)

    @QtCore.pyqtSlot()
    @logger.catch
    def change_mode(self, id):
        self.mode = id # последняя нажатая кнопка H
        try:
            self.pack = bytes([self.modes[id]])
            self.write_port(self.pack)
            # self.serial_port.sendBreak(1000)
            self.pack = "TX " + str(datetime.now()) + ":\r\n" + chr(self.modes[id]).encode('unicode_escape').decode(
                'ascii')
            self.form.listWidget.addItem(self.pack)
            logger.info(self.pack)


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

    @QtCore.pyqtSlot()
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
