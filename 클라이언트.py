import sys
import time
from socket import *
from threading import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui

from os import environ

import json

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
        self.teacher_quiz_title_list.itemClicked.connect(self.click_topic)

        self.show_teacher_topic()
        self.show_teacher_score()

        self.a_btn.clicked.connect(self.show_teacher_topic)

    def show_teacher_score(self):
        time.sleep(0.5)
        data = {'method': '005'}
        print(data)
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())


    def click_topic(self):
        self.teacher_quiz_list.clear()
        text = self.teacher_quiz_title_list.selectedItems()
        topic = text[0].text()
        data = {'method': '004', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def show_teacher_topic(self):
        data = {'method': '003'}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def teacher_quiz_send(self):
        quiz = []
        quiz_list = [self.teacher_quiz_title_edit.text(), self.teacher_quiz_edit1.text(), self.teacher_quiz_edit2.text(), self.teacher_quiz_edit3.text(), self.teacher_quiz_edit4.text(), self.teacher_quiz_edit5.text(), self.teacher_quiz_answer_edit1.text(), self.teacher_quiz_answer_edit2.text(), self.teacher_quiz_answer_edit3.text(), self.teacher_quiz_answer_edit4.text(), self.teacher_quiz_answer_edit5.text()]

        for x in quiz_list:
            quiz.append(x)
            print(quiz)
        data = {'method': '002', 'text': quiz}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def student_chat_send(self):
        text = self.student_text_edit.text()

        data = {'method': '001', 'text': text}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

        self.student_text_edit.clear()

    def teacher_chat_send(self):
        text = self.teacher_text_edit.text()

        data = {'method': '001', 'text': text}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

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
            try:
                data = self.client_socket.recv(9999)
                dic_data = json.loads(data.decode())
            except:
                break
            else:
                # if not buf: #연결 종료 됨
                #     break
                if dic_data['method'] == '001':
                    print(dic_data['text'])
                    self.teacher_chat_view_list.addItem(dic_data['text'])
                    self.student_chat_view_list.addItem(dic_data['text'])
                elif dic_data['method'] == '002':
                    print("b")
                elif dic_data['method'] == '003':
                    print(dic_data)
                    print(dic_data['text'])
                    for x in dic_data['text']:
                        self.teacher_quiz_title_list.addItem(x[0])
                elif dic_data['method'] == '004':
                    for x in dic_data['text']:
                        self.teacher_quiz_list.addItem(x[0])
                elif dic_data['method'] == '005':
                    print(dic_data)
                    print(dic_data['text'])
                    print(len(dic_data['text']))
                    self.score_table.setRowCount(len(dic_data['text']))
                    for i in range(len(dic_data['text'])):
                        self.score_table.setItem(i, 0, QTableWidgetItem(dic_data['text'][i][0]))
                        self.score_table.setItem(i, 1, QTableWidgetItem(str(dic_data['text'][i][1])))
                        self.score_table.setItem(i, 2, QTableWidgetItem(dic_data['text'][i][2]))
                        self.score_table.setItem(i, 3, QTableWidgetItem(dic_data['text'][i][3]))
                        self.score_table.setItem(i, 4, QTableWidgetItem(dic_data['text'][i][4]))
                        self.score_table.setItem(i, 5, QTableWidgetItem(dic_data['text'][i][5]))
                        self.score_table.setItem(i, 6, QTableWidgetItem(dic_data['text'][i][6]))
                        self.score_table.setItem(i, 7, QTableWidgetItem(dic_data['text'][i][7]))
                        self.score_table.setItem(i, 8, QTableWidgetItem(str(dic_data['text'][i][8])))
                    # for x in dic_data['text']:
                    #     print(x)
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
