import sys
import os
import sqlite3
from ctypes import *
from PyQt5 import uic, QtCore
import serial
import serial.tools.list_ports
import serial.threaded
import threading
#from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from datetime import datetime
from loguru import logger
import os.path
import time


# TODO: проверка ком-порта (не помню)
# TODO: отправка в BIN HEX DEC
# TODO: режим работы актуальный видно всегда (PRND)
# TODO: скорость (0-100 и фиксированные значения)
# TODO: J1-6 отображение положения (мин-макс и "плпавющий" режим)


logger.add("main.log", format="{time} {level} {message}", level="DEBUG")


@logger.catch
class robot_form(QMainWindow):

    @logger.catch
    def __init__(self, parent=None):
        try:
            QMainWindow.__init__(self, parent)

            self.modes = (5, 16, 17, 18, 19, 20, 24, 48, 21)
            self.mode = ""
            self.pack = ""
            self.set_0_ready = False
            # self.mode_reset_read = 0
            # self.lnReset_Read = 0
            # self.text_Reset_Read = ""
            self.mode_joint_print = 0
            self.text_joint_print = ""
            self.offset_jointprint = [0] * 6  # оффсеты из координат
            self.offset_old = [0] * 6 # оффсеты из настроек ини-файла
            self.calc_offset = [0] * 6 # оффсеты вычисляем
            self.reset_file_name = "reset parameter.txt"
            self.mode_download = 0
            self.llFullPack = True
            self.J_max = [0] * 6 # максимумы осей
            self.J_min = [0] * 6 # минимумы осей


            # подключение к порту
            # self.serial_port = serial.Serial(readyRead=self.receive)
            self.serial_port = serial.Serial()
            # запустить поток приема
            # tr_in = threading.Thread(target=self.receive)
            # tr_in.daemon = True
            # tr_in.start()
            # self.serial_port.readyRead.connect(self.receive)
            # подключение к БД
            self.con = sqlite3.connect('main.db')
            self.cur = self.con.cursor()
            self.read_db()

            form, base = uic.loadUiType('main.ui')
            self.form = form()
            self.form.setupUi(self)

            self.status_port = False

            # заполнение списка доступных ком-портов
            self.serial = serial.tools.list_ports.comports()
            if len(self.serial) > 0:
                self.form.btnOpenClose.setEnabled(True)
            for port in self.serial:
                self.port_name = port.name
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

            # считываем из ини-файла параметры осей и заполняем вкладку axes
            if os.path.exists(self.form.EditINI.text()):
                self.axes_from_ini()
            else:
                logger.error(f"Не файл {self.form.EditINI.text()}")

            # КНОПКИ
            # кнопка Открыть/Закрыть порт
            self.form.btnOpenClose.clicked.connect(lambda: self.open_close_port())
            # кнопка Сохранить
            self.form.btnSave.clicked.connect(lambda: self.save_port())
            # # кнопка Set 0
            # try:
            #     self.form.btnSetZero.clicked.connect(lambda: self.set_zero())
            # except Exception as e:
            #     logger.error("error_set_0 " + str(e))
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
            #              ([20], "<DC4>"), ([24], "<CAN>"), ([48], "0"), ([21], "<NAK>"))

            # режимы:
            # 0 - 05H - Query
            # 1 - 10H - Idle, Exit
            # 2 - 11H - File
            # 3 - 12H - Reset
            # 4 - 13H - Run
            # 5 - 14H - Teach
            # 6 - 18H - Restart
            # 7 - 30H - Stop
            # 8 - 15H - Zero - пока не используется
            # кнопка Stop 30H
            self.form.btn30H.clicked.connect(lambda: self.change_mode(7))
            # кнопка Idle 10H
            self.form.btn10H.clicked.connect(lambda: self.change_mode(1))
            # кнопка Teach 14H
            self.form.btn14H.clicked.connect(lambda: self.change_mode(5))
            # кнопка Query 05H
            self.form.btn05H.clicked.connect(lambda: self.change_mode(0))
            # кнопка Restart 18H
            self.form.btn18H.clicked.connect(lambda: self.change_mode(6))
            # кнопка Zero
            self.form.btn15H.clicked.connect(lambda: self.command_to_port_encode("G00 J1=0 J2=0 J3=-90 J4=0 J5=-90 J6=0 \r\n"))
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



            # self.form.btnResetRead2.clicked.connect(lambda: self.reset_read2())
            # кнопка Calc Offset
            self.form.btnCalcOffset.clicked.connect(lambda: self.calc_new_offset())

            # кнопка Prepare
            self.form.btnPrepare.clicked.connect(lambda: self.proc_prepare())

            # кнопка Download
            self.form.btnDownload.clicked.connect(lambda: self.proc_download())

            # кнопка Read_JP
            self.form.btnReadJP.clicked.connect(lambda: self.read_JP())

            # кнопка Read_Offsets
            self.form.btnRead_Offsets.clicked.connect(lambda: self.read_offsets())

            # кнопка Calc_Size
            self.form.btnCalc_Size.clicked.connect(lambda: self.calc_size("tmp.txt"))

            # кнопка Browse INI
            self.form.btnINI.clicked.connect(lambda: self.choose_ini_file())
            # кнопка Browse CFG
            self.form.btnCFG.clicked.connect(lambda: self.choose_cfg_file())

            # # кнопка Открыть/Закрыть порт
            # self.form.btn_Close1.clicked.connect(lambda: self.close_port_dll())
            # self.form.btn_Open1.clicked.connect(lambda: self.open_port_dll())

        except Exception as e:
            logger.error(f"error_ini_form {str(e)}")

    # считываем параметры осей из ини-файла
    @logger.catch
    def axes_from_ini(self):
        try:
            lcFile = open(self.form.EditINI.text(), "r")
            lcText = lcFile.readlines()
            for j in range(6):
                lnAxeMax = 0
                lnAxeMin = 0
                for i in range(len(lcText)):
                    lcTmp = lcText[i]
                    lnFind = lcTmp.find(f"_sLp{j}=")
                    if lnFind != -1:
                        lnAxeMax = int(lcTmp[lnFind+6:]) - 5
                        logger.info(f"Максимум {j+1}-й оси: {str(lnAxeMax)}")
                        self.J_max[j] = lnAxeMax
                        self.axes_form_max(int(j), lnAxeMax)
                    lnFind = lcTmp.find(f"_sLn{j}=")
                    if lnFind != -1:
                        lnAxeMin = int(lcTmp[lnFind + 6:]) + 5
                        logger.info(f"Минимум {j+1}-й оси: {str(lnAxeMin)}")
                        self.J_min[j] = lnAxeMin
                        self.axes_form_min(int(j), lnAxeMin, lnAxeMax)

            lcFile.close()
        except Exception as e:
            logger.error(f"error_axes_from_ini {str(e)}")

    @logger.catch
    def axes_form_max(self, id, lnAxeMax):
        try:
            if id == 0:
                self.form.J1max.setText(str(lnAxeMax))
                self.form.SliderJ1.setMaximum(lnAxeMax)
            if id == 1:
                self.form.J2max.setText(str(lnAxeMax))
                self.form.SliderJ2.setMaximum(lnAxeMax)
            if id == 2:
                self.form.J3max.setText(str(lnAxeMax))
                self.form.SliderJ3.setMaximum(lnAxeMax)
            if id == 3:
                self.form.J4max.setText(str(lnAxeMax))
                self.form.SliderJ4.setMaximum(lnAxeMax)
            if id == 4:
                self.form.J5max.setText(str(lnAxeMax))
                self.form.SliderJ5.setMaximum(lnAxeMax)
            if id == 5:
                self.form.J6max.setText(str(lnAxeMax))
                self.form.SliderJ6.setMaximum(lnAxeMax)
        except Exception as e:
            logger.error(f"error_axes_form_max {str(e)}")

    @logger.catch
    def axes_form_min(self, id, lnAxeMin, lnAxeMax):
        try:
            if id == 0:
                self.form.J1min.setText(str(lnAxeMin))
                self.form.SliderJ1.setMinimum(lnAxeMin)
                self.form.SliderJ1.setValue(int((lnAxeMax+lnAxeMin)/2))
            if id == 1:
                self.form.J2min.setText(str(lnAxeMin))
                self.form.SliderJ2.setMinimum(lnAxeMin)
                self.form.SliderJ2.setValue(int((lnAxeMax+lnAxeMin)/2))
            if id == 2:
                self.form.J3min.setText(str(lnAxeMin))
                self.form.SliderJ3.setMinimum(lnAxeMin)
                self.form.SliderJ3.setValue(int((lnAxeMax+lnAxeMin)/2))
            if id == 3:
                self.form.J4min.setText(str(lnAxeMin))
                self.form.SliderJ4.setMinimum(lnAxeMin)
                self.form.SliderJ4.setValue(int((lnAxeMax+lnAxeMin)/2))
            if id == 4:
                self.form.J5min.setText(str(lnAxeMin))
                self.form.SliderJ5.setMinimum(lnAxeMin)
                self.form.SliderJ5.setValue(int((lnAxeMax+lnAxeMin)/2))
            if id == 5:
                self.form.J6min.setText(str(lnAxeMin))
                self.form.SliderJ6.setMinimum(lnAxeMin)
                self.form.SliderJ6.setValue(int((lnAxeMax+lnAxeMin)/2))

        except Exception as e:
            logger.error(f"error_axes_form_max {str(e)}")

    @logger.catch
    def calc_new_offset(self):
        # разбор self.text_joint_print
        if self.text_joint_print == "":
            logger.error("Нарушена последовательность вызовов, нет координат (joint print)")
        else:
            self.form.listWidget_offsets.clear()
            for i in range(0, 6):
                if i == 2 or i == 4:
                    max = -90
                else:
                    max = 0
                logger.debug("max: " + str(max))
                self.calc_offset[i] = round(max - self.offset_jointprint[i] + self.offset_old[i], 4)
                self.form.listWidget_offsets.addItem("OFFSET" + str(i+1) + " = " + str(self.calc_offset[i]))


    @logger.catch
    def proc_prepare(self):
        lcFile = open(self.reset_file_name, "w+")
        lcFile.write(self.form.textEdit.toPlainText())
        lcFile.close()  # закрыли, чтоб сохранить




    @logger.catch
    # для работы, когда нет подключения к роботу - из textEdit готовим массив self.calc_offset
    def read_offsets(self):
        lcText = self.form.textEdit.toPlainText().split('\n')
        for i in range(len(lcText)):
            lcTmp = lcText[i]
            if lcTmp.find("G09 ENC OFFSET") == 0:
                j = int(lcTmp[14:15]) - 1
                self.offset_old[j] = round(float(lcTmp[16:]), 4)  # сохраняем оффсеты в массив self.offset_old
                logger.info("offset_old[" + str(j) + "]: " + str(self.offset_old[j]))

    @logger.catch
    # вычисление размера в байтах содержимого TextEdit
    def calc_size(self, lcFileName):
        lcText = self.form.textEdit.toPlainText().split('\n')
        lcFile = open(lcFileName, "w+")
        for i in range(len(lcText)):
            if i < len(lcText)-1:
                lcFile.write(lcText[i] + "\n")
            else:
                lcFile.write(lcText[i])
        lcFile.close()  # закрыли, чтоб сохранить
        lnSize = os.stat(lcFileName).st_size
        self.form.lblSize.setText(str(lnSize))


    @logger.catch
    def proc_download(self):
        self.mode_download = 1
        self.change_mode(2)  # 11H
        # отправляем первые 3 строки, потом надо дождаться ответа от робота, и послать остальные строки
        lcText = self.form.textEdit.toPlainText().split('\n')
        for i in range(3):
            self.command_to_port_encode(lcText[i]+"\r\n")

        # self.commands_to_port_encode(self.form.textEdit.toPlainText()+"\r\n")
        # lcFile = open(self.reset_file_name, "w+")
        # # self.change_mode(2) # 11H
        # # self.command_to_port_encode("FILE=OQ\r\n")
        # lcText = self.form.textEdit.toPlainText().split('\n')
        # for i in range(len(lcText)):
        #     if i > 2:
        #         lcFile.write(lcText[i])
        # lcFile.close()  # закрыли, чтоб сохранить

        # lnSize = sys.getsizeof(lcText)
        # logger.debug("!!! " + str(lnSize))
        # lcText = lcText.split('\n')
        # for i in range(len(lcText)):
        #     if i != 2:
        #         # if i < len(lcText):
        #         #     lcTmp = "\r\n"
        #         # else:
        #         #     lcTmp = ""
        #         self.command_to_port_encode(lcText[i] + "\r\n")
        #         logger.debug(str(i) + "-я строка: " + lcText[i])
        #     else:
        #         # в 3ю пишем размер в байтах
        #         self.command_to_port_encode(str(lnSize)+"\r\n")
        #         logger.debug("3-я строка: " + str(lnSize))

        # lcFile.write(lcText)
        # lcFile.close() # закрыли, чтоб сохранить


        # lcFile = open(self.reset_file_name)
        # for i in range(2): # отправляем первые 2 строки в порт
        #     lcText = lcFile.readline().rstrip("\n")
        #     logger.debug("Первые 2 строки: " + str(lcText))
        #     self.command_to_port_encode(lcText+ "\r\n")
        #
        # lcText = lcFile.readline().rstrip("\n")
        # logger.debug("!!!" + lcText + ", " + str(lnSize) + ", " + str(len(str(lnSize))) + ", " + str(len(lcText)))
        # lnSize += len(str(lnSize)) - len(lcText) # + lcText1.count("\n")
        # logger.debug("3я строка: " + str(lnSize))
        # self.command_to_port_encode(str(lnSize) + "\r\n")
        # lcText = lcFile.readlines()
        # logger.debug("4я и дальше строки: " + str(lcText))
        # self.commands_to_port_encode(lcText)

    @logger.catch
    # после ответа робота отправляем с 4й строки все остальное из textEdit
    def proc_download_end(self):
        lcText = self.form.textEdit.toPlainText().split('\n')
        for i in range(3, len(lcText)):
            self.command_to_port_encode(lcText[i]+"\r\n")
        # отменяем параметры после записи файла в робота
        self.mode_download = 0
        # self.mode_reset_read = 0
        # self.len_Reset_Read = 0
        # self.text_Reset_Read = ""
        self.mode_joint_print = 0
        self.text_joint_print = ""
        self.offset_old = [0] * 6 # оффсеты из настроек ини-файла
        self.calc_offset = [0] * 6 # оффсеты вычисляем
        logger.debug("Download завершена")

    @logger.catch
    def reset_read(self):
        self.reset_read_thread = threading.Thread(target=self.reset_read1)
        self.reset_read_thread.daemon = True
        self.reset_read_thread.start()

    @logger.catch
    def reset_read1(self):
        try:
            if self.mode == 2:
                self.command_to_port_encode("WR=Q,50\r\n")
                time.sleep(0.5)
                pack = self.pack.split("\r\n")
                lnReset_Read = int(pack[1]) # во 2й строке ответа робота должно вернуться нужное число
                # logger.info(f"lnReset_Read = {pack[1]}")
                if lnReset_Read > 0: #
                    self.form.textEdit.clear()
                    self.form.textEdit.append("FILE=OQ")
                    pack = "WR=Q," + str(lnReset_Read+13) + "\r\n"
                    self.command_to_port_encode(pack)
                    time.sleep(1)
                    pack = self.pack.split("\r\n")
                    for i in range(len(pack)):
                        lcText = pack[i]
                        # logger.info(lcText)
                        if lcText.find("G09 ENC OFFSET") == 0:
                            i = int(lcText[14:15]) - 1
                            self.offset_old[i] = round(float(lcText[16:]), 4) # сохраняем оффсеты в массив self.offset_old
                            logger.info("offset_old[" + str(i) + "]: " + str(self.offset_old[i]))
                        # self.text_Reset_Read += lcText
                        self.form.textEdit.append(lcText)
                    self.form.btnCalcOffset.setEnabled(True)
                else:
                    logger.error(f"ResetRead после команды WR=Q,50 вернул неверный ответ: {lcText}")
            else:
                logger.error("ResetRead можно выполнить только в режиме 11H")
        except Exception as e:
            logger.error(f"reset read {str(e)}")


    # @logger.catch
    # def reset_read2(self):
    #     if self.mode == 2:
    #         if self.mode_reset_read == 1:
    #             if self.len_Reset_Read > 0:
    #                 self.form.textEdit.clear()
    #                 # self.file_reset_parameter = open("reset parameter.txt", "w+")
    #                 # self.file_reset_parameter.write("FILE=OQ\n")
    #                 self.form.textEdit.append("FILE=OQ")
    #                 self.mode_reset_read = 2
    #                 pack = "WR=Q," + str(self.len_Reset_Read+13) + "\r\n"
    #                 self.command_to_port_encode(pack)
    #             else:
    #                 logger.error("Была ошибка при нажатии ResetRead1")
    #         else:
    #             logger.error("ResetRead2 можно выполнить только после ResetRead1")
    #     else:
    #         logger.error("ResetRead можно выполнить только в режиме 11H")

    def clear_list(self):
        self.form.listWidget.clear()

    def read_db(self):
        self.cur.execute("SELECT * FROM settings")
        self.settings_result = self.cur.fetchone()

    # Buttons func
    @QtCore.pyqtSlot(bool)
    @logger.catch
    def open_close_port(self):
        try:
            # кнопка Закрыть порт
            if self.status_port:
                self.serial_port.close()
                self.form.cmbxPorts.setEnabled(True)
                self.form.cmbxBaudRate.setEnabled(True)
                self.form.btnOpenClose.setText("OPEN")
                self.form.listWidget.addItem("success_close_port")
                print("success_close_port")
                self.status_port = False
            else:
                # кнопка Открыть порт
                # self.serial_port = QSerialPort()
                port = self.form.cmbxPorts.currentText()
                # self.serial_port.setPortName(port)
                # self.serial_port = port
                speed = int(self.form.cmbxBaudRate.currentText())
                self.serial_port = serial.Serial(port, baudrate=speed, parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

                self.form.listWidget.addItem("success_open_port")
                logger.info("success_open_port")
                self.status_port = True
                self.form.cmbxPorts.setEnabled(False)
                self.form.cmbxBaudRate.setEnabled(False)
                self.form.btnOpenClose.setText("CLOSE")
                self.change_mode(0)

                self.input_thread = threading.Thread(target=self.receive)
                self.input_thread.daemon = True
                self.input_thread.start()

        except Exception as e:
            logger.error(f"error_open_close_serial_port {str(e)}")
            self.read_db()
        except Exception as e:
            logger.error("error_save_port_db" + str(e))

    # сохранение параметров подключения к порту
    @logger.catch
    def save_port(self):
        for_save = (self.form.cmbxPorts.currentText(), self.form.cmbxBaudRate.currentText(),
                    self.form.checkBoxReconnect.checkState(), self.form.EditINI.text(), self.form.EditCFG.text())
        if self.settings_result is None:
            query = "INSERT INTO settings (ps_port_name, ps_speed, ps_reconnect, fs_ini, fs_cfg) VALUES (?,?,?,?,?)"
        else:
            query = "UPDATE settings SET ps_port_name = ?, ps_speed = ?, ps_reconnect = ?, fs_ini = ?, fs_cfg = ?"
        self.cur.execute(query, for_save)
        self.con.commit()
        self.form.listWidget.addItem("success_save_settings_db")


    # @logger.catch
    # def reset_read_receive(self, lcText, llReset_read):
    #     if self.mode_reset_read == 1:  # после нажатия Reset Read1
    #         self.text_Reset_Read = ""
    #         if llReset_read is True:
    #             try:
    #                 self.len_Reset_Read = int(lcText)
    #                 self.form.btnResetRead2.setEnabled(True)
    #                 logger.info("self.len_Reset_Read: " + str(self.len_Reset_Read))
    #             except Exception as e:
    #                 logger.error("Ошибка после Reset Read1 " + str(e))
    #             llReset_read = False
    #         if lcText == "AM.ST":
    #             llReset_read = True # в следующей строке будет длина текста
    #     if self.mode_reset_read == 2:  # после нажатия Reset Read2
    #         if lcText.find("G09 ENC OFFSET") == 0:
    #             i = int(lcText[14:15]) - 1
    #             self.offset_old[i] = round(float(lcText[16:]),4) # сохраняем оффсеты в массив self.offset_old
    #             logger.info("offset_old[" + str(i) + "]: " + str(self.offset_old[i]))
    #         self.text_Reset_Read += lcText
    #         self.form.textEdit.append(lcText)
    #         self.form.btnCalcOffset.setEnabled(True)
    #     logger.debug("llReset_read: " + str(llReset_read))
    #     logger.debug("self.text_Reset_Read: " + self.text_Reset_Read)
    #     return llReset_read

    # доступность доп кнопок в зависимости от режима
    @logger.catch
    def button_enabled_receive(self, lcText):
        if self.mode == 5 and lcText == "\\x14":  # teach 14H
            self.form.btnJP.setEnabled(True)
            self.form.tab_axis.setEnabled(True)
            self.form.btn12H.setEnabled(False)
            self.form.btn13H.setEnabled(False)
            self.form.btn15H.setEnabled(True)
            self.form.btn11H.setEnabled(False)
            self.form.btn05H.setEnabled(False)
            self.form.btn18H.setEnabled(False)
            self.form.btn10H.setEnabled(False)
        if self.mode == 2 and lcText == "\\x11":  # file 11H
            # self.mode_reset_read = 0
            self.form.btnResetRead1.setEnabled(True)
            self.form.btnResetRead2.setEnabled(True)
            self.form.btnDownload.setEnabled(True)
            self.form.tab_axis.setEnabled(False)
            self.form.btn12H.setEnabled(False)
            self.form.btn13H.setEnabled(False)
            self.form.btn15H.setEnabled(False)
            self.form.btn14H.setEnabled(False)
            self.form.btn05H.setEnabled(False)
            self.form.btn18H.setEnabled(False)
            self.form.btn10H.setEnabled(False)
        if lcText[0:1] == "\\" and self.mode != 5 and self.mode != 2:
            self.form.tab_axis.setEnabled(False)
            self.form.btnResetRead1.setEnabled(False)
            self.form.btnResetRead2.setEnabled(False)
            self.form.btnDownload.setEnabled(False)
        if lcText == "\\x10":  #idle 10H
            self.form.btn12H.setEnabled(True)
            self.form.btn13H.setEnabled(True)
            self.form.btn15H.setEnabled(True)
            self.form.btn11H.setEnabled(True)
            self.form.btn05H.setEnabled(True)
            self.form.btn18H.setEnabled(True)
            self.form.btn14H.setEnabled(True)
        if lcText == "0":  # 0
            self.form.tab_axis.setEnabled(False)
            self.form.btn12H.setEnabled(False)
            self.form.btn13H.setEnabled(False)
            self.form.btn14H.setEnabled(False)
            self.form.btn15H.setEnabled(False)
            self.form.btn11H.setEnabled(False)
            self.form.btn05H.setEnabled(False)
            self.form.btn18H.setEnabled(False)
            self.form.btn10H.setEnabled(True)


    @QtCore.pyqtSlot()
    @logger.catch
    def write_port(self, pack):
        self.serial_port.write(pack)


    # @QtCore.pyqtSlot()
    # @logger.catch
    # def set_zero(self):
    #     try:
    #         self.cur.execute("SELECT * FROM commands_spec WHERE id_header = 1 ORDER BY spec_num")
    #         self.settings_result = self.cur.fetchall()
    #         for command in self.settings_result:
    #             self.command_to_port(command[3])
    #             # logger.info(command[3])
    #         # self.set_0_ready = True
    #         # # stop
    #         # self.change_mode(8)
    #         # # exit
    #         # self.change_mode(1)
    #         # # reset
    #         # self.change_mode(3)
    #     except Exception as e:
    #         logger.error("error_set0 " + str(e))


    # @QtCore.pyqtSlot()
    # @logger.catch
    # def set_zero_1(self):
    #     # stop
    #     self.change_mode(7)
    #     # exit
    #     self.change_mode(1)
    #     # teach
    #     self.change_mode(5)
    #     # # joint print
    #     # pack = "G07 GCM=0\r\n"
    #     # self.serial_port.write(pack.encode())
    #     # pack = "TX " + str(datetime.now()) + ":\r\n" + pack
    #     # self.form.listWidget.addItem(pack)
    #     # # stop
    #     # self.change_mode(8)

    @logger.catch
    # отправляем одну строку байтами
    def command_to_port(self, text):
        try:
            if text[0:1] == "#":
                text_char = int(text[1:4])
                pack = bytes([text_char])
                self.serial_port.write(pack)
                self.pack = "TX " + str(datetime.now()) + ":\r\n" + chr(text_char).encode('unicode_escape').decode(
                    'ascii')
                self.form.listWidget.addItem(self.pack)
        except Exception as e:
            logger.error("error_command_to_port " + str(e))

    @logger.catch
    # отправляем одну строку в порт текстом
    def command_to_port_encode(self, text):
        try:
            self.serial_port.write(text.encode())
            self.pack = "TX " + str(datetime.now()) + ":\r\n" + text
            self.form.listWidget.addItem(self.pack)
        except Exception as e:
            logger.error("error_command_to_port_encode " + str(e))

    @logger.catch
    # отправляем несколько строк  в порт
    def commands_to_port_encode(self, text):
        try:
            for i in range(len(text)):
                if lcText != "":
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
            # self.serial_port.waitForReadyRead(2000)
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
        try:
            # if self.mode_reset_read == 2:
            #     self.mode_reset_read = 1
            self.mode = id  # последняя нажатая кнопка H

            self.pack = bytes([self.modes[id]])
            self.write_port(self.pack)
            self.pack = "TX---->>> " + str(datetime.now()) + ":\r\n" + chr(self.modes[id]).encode('unicode_escape').decode(
                'ascii')
            self.form.listWidget.addItem(self.pack)
            logger.info(self.pack)
            if id == 1:  # если нажали 10H
                self.button_enabled_receive("\\x10")

            if id == 7:  # если нажали 0, становится доступной кнопка 10H
                self.button_enabled_receive("0")
        except Exception as e:
            logger.error("error_printable " + str(e))

    # Выбор ини-файла
    @logger.catch
    def choose_ini_file(self):
        try:
            fname = QFileDialog.getOpenFileNames(self, "Open file", "SJ602-A INI.txt", "TXT files (*.txt)")
            self.form.EditINI.setText(fname[0][0])
            self.axes_from_ini()
        except Exception as e:
            logger.error("error_choose_ini " + str(e))

    # Выбор cfg-файла
    @logger.catch
    def choose_cfg_file(self):
        try:
            fname = QFileDialog.getOpenFileNames(self, "Open file", "SJ603-A CFG.txt", "TXT files (*.txt)")
            self.form.EditCFG.setText(fname[0][0])
        except Exception as e:
            logger.error("error_choose_ini " + str(e))

    @QtCore.pyqtSlot()
    def closeEvent(self, event):
        if self.serial_port.is_open:
            self.open_close_port()
        QMainWindow.close(self)

    @logger.catch
    def joint_print_receive(self, lcText):
        if self.mode == 7 and self.mode_joint_print == 1 and lcText != "":
            self.text_joint_print = lcText
            logger.debug("self.text_joint_print: " + self.text_joint_print)
            self.mode_joint_print = 0

    @logger.catch
    def proc_joint_print(self):
        if self.mode == 5:
            self.mode_joint_print = 1
            self.command_to_port_encode("G07 GCM=0\r\n")
        else:
            logger.error("JointPrint можно выполнить только в режиме 14H")

    @logger.catch
    # для работы, когда нет подключения к роботу - считываем строку self.text_joint_print из textEdit
    def read_JP(self):
        self.text_joint_print = self.form.textEdit.toPlainText()
        logger.debug("self.text_joint_print = " + self.text_joint_print)

    @logger.catch
    def joint_print_parsing(self, lcText):
        y = lcText.split(" ")
        for i in range(6):
            lcTmp = y[i].strip('\\').strip('n').strip('\\').strip('r')
            logger.debug(f"self.text_joint_print_parsing: {lcTmp}")
            self.offset_jointprint[i] = float(y[i].split("=")[1])
        self.form.SpinJ1.setValue(self.offset_jointprint[0])
        self.form.SpinJ2.setValue(self.offset_jointprint[1])
        self.form.SpinJ3.setValue(self.offset_jointprint[2])
        self.form.SpinJ4.setValue(self.offset_jointprint[3])
        self.form.SpinJ5.setValue(self.offset_jointprint[4])
        self.form.SpinJ6.setValue(self.offset_jointprint[5])
        self.form.SliderJ1.setValue(int(self.offset_jointprint[0]))
        self.form.SliderJ2.setValue(int(self.offset_jointprint[1]))
        self.form.SliderJ3.setValue(int(self.offset_jointprint[2]))
        self.form.SliderJ4.setValue(int(self.offset_jointprint[3]))
        self.form.SliderJ5.setValue(int(self.offset_jointprint[4]))
        self.form.SliderJ6.setValue(int(self.offset_jointprint[5]))

    # обрабатываем ответ из порта
    @QtCore.pyqtSlot()
    @logger.catch
    def receive(self):
        # TODO: line = str(line).strip().strip('b').strip('\'').strip('n').strip('\\').strip('r').strip('\\')
        try:
            while 1:
                if self.serial_port.inWaiting() > 0:
                    self.pack = self.serial_port.read(self.serial_port.inWaiting()).decode()
                    logger.debug("pack_receive_port:")
                    logger.info(self.pack)

                    if self.pack.isprintable:
                        lblText = self.pack.encode('unicode_escape').decode('ascii')
                    else:
                        lblText = self.pack
                    lblText = lblText.split("\\r\\n")
                    # llReset_read = False

                    for i in range(len(lblText)):
                        lcText = lblText[i]

                        lcTmp = "RX<<<=== " + str(datetime.now()) + ":\r\n" + lcText
                        self.form.listWidget.addItem(lcTmp)
                        # меняем lblMode - режим
                        if self.mode in [0, 1, 2, 5, 6] and (lcText=="0" or lcText[0:1]=="\\"):
                            self.form.lblMode.setText(lcText)
                            self.form.statusbar.showMessage(lcText)

                        # if self.mode_reset_read > 0:
                        #     llReset_read = self.reset_read_receive(lblText[i], llReset_read) # обработка результатов нажатия ResetRead

                        if lcText == "\\x11" and self.mode_download == 1:
                            self.proc_download_end()

                        # если вернулась строка с координатами, парсим ее
                        if lcText.find("J1=")!=-1 and lcText.find("J2=")!=-1 and lcText.find("J3=")!=-1 and lcText.find("J4=")!=-1 and lcText.find("J5=")!=-1 and lcText.find("J6=")!=-1:
                            if lcText.startswith("G"):
                                self.joint_print_parsing(lcText[4:])
                            else:
                                self.joint_print_parsing(lcText)

                        self.joint_print_receive(lcText) # после нажатия joint print

                        self.button_enabled_receive(lcText) # доступность доп кнопок в зависимости от режима и пришедшего ответа

                        logger.info(lcTmp)
                else:
                    time.sleep(0.3)
        except Exception as e:
            logger.error("error_receive_port " + str(e))


@logger.catch
def main():
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = robot_form()
        window.show()
        sys.exit(app.exec_())


main()
