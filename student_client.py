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

form_class = uic.loadUiType("edu_rgm.ui")[0]


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
                if dic_data['result']:
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
                row_num = dic_data['index']
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

                    if self.form.login_user.num == dic_data['result'][1]:
                        self.form.isSameUser = True
                    else:
                        self.form.isSameUser = False

                    data_list = [self.form.text_stu_qna_title, self.form.text_stu_qna_content,
                                 self.form.label_stu_qna_stu_name, self.form.label_stu_qna_stu_id,
                                 self.form.label_stu_qna_add_time, self.form.label_stu_qna_edit_time,
                                 self.form.label_stu_qna_tea_name, self.form.label_stu_qna_tea_id,
                                 self.form.text_stu_qna_answer, self.form.label_stu_qna_num]
                else:
                    data_list = [self.form.text_tea_qna_title, self.form.text_tea_qna_content,
                                 self.form.label_tea_qna_stu_name, self.form.label_tea_qna_stu_id,
                                 self.form.label_tea_qna_add_time, self.form.label_tea_qna_edit_time,
                                 self.form.label_tea_qna_tea_name, self.form.label_tea_qna_tea_id,
                                 self.form.text_tea_qna_answer, self.form.label_tea_qna_num]

                data_list[0].setText(dic_data['result'][4])
                data_list[1].append(dic_data['result'][5])
                data_list[2].setText(dic_data['result'][3])
                data_list[3].setText("("+dic_data['result'][2]+")")
                data_list[4].setText(dic_data['result'][9])
                data_list[5].setText(dic_data['result'][10])
                data_list[6].setText(dic_data['result'][7])
                if dic_data['result'][6] is not None:
                    data_list[7].setText("("+dic_data['result'][6]+")")
                else:
                    data_list[7].clear()
                data_list[8].append(dic_data['result'][8])
                data_list[9].setText(str(dic_data['result'][0]))

            if dic_data['method'] == 'add_question_result':
                print('recv:', dic_data['method'])
                print('result:', dic_data['result'])
                self.form.stack_stu_qna.setCurrentWidget(self.form.stack_stu_qna_list)
                self.form.load_qna()

            if dic_data['method'] == 'edit_question_result':
                print('recv:', dic_data['method'])
                print('result:', dic_data['result'])
                self.form.stack_stu_qna.setCurrentWidget(self.form.stack_stu_qna_list)
                self.form.load_qna()

            if dic_data['method'] == 'delete_question_result':
                print('recv:', dic_data['method'])
                print('result:', dic_data['result'])
                if self.form.login_user.auth == 's':
                    self.form.stack_stu_qna.setCurrentWidget(self.form.stack_stu_qna_list)
                else:
                    self.form.stack_tea_qna.setCurrentWidget(self.form.stack_tea_qna_list)
                self.form.load_qna()

            if dic_data['method'] == 'answer_result':
                print('recv:', dic_data['method'])
                print('result:', dic_data['result'])
                self.form.stack_tea_qna.setCurrentWidget(self.form.stack_tea_qna_list)
                self.form.load_qna()

            if dic_data['method'] == 'point_grade_result':
                print('recv:', dic_data['method'])
                print('point:', dic_data['point'], 'grade:', dic_data['grade'])
                # print('max_point:', dic_data['max_point'])
                self.form.label_stu_point.setText(str(dic_data['point']))
                self.form.label_stu_my_name.setText(self.form.login_user.uname)
                self.form.label_stu_grade.setText(dic_data['grade'])

            if dic_data['method'] == 'load_quiz_score_result':
                print('recv:', dic_data['method'])
                print('recv_data:', dic_data['data'])
                table = self.form.table_stu_quiz_result
                row_num = dic_data['index']
                table.insertRow(row_num)
                print(table.rowCount())
                table.setItem(row_num, 0, QTableWidgetItem(dic_data['data'][0]))
                table.setItem(row_num, 1, QTableWidgetItem(dic_data['data'][2]))
                question_num = 0
                for n in range(3, 8):
                    if dic_data['data'][n] is None:
                        table.setItem(row_num, n, QTableWidgetItem(''))
                    else:
                        table.setItem(row_num, n, QTableWidgetItem(dic_data['data'][n]))
                        question_num += 1
                table.setItem(row_num, 2, QTableWidgetItem(str(dic_data['data'][8])+' / ' + str(question_num)))

    # 여기서부터 def send_기능명(self, 매개변수): 이런 식으로 기능별 서버로 데이터 전송하는 코드 작성
    def send_check_id(self, input_id):
        data = {"method": 'check_id', "input_id": input_id, "result": bool()}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_login(self, uid, upw):
        data = {"method": 'login', "uid": uid, "upw": upw}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_registration(self, uid, upw, uname, auth):
        data = {"method": 'registration', "uid": uid, "upw": upw, "uname": uname, "auth": auth}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_load_table(self, member_num):
        data = {"method": 'load_table', "member_num": member_num}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_qna_detail(self, qna_num):
        data = {"method": 'qna_detail', "qna_num": qna_num}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_add_question(self, num, title, content, add_time):
        data = {"method": 'add_question', "member_num": num, "title": title, "content": content, "add_time": add_time}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_edit_question(self, qna_num, title, content, edit_time):
        data = {"method": 'edit_question', "qna_num": qna_num, "title": title, "content": content, "edit_time": edit_time}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_delete_question(self, qna_num):
        data = {"method": 'delete_question', "qna_num": qna_num}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_answer(self, qna_num, member_num, answer):
        data = {"method": 'answer', "qna_num": qna_num, "member_num": member_num, "answer": answer}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_point_grade(self, member_num):
        data = {"method": 'point_grade', "member_num": member_num}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_load_quiz_score(self, member_num):
        data = {"method": 'load_quiz_score', "member_num": member_num}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])


class WindowClass(QMainWindow, form_class):
    login_user = None
    isIDChecked = False
    isPWRuleChecked = False
    isPWSameChecked = False
    isSameUser = False
    isEdit = False
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
        self.label_stu_qna_num.setVisible(False)
        self.label_tea_qna_num.setVisible(False)

        self.btn_main_to_login.clicked.connect(self.go_login)
        self.btn_main_to_sign_in.clicked.connect(self.go_sign_in)

        self.btn_stu_list_to_add.clicked.connect(self.go_add_question)

        self.btn_login.clicked.connect(self.login)

        self.btn_sign_in.clicked.connect(self.sign_in)
        self.btn_id_check.clicked.connect(self.check_id)
        self.input_sign_in_id.textChanged.connect(self.id_changed)
        self.input_sign_in_pw.textChanged.connect(self.pw_changed)
        self.input_sign_in_pw_ck.textChanged.connect(self.pw_changed)
        self.radio_sign_in_student.clicked.connect(self.set_auth)
        self.radio_sign_in_teacher.clicked.connect(self.set_auth)

        self.tab_student.currentChanged.connect(self.tab_changed)
        self.tab_teacher.currentChanged.connect(self.tab_changed)

        self.table_stu_qna.doubleClicked.connect(self.view_qna_detail)
        self.table_tea_qna.doubleClicked.connect(self.view_qna_detail)

        self.btn_stu_qna_add.clicked.connect(self.add_question)

        self.btn_stu_detail_edit.clicked.connect(self.edit_question)

        self.btn_tea_answer_save.clicked.connect(self.answer)

        self.btn_stu_detail_delete.clicked.connect(self.delete_question)
        self.btn_tea_qna_delete.clicked.connect(self.delete_question)

    def go_login(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_sign_in(self):
        self.stackedWidget.setCurrentIndex(2)

    def go_add_question(self):
        self.stack_stu_qna.setCurrentWidget(self.stack_stu_add_question)

    def tab_changed(self):
        self.stack_stu_qna.setCurrentWidget(self.stack_stu_qna_list)
        self.stack_tea_qna.setCurrentWidget(self.stack_tea_qna_list)
        tab_student = self.tab_student.currentWidget()
        tab_teacher = self.tab_teacher.currentWidget()
        if tab_student == self.tab_stu_qna or tab_teacher == self.tab_tea_qna:
            print('tab_qna')
            self.load_qna()
        if tab_student == self.tab_stu_point:
            print('tab_point')
            self.load_point()

    def load_qna(self):
        self.table_stu_qna.setRowCount(0)
        self.table_tea_qna.setRowCount(0)
        self.thread.send_load_table(self.login_user.num)

    def view_qna_detail(self):
        self.text_stu_qna_answer.clear()
        self.text_stu_qna_content.clear()
        self.text_tea_qna_content.clear()
        self.text_tea_qna_answer.clear()

        sender = self.sender()
        row = sender.currentIndex().row()
        sel_data = sender.item(row, 0).text()
        self.thread.send_qna_detail(sel_data)
        time.sleep(0.05)

        if self.isSameUser:
            self.text_stu_qna_title.setReadOnly(False)
            self.text_stu_qna_content.setReadOnly(False)
            self.group_stu_qna_editable.setVisible(True)
        else:
            self.text_stu_qna_title.setReadOnly(True)
            self.text_stu_qna_content.setReadOnly(True)
            self.group_stu_qna_editable.setVisible(False)

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
        if 0 in [len(self.input_sign_in_id.text()), len(self.input_sign_in_pw.text()),
                 len(self.input_sign_in_pw_ck.text()), len(self.input_sign_in_name.text())] or self.auth is None:
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

    def add_question(self):
        title = self.input_stu_qna_title.text()
        content = self.input_stu_qna_content.toPlainText()
        add_time = datetime.now().strftime('%F %T')
        print(add_time)
        if 0 in [len(title), len(content)]:
            QMessageBox.warning(self, '경고', '제목 또는 내용을 확인해주세요')
        else:
            self.thread.send_add_question(self.login_user.num, title, content, add_time)

    def edit_question(self):
        qna_num = self.label_stu_qna_num.text()
        title = self.text_stu_qna_title.text()
        content = self.text_stu_qna_content.toPlainText()
        edit_time = datetime.now().strftime('%F %T')
        print(edit_time)
        if 0 in [len(title), len(content)]:
            QMessageBox.warning(self, '경고', '제목 또는 내용을 확인해주세요')
        else:
            self.thread.send_edit_question(qna_num, title, content, edit_time)

    def delete_question(self):
        if self.login_user.auth == 's':
            qna_num = self.label_stu_qna_num.text()
        else:
            qna_num = self.label_tea_qna_num.text()
        answer = QMessageBox.question(self, '확인', '해당 문의를 삭제하시겠습니까?')
        if answer == QMessageBox.Yes:
            self.thread.send_delete_question(qna_num)

    def answer(self):
        qna_num = self.label_tea_qna_num.text()
        member_num = self.login_user.num
        answer = self.text_tea_qna_answer.toPlainText()
        if len(self.text_tea_qna_answer.toPlainText()) == 0:
            QMessageBox.warning(self, '경고', '내용을 확인해주세요')
        else:
            self.thread.send_answer(qna_num, member_num, answer)

    def load_point(self):
        self.table_stu_quiz_result.setRowCount(0)
        self.thread.send_point_grade(self.login_user.num)
        self.thread.send_load_quiz_score(self.login_user.num)
        time.sleep(0.05)
        self.table_stu_quiz_result.setColumnWidth(0, 100)
        self.table_stu_quiz_result.setColumnWidth(1, 100)
        self.table_stu_quiz_result.setColumnWidth(2, 60)
        self.table_stu_quiz_result.setColumnWidth(3, 60)
        self.table_stu_quiz_result.setColumnWidth(4, 60)
        self.table_stu_quiz_result.setColumnWidth(5, 60)
        self.table_stu_quiz_result.setColumnWidth(6, 60)
        self.table_stu_quiz_result.setColumnWidth(7, 60)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
