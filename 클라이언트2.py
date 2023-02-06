import sys
from socket import *
from threading import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui

from os import environ


form_class = uic.loadUiType("edu.ui")[0]

class Main(QMainWindow, form_class):
    Client_socket = None

    def __init__(self, ip, port):
        super().__init__()
        self.setupUi(self)
        self.initialize_socket(ip, port)
        self.listen_thread()
        self.btn1.clicked.connect(self.btn11)
        self.btn2.clicked.connect(self.btn22)

        self.teacher_send_btn.clicked.connect(self.teacher_chat_send)
        self.student_send_btn.clicked.connect(self.student_chat_send)
        self.teacher_quiz_send_btn.clicked.connect(self.teacher_quiz_send)

    def teacher_quiz_send(self):
        quiz = []
        quiz_list = [self.teacher_quiz_title_edit.text(), self.teacher_quiz_edit1.text(), self.teacher_quiz_edit2.text(), self.teacher_quiz_edit3.text(), self.teacher_quiz_edit4.text(), self.teacher_quiz_edit5.text(), self.teacher_quiz_answer_edit1.text(), self.teacher_quiz_answer_edit2.text(), self.teacher_quiz_answer_edit3.text(), self.teacher_quiz_answer_edit4.text(), self.teacher_quiz_answer_edit5.text()]
        for x in quiz_list:
            quiz.append(x)
            print(quiz)
        self.client_socket.send((str(quiz_list) + "002").encode('utf-8'))

    def student_chat_send(self):
        text = self.student_text_edit.text()
        self.client_socket.send((text + "001").encode('utf-8'))
        self.student_text_edit.clear()

    def teacher_chat_send(self):
        text = self.teacher_text_edit.text()
        self.client_socket.send((text+"001").encode('utf-8'))
        self.teacher_text_edit.clear()

    def btn11(self):
        self.stackedWidget.setCurrentIndex(4)

    def btn22(self):
        self.stackedWidget.setCurrentIndex(3)

    def initialize_socket(self,ip,port):
        self.client_socket = socket(AF_INET,SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))

    def listen_thread(self):
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()

    def receive_message(self,so):
        while True:
            buf = so.recv(512)
            text = buf.decode('utf-8')
            if not buf: #연결 종료 됨
                break
            if text[-3:] == '001':
                self.teacher_chat_view_list.addItem(text[:-3])
                self.student_chat_view_list.addItem(text[:-3])
            elif text[-3:] == '002':
                print("b")
        so.close()



if __name__ == "__main__":
    ip = '10.10.21.112'
    port = 55000

    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCREEN_FACTOR"] = "1"

    app = QApplication(sys.argv)
    mainWindow = Main(ip, port)
    mainWindow.show()
    app.exec_()
