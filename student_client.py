import socket
from threading import Thread
from datetime import datetime
import sys
import re
import json
import time
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegExpValidator

form_class = uic.loadUiType("edu.ui")[0]


class User:
    def __init__(self, info):  # 유저가 로그인 시 클라이언트에 로그인 중인 유저 정보 저장
        self.num = info[0]
        self.uid = info[1]
        self.upw = info[2]
        self.uname = info[3]
        self.auth = info[4]


class ThreadClass:
    def __init__(self, form, host='127.0.0.1', port=9000):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.thread_recv = Thread(target=self.recv_data, daemon=True)
        # target: 실행할 함수, daemon: 메인스레드 종료 시 같이 종료할 것인지, args: 함수에 넘겨줄 인자
        self.thread_recv.start()
        self.form = form  # WindowClass 객체

    def recv_data(self):
        while True:
            data = self.client_socket.recv(9999)
            dic_data = json.loads(data.decode())  # json 데이터를 다시 파이썬 코드로 변환

            # 여기서부터 if dic_data['method'] == 기능명: 이런 식으로 기능별 서버에서 받아온 데이터 처리하는 코드 작성
            if dic_data['method'] == 'check_id_result':
                print(dic_data['result'])
                if dic_data['result']:
                    self.form.id_same_label.setVisible(False)
                    self.form.id_same_btn.setEnabled(False)
                    self.form.isIDChecked = True
                else:
                    self.form.id_same_label.setVisible(True)
                    self.form.isIDChecked = False

            if dic_data['method'] == 'login_result':
                if dic_data['result']:
                    self.form.login_user = User(dic_data['login_info'])
                    print('uid:', self.form.login_user.uid)

            if dic_data['method'] == 'registration_result':
                print(dic_data['result'])
                if dic_data['result']:
                    self.form.stackedWidget.setCurrentIndex(0)
                else:
                    print('no')

    # 여기서부터 def send_기능명(self, 매개변수): 이런 식으로 기능별 서버로 데이터 전송하는 코드 작성
    def send_check_id(self, input_id):
        data = {"method": 'check_id', "input_id": input_id, "result": bool()}
        print(data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_login(self, uid, upw):
        data = {"method": 'login', "uid": uid, "upw": upw}
        print(data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_registration(self, uid, upw, uname, auth):
        data = {"method": 'registration', "uid": uid, "upw": upw, "uname": uname, "auth": auth}
        print(data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())


class WindowClass(QMainWindow, form_class):
    login_user = None
    isIDChecked = False
    isPWRuleChecked = False
    isPWSameChecked = False
    auth = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.thread = ThreadClass(self)  # 스레드에 GUI 같이 넘겨주기

        self.stackedWidget.setCurrentIndex(0)

        self.main_login_btn.clicked.connect(self.go_login)
        self.main_sign_in_btn.clicked.connect(self.go_sign_in)
        self.login_btn.clicked.connect(self.login)
        self.sign_btn.clicked.connect(self.sign_in)

        self.id_same_btn.clicked.connect(self.check_id)
        self.id_edit.textChanged.connect(self.id_changed)
        self.password1_edit.textChanged.connect(self.pw_changed)
        self.password2_edit.textChanged.connect(self.pw_changed)

        self.student_radio.clicked.connect(self.set_auth)
        self.teacher_radio.clicked.connect(self.set_auth)

    def go_login(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_sign_in(self):
        self.stackedWidget.setCurrentIndex(2)

    def login(self):
        input_id = self.login_id_edit.text()
        input_pw = self.login_password_edit.text()
        self.thread.send_login(input_id, input_pw)
        time.sleep(0.1)
        if self.login_user is not None:
            QMessageBox.information(self, '알림', '로그인 되었습니다')
            if self.login_user.auth == 's':
                self.stackedWidget.setCurrentIndex(4)
            else:
                self.stackedWidget.setCurrentIndex(3)
        else:
            print('no')

    def check_id(self):
        self.thread.send_check_id(self.id_edit.text())

    def id_changed(self):
        self.isIDChecked = False
        self.id_same_btn.setEnabled(True)

    def pw_changed(self):
        if self.password1_edit.text().isdigit() or self.password1_edit.text().isalpha() or len(
                self.password1_edit.text()) < 8:
            self.isPWRuleChecked = False
        else:
            self.isPWRuleChecked = True
        if self.password1_edit.text() != self.password2_edit.text():
            self.isPWSameChecked = False
        else:
            self.isPWSameChecked = True

    def sign_in(self):
        if 0 in [len(self.id_edit.text()), len(self.password1_edit.text()), len(self.password2_edit.text()),
                 len(self.name_edit.text())] or self.auth is None:
            QMessageBox.warning(self, '경고', '모든 입력칸을 확인해주세요')
        elif not self.isIDChecked:
            QMessageBox.warning(self, '경고', '아이디 중복 확인을 해주세요')
        elif not self.isPWRuleChecked or not self.isPWSameChecked:
            QMessageBox.warning(self, '경고', '비밀번호를 확인해주세요')
        else:
            input_id = self.id_edit.text()
            input_pw = self.password1_edit.text()
            input_name = self.name_edit.text()
            input_auth = self.auth
            self.thread.send_registration(input_id, input_pw, input_name, input_auth)

    def set_auth(self):
        if self.student_radio.isChecked():
            self.auth = 's'
        elif self.teacher_radio.isChecked():
            self.auth = 't'



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
