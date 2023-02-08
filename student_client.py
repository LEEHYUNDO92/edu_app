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
                print('recv:', dic_data['method'])
                if dic_data['result']:
                    self.form.label_id_check.setVisible(False)
                    self.form.btn_id_check.setEnabled(False)
                    self.form.isIDChecked = True
                else:
                    self.form.label_id_check.setVisible(True)
                    self.form.isIDChecked = False

            if dic_data['method'] == 'login_result':
                print('recv:', dic_data['method'])
                if dic_data['method']:
                    self.form.login_user = User(dic_data['login_info'])
                    print('uid:', self.form.login_user.uid)

            if dic_data['method'] == 'registration_result':
                print('recv:', dic_data['method'])
                if dic_data['result']:
                    self.form.stackedWidget.setCurrentIndex(0)
                else:
                    print('no')

            if dic_data['method'] == 'load_table_result':
                print('recv:', dic_data['method'])
                print('recv_data:', dic_data['data'])
                row_num = dic_data['data'][0] - 1
                if self.form.login_user.auth == 's':
                    qna_table = self.form.table_stu_qna
                else:
                    qna_table = self.form.table_tea_qna
                qna_table.insertRow(row_num)
                print(qna_table.rowCount())
                qna_table.setItem(row_num, 0, QTableWidgetItem(str(dic_data['data'][0])))
                qna_table.setItem(row_num, 1, QTableWidgetItem(dic_data['data'][1]))
                qna_table.setItem(row_num, 2, QTableWidgetItem(dic_data['data'][2]))
                if dic_data['data'][3] is None:
                    qna_table.setItem(row_num, 3, QTableWidgetItem('대기'))
                else:
                    qna_table.setItem(row_num, 3, QTableWidgetItem('완료'))

            if dic_data['method'] == 'qna_detail_result':
                print('recv:', dic_data['method'])
                print('result:', dic_data['result'])
                if self.form.login_user.auth == 's':
                    self.form.label_stu_qna_title.setText(dic_data['result'][3])
                    self.form.browser_stu_qna_content.append(dic_data['result'][4])
                    self.form.label_stu_qna_stu_name.setText(dic_data['result'][2])
                    self.form.label_stu_qna_stu_id.setText("("+dic_data['result'][1]+")")
                    self.form.label_stu_qna_add_time.setText(dic_data['result'][8])
                    self.form.label_stu_qna_edit_time.setText(dic_data['result'][9])
                    self.form.label_stu_qna_tea_name.setText(dic_data['result'][6])
                    if dic_data['result'][5] is not None:
                        self.form.label_stu_qna_tea_id.setText("("+dic_data['result'][5]+")")
                    else:
                        self.form.label_stu_qna_tea_id.clear()
                    self.form.browser_stu_qna_answer.append(dic_data['result'][7])
                else:
                    self.form.label_tea_qna_title.setText(dic_data['result'][3])
                    self.form.browser_tea_qna_content.append(dic_data['result'][4])
                    self.form.label_tea_qna_stu_name.setText(dic_data['result'][2])
                    self.form.label_tea_qna_stu_id.setText("("+dic_data['result'][1]+")")
                    self.form.label_tea_qna_add_time.setText(dic_data['result'][8])
                    self.form.label_tea_qna_edit_time.setText(dic_data['result'][9])
                    self.form.label_tea_qna_tea_name.setText(dic_data['result'][6])
                    if dic_data['result'][5] is not None:
                        self.form.label_tea_qna_tea_id.setText("("+dic_data['result'][5]+")")
                    else:
                        self.form.label_tea_qna_tea_id.clear()
                    self.form.browser_tea_qna_answer.append(dic_data['result'][7])

    # 여기서부터 def send_기능명(self, 매개변수): 이런 식으로 기능별 서버로 데이터 전송하는 코드 작성
    def send_check_id(self, input_id):
        data = {"method": 'check_id', "input_id": input_id, "result": bool()}
        print('send:', data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_login(self, uid, upw):
        data = {"method": 'login', "uid": uid, "upw": upw}
        print('send:', data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_registration(self, uid, upw, uname, auth):
        data = {"method": 'registration', "uid": uid, "upw": upw, "uname": uname, "auth": auth}
        print('send:', data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_load_table(self):
        data = {"method": 'load_table', "member_num": self.form.login_user.num}
        print('send:', data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_qna_detail(self, qna_num):
        data = {"method": 'qna_detail', "qna_num": qna_num}
        print('send:', data['method'])
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
        self.tab_student.setCurrentIndex(0)
        self.tab_teacher.setCurrentIndex(0)
        self.stack_stu_qna.setCurrentIndex(0)
        self.stack_tea_qna.setCurrentIndex(0)

        self.btn_main_to_login.clicked.connect(self.go_login)
        self.btn_main_to_sign_in.clicked.connect(self.go_sign_in)
        self.btn_login.clicked.connect(self.login)
        self.btn_sign_in.clicked.connect(self.sign_in)

        self.btn_id_check.clicked.connect(self.check_id)
        self.input_sign_in_id.textChanged.connect(self.id_changed)
        self.input_sign_in_pw.textChanged.connect(self.pw_changed)
        self.input_sign_in_pw_ck.textChanged.connect(self.pw_changed)

        self.tab_student.currentChanged.connect(self.tab_changed)
        self.tab_teacher.currentChanged.connect(self.tab_changed)

        self.table_stu_qna.doubleClicked.connect(self.view_qna_detail)
        self.table_tea_qna.doubleClicked.connect(self.view_qna_detail)

        self.radio_sign_in_student.clicked.connect(self.set_auth)
        self.radio_sign_in_teacher.clicked.connect(self.set_auth)

    def go_login(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_sign_in(self):
        self.stackedWidget.setCurrentIndex(2)

    def tab_changed(self):
        self.stack_stu_qna.setCurrentWidget(self.stack_stu_qna_list)
        self.stack_tea_qna.setCurrentWidget(self.stack_tea_qna_list)
        tab_student = self.tab_student.currentWidget()
        tab_teacher = self.tab_teacher.currentWidget()
        if tab_student == self.tab_stu_qna or tab_teacher == self.tab_tea_qna:
            print('tab_qna')
            self.load_qna()

    def load_qna(self):
        self.table_stu_qna.setRowCount(0)
        self.table_tea_qna.setRowCount(0)
        self.thread.send_load_table()

    def view_qna_detail(self):
        self.browser_stu_qna_content.clear()
        self.browser_tea_qna_content.clear()
        self.browser_stu_qna_answer.clear()
        self.browser_tea_qna_answer.clear()
        sender = self.sender()
        print(sender == self.table_stu_qna)
        row = sender.currentIndex().row()
        print(row)
        sel_data = sender.item(row, 0).text()
        print(sel_data)
        self.thread.send_qna_detail(sel_data)
        self.stack_stu_qna.setCurrentWidget(self.stack_stu_qna_detail)
        self.stack_tea_qna.setCurrentWidget(self.stack_tea_qna_detail)

    def login(self):
        input_id = self.input_login_id.text()
        input_pw = self.input_login_pw.text()
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
        self.thread.send_check_id(self.input_sign_in_id.text())

    def id_changed(self):
        self.isIDChecked = False
        self.btn_id_check.setEnabled(True)

    def pw_changed(self):
        if self.input_sign_in_pw.text().isdigit() or self.input_sign_in_pw.text().isalpha() or len(
                self.input_sign_in_pw.text()) < 8:
            self.isPWRuleChecked = False
        else:
            self.isPWRuleChecked = True
        if self.input_sign_in_pw.text() != self.input_sign_in_pw_ck.text():
            self.isPWSameChecked = False
        else:
            self.isPWSameChecked = True

    def sign_in(self):
        if 0 in [len(self.input_sign_in_id.text()), len(self.input_sign_in_pw.text()), len(self.input_sign_in_pw_ck.text()),
                 len(self.input_sign_in_name.text())] or self.auth is None:
            QMessageBox.warning(self, '경고', '모든 입력칸을 확인해주세요')
        elif not self.isIDChecked:
            QMessageBox.warning(self, '경고', '아이디 중복 확인을 해주세요')
        elif not self.isPWRuleChecked or not self.isPWSameChecked:
            QMessageBox.warning(self, '경고', '비밀번호를 확인해주세요')
        else:
            input_id = self.input_sign_in_id.text()
            input_pw = self.input_sign_in_pw.text()
            input_name = self.input_sign_in_name.text()
            input_auth = self.auth
            self.thread.send_registration(input_id, input_pw, input_name, input_auth)

    def set_auth(self):
        if self.radio_sign_in_student.isChecked():
            self.auth = 's'
        elif self.radio_sign_in_teacher.isChecked():
            self.auth = 't'


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
