import sys
import time
from socket import *
from threading import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtGui
from os import environ
import json
import requests
import xmltodict
from bs4 import BeautifulSoup
from tkinter import *
import urllib.request
from PyQt5.QtGui import QPixmap
import datetime
import random

# import socket
from threading import Thread
from datetime import datetime
from PyQt5.QtGui import QRegExpValidator

form_class = uic.loadUiType("edu.ui")[0]


class User:
    def __init__(self, info):  # 유저가 로그인 시 클라이언트에 로그인 중인 유저 정보 저장
        self.num = info[0]
        self.uid = info[1]
        self.upw = info[2]
        self.uname = info[3]
        self.auth = info[4]


class Main(QMainWindow, form_class):
    Client_socket = None

    ####### 가미 시작
    login_user = None
    isIDChecked = False
    isPWRuleChecked = False
    isPWSameChecked = False
    isSameUser = False
    isEdit = False
    auth = None

    ########## 가미 끝

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

        # self.show_teacher_topic()
        # self.show_teacher_score()

        self.a_btn.clicked.connect(self.show_teacher_topic)
        self.b_btn.clicked.connect(self.show_teacher_score)
        self.c_btn.clicked.connect(self.teacher_learning_view)

        self.show_bird_list()

        self.bird_list.itemClicked.connect(self.show_bird_contents)

        self.user_id = '이현도'
        self.learning_complete_btn.clicked.connect(self.learning_complete)

        self.teacher_learning_view()
        self.student_learning_view()

        ########## 가미 시작
        # self.thread = ThreadClass(self)  # 스레드에 GUI 같이 넘겨주기

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
        ########### 가미 끝

        ######## 연재 시작
        self.quiz_name_btn.clicked.connect(self.quizname)
        self.quiz_name_tablewidget.cellDoubleClicked.connect(self.click_quizname)
        self.quiz_insert_btn.clicked.connect(self.answer_index)
        self.o_x_list = []
        self.teacher_index_btn.clicked.connect(self.cb_pro)
        self.student_send_btn.clicked.connect(self.send_message_to_server)
        self.teacher_combobox.activated[str].connect(lambda: self.pro_name_click(self.teacher_combobox))
        self.find_stu_btn.clicked.connect(self.student_name_find)
        self.stu_name_index_tablewidget.cellClicked.connect(self.name_click_content)
        ######### 연재 끝

    ####################연재 시작

    def quizname(self):
        btn = self.sender()
        topic = btn.text()
        data = {'method': '!!!', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def click_quizname(self):
        topic = self.quiz_name_tablewidget.currentItem().text()
        data = {'method': '@@@', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        self.student_quiz_1.clear()
        self.student_quiz_2.clear()
        self.student_quiz_3.clear()
        self.student_quiz_4.clear()
        self.student_quiz_5.clear()

    def answer_index(self):
        print("opopopopopop")
        print(self.answer_list)
        print(self.answer_list[0])
        print(self.answer_list[1])
        for i in range(len(self.answer_list)):
            self.stu_answer_temp = eval("self.student_quiz_answer_edit_" + str(i) + ".text()")
            print(self.stu_answer_temp)
            if self.answer_list[i] == self.stu_answer_temp:
                self.o_x_list.append('o')
                print("lllll")
            elif self.answer_list[i] != self.stu_answer_temp:
                print("mmmmmm")
                self.o_x_list.append('x')
        print(self.o_x_list)
        self.quiz_name_clicked = self.quiz_name_tablewidget.currentItem().text()
        self.o_x_list.append(self.quiz_name_clicked)
        print(self.o_x_list)
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.o_x_list.append(time)
        print(self.o_x_list)
        o_count = self.o_x_list.count('o')
        self.o_x_list.append(o_count)
        print(self.o_x_list)
        self.o_x_list.append(self.quiz_stu_name_lbl.text())
        print(self.o_x_list)
        topic = self.o_x_list
        data = {'method': '^^^', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        self.o_x_list.clear()
        print(self.o_x_list)
        self.student_quiz_answer_edit_0.clear()
        self.student_quiz_answer_edit_1.clear()
        self.student_quiz_answer_edit_2.clear()
        self.student_quiz_answer_edit_3.clear()
        self.student_quiz_answer_edit_4.clear()

    def cb_pro(self):
        topic = self.teacher_combobox.itemText(0)
        data = {'method': '%%%', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def login_to_program(self):  # temp
        topic = self.login_id_edit.text()
        data = {'method': '^0^', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def pro_name_click(self, combobox):
        self.student_chat_view_list.clear()
        topic = self.teacher_combobox.currentText()
        data = {'method': '^*^*', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def send_message_to_server(self):
        print('sfsfsfsf```')
        self.line_send_list = []
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        a = self.student_text_edit.text()
        b = self.chat_name_lbl.text()
        c = self.teacher_combobox.currentText()
        self.line_send_list.append(time)
        self.line_send_list.append(b)
        self.line_send_list.append(a)
        self.line_send_list.append(c)
        print('sfsfsfsf```')
        print(self.line_send_list)
        topic = self.line_send_list
        data = {'method': '#$#$', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    # -----------------------교사 채팅--------------------------------------------
    def student_name_find(self):
        btn = self.sender()
        topic = btn.text()
        data = {'method': '(**', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def name_click_content(self):
        self.teacher_chat_view_list.clear()
        topic = self.stu_name_index_tablewidget.currentItem().text()
        data = {'method': '<><>', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def text_to_stud(self):
        print('여기도 다시 확인')
        self.line_send_list_tc = []
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        a = self.teacher_text_edit.text()
        b = self.tc_chat_name_lbl.text()
        c = self.stu_name_index_tablewidget.currentItem().text()
        self.line_send_list_tc.append(time)
        self.line_send_list_tc.append(b)
        self.line_send_list_tc.append(a)
        self.line_send_list_tc.append(c)
        print(self.line_send_list_tc)
        topic = self.line_send_list_tc
        data = {'method': '*()*()', 'text': topic}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    ############ 연재 끝

    ############# 가미 시작
    def go_login(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_sign_in(self):
        self.stackedWidget.setCurrentIndex(2)

    def go_add_question(self):
        self.stack_stu_qna.setCurrentWidget(self.stack_stu_add_question)

    def tab_changed(self):
        print("a")
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
        self.send_load_table(self.login_user.num)

    def view_qna_detail(self):
        self.text_stu_qna_answer.clear()
        self.text_stu_qna_content.clear()
        self.text_tea_qna_content.clear()
        self.text_tea_qna_answer.clear()

        sender = self.sender()
        row = sender.currentIndex().row()
        sel_data = sender.item(row, 0).text()
        self.send_qna_detail(sel_data)
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
        self.send_login(input_id, input_pw)
        time.sleep(0.5)
        # if self.login_user is not None:
        #     QMessageBox.information(self, '알림', '로그인 되었습니다')
        #     if self.login_user.auth == 's':
        #         self.stackedWidget.setCurrentIndex(4)
        #     else:
        #         self.stackedWidget.setCurrentIndex(3)
        # else:
        #     print('no')

    def check_id(self):
        self.send_check_id(self.input_sign_in_id.text())

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
                 len(self.input_sign_in_pw_ck.text()),
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
            self.send_registration(input_id, input_pw, input_name, input_auth)

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
            self.send_add_question(self.login_user.num, title, content, add_time)

    def edit_question(self):
        qna_num = self.label_stu_qna_num.text()
        title = self.text_stu_qna_title.text()
        content = self.text_stu_qna_content.toPlainText()
        edit_time = datetime.now().strftime('%F %T')
        print(edit_time)
        if 0 in [len(title), len(content)]:
            QMessageBox.warning(self, '경고', '제목 또는 내용을 확인해주세요')
        else:
            self.send_edit_question(qna_num, title, content, edit_time)

    def delete_question(self):
        if self.login_user.auth == 's':
            qna_num = self.label_stu_qna_num.text()
        else:
            qna_num = self.label_tea_qna_num.text()
        answer = QMessageBox.question(self, '확인', '해당 문의를 삭제하시겠습니까?')
        if answer == QMessageBox.Yes:
            self.send_delete_question(qna_num)

    def answer(self):
        qna_num = self.label_tea_qna_num.text()
        member_num = self.login_user.num
        answer = self.text_tea_qna_answer.toPlainText()
        if len(self.text_tea_qna_answer.toPlainText()) == 0:
            QMessageBox.warning(self, '경고', '내용을 확인해주세요')
        else:
            self.send_answer(qna_num, member_num, answer)

    def load_point(self):
        self.table_stu_quiz_result.setRowCount(0)
        self.send_point_grade(self.login_user.num)
        self.send_load_quiz_score(self.login_user.num)
        time.sleep(0.05)
        self.table_stu_quiz_result.setColumnWidth(0, 100)
        self.table_stu_quiz_result.setColumnWidth(1, 100)
        self.table_stu_quiz_result.setColumnWidth(2, 60)
        self.table_stu_quiz_result.setColumnWidth(3, 60)
        self.table_stu_quiz_result.setColumnWidth(4, 60)
        self.table_stu_quiz_result.setColumnWidth(5, 60)
        self.table_stu_quiz_result.setColumnWidth(6, 60)
        self.table_stu_quiz_result.setColumnWidth(7, 60)

    ############# 가미 끝

    def student_learning_view(self):
        data = {'method': '009', 'user_id': self.user_id}
        print(data)
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def teacher_learning_view(self):
        data = {'method': '008'}
        print(data)
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def learning_complete(self):
        text = self.bird_list.selectedItems()
        text = text[0].text()
        data = {'method': '006', 'text': text, 'user_id': self.user_id}
        print(data)
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def show_bird_contents(self):
        text = self.bird_list.selectedItems()
        text = text[0].text()
        # print(text)
        #
        key = "NduHOhIXFSeGjCmd2mxVGcIDVRgR9ooMiRLXcDTwFxBuenEsZEtIsxYy43lSSDxGyn0OsPpOQ8as3Yffw37wbg%3D%3D"

        url = f'http://apis.data.go.kr/1400119/BirdService/birdSpcmSearch?serviceKey={key}&st=3&sw={text}&numOfRows=15000&pageNo=1'
        content = requests.get(url).content  # request 모듈을 이용해서 정보 가져오기(byte형태로 가져와지는듯)
        dict = xmltodict.parse(content)  # xmltodict 모듈을 이용해서 딕셔너리화 & 한글화
        jsonString = json.dumps(dict, ensure_ascii=False)  # json.dumps를 이용해서 문자열화(데이터를 보낼때 이렇게 바꿔주면 될듯)
        jsonObj = json.loads(jsonString)  # 데이터 불러올 때(딕셔너리 형태로 받아옴)

        try:
            knam = jsonObj['response']['body']['items']['item']['anmlSmplNo']
            # print(knam)
        except:
            # print("a")
            knam = jsonObj['response']['body']['items']['item'][0]['anmlSmplNo']
            # print(knam)

        url = f'http://apis.data.go.kr/1400119/BirdService/birdSpcmInfo?serviceKey={key}&q1={knam}'
        content = requests.get(url).content  # request 모듈을 이용해서 정보 가져오기(byte형태로 가져와지는듯)
        dict = xmltodict.parse(content)  # xmltodict 모듈을 이용해서 딕셔너리화 & 한글화
        jsonString = json.dumps(dict, ensure_ascii=False)  # json.dumps를 이용해서 문자열화(데이터를 보낼때 이렇게 바꿔주면 될듯)
        jsonObj = json.loads(jsonString)  # 데이터 불러올 때(딕셔너리 형태로 받아옴)

        anmlSpecsId = jsonObj['response']['body']['item']['anmlSpecsId']

        #
        url = f'http://apis.data.go.kr/1400119/BirdService/birdIlstrInfo?serviceKey={key}&q1={anmlSpecsId}'
        content = requests.get(url).content  # request 모듈을 이용해서 정보 가져오기(byte형태로 가져와지는듯)
        dict = xmltodict.parse(content)  # xmltodict 모듈을 이용해서 딕셔너리화 & 한글화
        jsonString = json.dumps(dict, ensure_ascii=False)  # json.dumps를 이용해서 문자열화(데이터를 보낼때 이렇게 바꿔주면 될듯)
        jsonObj = json.loads(jsonString)  # 데이터 불러올 때(딕셔너리 형태로 받아옴)

        self.eclgDpftrCont_brower.clear()
        self.gnrlSpftrCont_brower.clear()

        self.eclgDpftrCont_brower.append(jsonObj['response']['body']['item']['eclgDpftrCont'])
        self.gnrlSpftrCont_brower.append(jsonObj['response']['body']['item']['gnrlSpftrCont'])

        img_url = jsonObj['response']['body']['item']['imgUrl']

        imageFromWeb = urllib.request.urlopen(img_url).read()
        qPixmapVar = QPixmap()
        qPixmapVar.loadFromData(imageFromWeb)
        qPixmapVar = qPixmapVar.scaled(self.image_url_label.width(), self.image_url_label.height(), Qt.KeepAspectRatio,
                                       Qt.SmoothTransformation)
        self.image_url_label.setPixmap(qPixmapVar)

    def show_bird_list(self):
        self.bird_list.clear()
        key = "NduHOhIXFSeGjCmd2mxVGcIDVRgR9ooMiRLXcDTwFxBuenEsZEtIsxYy43lSSDxGyn0OsPpOQ8as3Yffw37wbg%3D%3D"
        url = f'http://apis.data.go.kr/1400119/BirdService/birdSpcmSearch?serviceKey={key}&st=1&sw=&numOfRows=5000&pageNo=1'

        content = requests.get(url).content  # request 모듈을 이용해서 정보 가져오기(byte형태로 가져와지는듯)
        dict = xmltodict.parse(content)  # xmltodict 모듈을 이용해서 딕셔너리화 & 한글화
        jsonString = json.dumps(dict, ensure_ascii=False)  # json.dumps를 이용해서 문자열화(데이터를 보낼때 이렇게 바꿔주면 될듯)
        jsonObj = json.loads(jsonString)  # 데이터 불러올 때(딕셔너리 형태로 받아옴)

        animal_name_list = []
        for item in jsonObj['response']['body']['items']['item']:
            animal_name_list.append(item['anmlGnrlNm'])
        # print(animal_name_list)
        animal_list = set(animal_name_list)
        for x in sorted(animal_list):
            self.bird_list.addItem(x)

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
        self.teacher_quiz_send_label.setText("")
        data = {'method': '003'}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

    def teacher_quiz_send(self):
        quiz = []
        quiz_list = [self.teacher_quiz_title_edit.text(), self.teacher_quiz_edit1.text(),
                     self.teacher_quiz_edit2.text(), self.teacher_quiz_edit3.text(), self.teacher_quiz_edit4.text(),
                     self.teacher_quiz_edit5.text(), self.teacher_quiz_answer_edit1.text(),
                     self.teacher_quiz_answer_edit2.text(), self.teacher_quiz_answer_edit3.text(),
                     self.teacher_quiz_answer_edit4.text(), self.teacher_quiz_answer_edit5.text()]

        for x in quiz_list:
            quiz.append(x)
        data = {'method': '002', 'text': quiz}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())

        self.teacher_quiz_title_edit.clear()
        self.teacher_quiz_edit1.clear()
        self.teacher_quiz_edit2.clear()
        self.teacher_quiz_edit3.clear()
        self.teacher_quiz_edit4.clear()
        self.teacher_quiz_edit5.clear()
        self.teacher_quiz_answer_edit1.clear()
        self.teacher_quiz_answer_edit2.clear()
        self.teacher_quiz_answer_edit3.clear()
        self.teacher_quiz_answer_edit4.clear()
        self.teacher_quiz_answer_edit5.clear()
        self.teacher_quiz_send_label.setText("제출완료")

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

    ################ 가미 시작
    def send_check_id(self, input_id):
        data = {"method": 'check_id', "input_id": input_id, "result": bool()}
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
        print('send:', data['method'])

    def send_login(self, uid, upw):
        print("a")
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
        data = {"method": 'edit_question', "qna_num": qna_num, "title": title, "content": content,
                "edit_time": edit_time}
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

    ################ 가미 끝

    def initialize_socket(self, ip, port):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        remote_ip = ip
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))

    def listen_thread(self):
        t = Thread(target=self.receive_message, args=(self.client_socket,))
        t.start()

    def receive_message(self, so):
        while True:
            try:
                data = self.client_socket.recv(9999)
                dic_data = json.loads(data.decode())
                print("abc")
                print(dic_data)
            except:
                break
            else:
                # if not buf: #연결 종료 됨
                #     break
                if dic_data['method'] == '001':
                    print(dic_data['text'])
                    self.teacher_chat_view_list.addItem(dic_data['text'])
                    self.student_chat_view_list.addItem(dic_data['text'])
                if dic_data['method'] == '002':
                    print("b")
                if dic_data['method'] == '003':
                    self.teacher_quiz_title_list.clear()

                    for x in dic_data['text']:
                        self.teacher_quiz_title_list.addItem(x[0])
                if dic_data['method'] == '004':
                    for x in dic_data['text']:
                        self.teacher_quiz_list.addItem(x[0])
                if dic_data['method'] == '005':
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
                if dic_data['method'] == '006':
                    print(dic_data)
                    if dic_data['text'] == 0:
                        text = self.bird_list.selectedItems()
                        text = text[0].text()
                        data = {'method': '007', 'text': text, 'user_id': self.user_id}
                        print(data)
                        json_data = json.dumps(data)
                        self.client_socket.sendall(json_data.encode())
                        self.learning_complete_label.setText("\'" + text + "\' 학습 완료")
                    else:
                        text = self.bird_list.selectedItems()
                        text = text[0].text()
                        self.learning_complete_label.setText("\'" + text + "\' 학습 완료 상태입니다.")
                if dic_data['method'] == '008':
                    self.teacher_learning_list.clear()
                    text = dic_data['text']
                    for x in text:
                        self.teacher_learning_list.addItem(str(x[0]) + ": " + str(x[1]))
                if dic_data['method'] == '009':
                    self.student_learning_list.clear()
                    text = dic_data['text']
                    for x in text:
                        self.student_learning_list.addItem(str(x[1]))

                ###############가미 시작
                if dic_data['method'] == 'check_id_result':
                    print('recv:', dic_data['method'])
                    if dic_data['result']:
                        self.label_id_check.setVisible(False)
                        self.btn_id_check.setEnabled(False)
                        self.isIDChecked = True
                    else:
                        self.label_id_check.setVisible(True)
                        self.isIDChecked = False

                if dic_data['method'] == 'login_result':
                    print("123")
                    print('recv:', dic_data['method'])
                    if dic_data['method']:
                        self.login_user = User(dic_data['login_info'])
                        print('uid:', self.login_user.uid)

                    if self.login_user is not None:
                        self.input_login_id
                        # QMessageBox.information(self, '알림', '로그인 되었습니다')
                        if self.login_user.auth == 's':
                            self.stackedWidget.setCurrentIndex(4)
                            self.lg_temp_c = self.login_user.uid
                            self.chat_name_lbl.setText(self.login_user.uid)  # 학생 채팅 페이지 라벨
                            self.quiz_stu_name_lbl.setText(self.login_user.uid)  # 학생 퀴즈 페이지 라벨
                            self.index_name_stu_lbl.setText(self.login_user.uid)  # 학생 퀴즈 결과 등급 페이지 라벨


                        else:
                            self.lg_temp_c = self.login_user.uid
                            self.tc_chat_name_lbl.setText(self.login_user.uid)
                            self.stackedWidget.setCurrentIndex(3)
                    else:
                        print('no')

                if dic_data['method'] == 'registration_result':
                    print('recv:', dic_data['method'])
                    if dic_data['result']:
                        self.stackedWidget.setCurrentIndex(0)
                    else:
                        print("1")
                        print('no')

                if dic_data['method'] == 'load_table_result':
                    print('recv:', dic_data['method'])
                    print('recv_data:', dic_data['data'])
                    row_num = dic_data['index']
                    if self.login_user.auth == 's':
                        qna_table = self.table_stu_qna
                    else:
                        qna_table = self.table_tea_qna
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

                    if self.login_user.auth == 's':

                        if self.login_user.num == dic_data['result'][1]:
                            self.isSameUser = True
                        else:
                            self.isSameUser = False

                        data_list = [self.text_stu_qna_title, self.text_stu_qna_content,
                                     self.label_stu_qna_stu_name, self.label_stu_qna_stu_id,
                                     self.label_stu_qna_add_time, self.label_stu_qna_edit_time,
                                     self.label_stu_qna_tea_name, self.label_stu_qna_tea_id,
                                     self.text_stu_qna_answer, self.label_stu_qna_num]
                    else:
                        data_list = [self.text_tea_qna_title, self.text_tea_qna_content,
                                     self.label_tea_qna_stu_name, self.label_tea_qna_stu_id,
                                     self.label_tea_qna_add_time, self.label_tea_qna_edit_time,
                                     self.label_tea_qna_tea_name, self.label_tea_qna_tea_id,
                                     self.text_tea_qna_answer, self.label_tea_qna_num]

                    data_list[0].setText(dic_data['result'][4])
                    data_list[1].append(dic_data['result'][5])
                    data_list[2].setText(dic_data['result'][3])
                    data_list[3].setText("(" + dic_data['result'][2] + ")")
                    data_list[4].setText(dic_data['result'][9])
                    data_list[5].setText(dic_data['result'][10])
                    data_list[6].setText(dic_data['result'][7])
                    if dic_data['result'][6] is not None:
                        data_list[7].setText("(" + dic_data['result'][6] + ")")
                    else:
                        data_list[7].clear()
                    data_list[8].append(dic_data['result'][8])
                    data_list[9].setText(str(dic_data['result'][0]))

                if dic_data['method'] == 'add_question_result':
                    print('recv:', dic_data['method'])
                    print('result:', dic_data['result'])
                    self.stack_stu_qna.setCurrentWidget(self.stack_stu_qna_list)
                    self.load_qna()

                if dic_data['method'] == 'edit_question_result':
                    print('recv:', dic_data['method'])
                    print('result:', dic_data['result'])
                    self.stack_stu_qna.setCurrentWidget(self.stack_stu_qna_list)
                    self.load_qna()

                if dic_data['method'] == 'delete_question_result':
                    print('recv:', dic_data['method'])
                    print('result:', dic_data['result'])
                    if self.login_user.auth == 's':
                        self.stack_stu_qna.setCurrentWidget(self.stack_stu_qna_list)
                    else:
                        self.stack_tea_qna.setCurrentWidget(self.stack_tea_qna_list)
                    self.load_qna()

                if dic_data['method'] == 'answer_result':
                    print('recv:', dic_data['method'])
                    print('result:', dic_data['result'])
                    self.stack_tea_qna.setCurrentWidget(self.stack_tea_qna_list)
                    self.load_qna()

                if dic_data['method'] == 'point_grade_result':
                    print('recv:', dic_data['method'])
                    print('point:', dic_data['point'], 'grade:', dic_data['grade'])
                    # print('max_point:', dic_data['max_point'])
                    self.label_stu_point.setText(str(dic_data['point']))
                    self.index_name_stu_lbl.setText(self.login_user.uname)
                    self.label_stu_grade.setText(dic_data['grade'])

                if dic_data['method'] == 'load_quiz_score_result':
                    print('recv:', dic_data['method'])
                    print('recv_data:', dic_data['data'])
                    table = self.table_stu_quiz_result
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
                    table.setItem(row_num, 2, QTableWidgetItem(str(dic_data['data'][8]) + ' / ' + str(question_num)))

                ########## 가미 끝

                ########## 연재 시작
                if dic_data['method'] == '!!!':
                    print("qqqqqqqqqq")
                    print(dic_data['text'])
                    self.quizname_index = dic_data['text']
                    self.quiz_name_tablewidget.setRowCount(len(self.quizname_index))
                    self.quiz_name_tablewidget.setColumnCount(1)
                    for i in range(len(self.quizname_index)):
                        self.quiz_name_tablewidget.setItem(i, 0, QTableWidgetItem(str(self.quizname_index[i][0])))

                if dic_data['method'] == '@@@':
                    print("gggggggg")
                    # quizcontent_remove = recv_data.replace("@@@", "")
                    self.quizcontent_index = dic_data['text']
                    print(self.quizcontent_index)
                    print("()()()()")
                    print(type(self.quizcontent_index))
                    self.answer_list = list(self.quizcontent_index.keys())
                    print(self.answer_list)
                    self.content_list = list(self.quizcontent_index.values())
                    print(self.content_list)
                    print("KKKK")
                    if len(self.quizcontent_index) == 1:
                        self.student_quiz_1.append(f"{self.content_list[0]}")
                    elif len(self.quizcontent_index) == 2:
                        self.student_quiz_1.append(f"{self.content_list[0]}")
                        self.student_quiz_2.append(f"{self.content_list[1]}")
                    elif len(self.quizcontent_index) == 3:
                        self.student_quiz_1.append(f"{self.content_list[0]}")
                        self.student_quiz_2.append(f"{self.content_list[1]}")
                        self.student_quiz_3.append(f"{self.content_list[2]}")
                    elif len(self.quizcontent_index) == 4:
                        self.student_quiz_1.append(f"{self.content_list[0]}")
                        self.student_quiz_2.append(f"{self.content_list[1]}")
                        self.student_quiz_3.append(f"{self.content_list[2]}")
                        self.student_quiz_4.append(f"{self.content_list[3]}")
                    elif len(self.quizcontent_index) >= 5:
                        print("GHKGFHK")
                        self.student_quiz_1.append(f"{self.content_list[0]}")
                        self.student_quiz_2.append(f"{self.content_list[1]}")
                        self.student_quiz_3.append(f"{self.content_list[2]}")
                        self.student_quiz_4.append(f"{self.content_list[3]}")
                        self.student_quiz_5.append(f"{self.content_list[4]}")

                if dic_data['method'] == '%%%':
                    print("클라콤보")
                    t_cb = dic_data['text']
                    self.t_cb_temp = t_cb
                    for i in range(len(self.t_cb_temp)):
                        self.teacher_combobox.addItems(self.t_cb_temp[i])

                if dic_data['method'] == '^0^':  # temp
                    print("임시로그인클라")
                    lg_temp = dic_data['text']
                    self.lg_temp_c = lg_temp
                    print(self.lg_temp_c)  ## 로그인 이름, auth 담겨 있는 이중리스트

                    if self.lg_temp_c[0][1] == 's':  # temp
                        self.stackedWidget.setCurrentIndex(4)
                        print("이현도")
                        self.chat_name_lbl.setText(f"{self.lg_temp_c[0][0]}")  # 학생 채팅 페이지 라벨
                        self.quiz_stu_name_lbl.setText(f"{self.lg_temp_c[0][0]}")  # 학생 퀴즈 페이지 라벨
                        self.index_name_stu_lbl.setText(f"{self.lg_temp_c[0][0]}")  # 학생 퀴즈 결과 등급 페이지 라벨
                    elif self.lg_temp_c[0][1] == 't':
                        self.stackedWidget.setCurrentIndex(3)
                        self.tc_chat_name_lbl.setText(f"{self.lg_temp_c[0][0]}")

                if dic_data['method'] == '^*^*':
                    print("리스트위젯에 채팅 내용 띄우기")
                    message_temp = dic_data['text']
                    self.message_to_widget = message_temp
                    print(self.message_to_widget)
                    self.message_to_widget.reverse()

                    for i in range(len(self.message_to_widget)):
                        if self.teacher_combobox.currentText() == self.message_to_widget[i][
                            2] or self.teacher_combobox.currentText() == self.message_to_widget[i][4]:
                            self.student_chat_view_list.insertItem(i,
                                                                   f"{self.message_to_widget[i][6]}   {self.message_to_widget[i][2]} : {self.message_to_widget[i][5]}")

                        else:
                            self.student_chat_view_list.clear()

                if dic_data['method'] == '#$#$':
                    print("리스트위젯에 내가 쓴 글 인설트 하기")
                    line_message_temp = dic_data['text']
                    self.line_message_to_widget = line_message_temp
                    print(self.line_message_to_widget)
                    self.student_chat_view_list.addItem(
                        f"{self.line_message_to_widget[0]}  {self.line_message_to_widget[1]}:{self.line_message_to_widget[2]}")
                    self.student_text_edit.clear()
                    if self.line_message_to_widget[3] == self.tc_chat_name_lbl.text():
                        self.teacher_chat_view_list.addItem(
                            f"{self.line_message_to_widget[0]}  {self.line_message_to_widget[1]}:{self.line_message_to_widget[2]}")
                    else:
                        pass
                # ------------------- 교사 채팅 ---------------------------------------------------------

                if dic_data['method'] == '(**':
                    print("테이블위젯에 학생 이름 띄우기")
                    stu_name_for_temp = dic_data['text']
                    self.stu_name_for_tc = stu_name_for_temp
                    print(self.stu_name_for_tc)
                    for i in range(len(self.stu_name_for_tc)):
                        self.stu_name_index_tablewidget.setRowCount(len(self.stu_name_for_tc[i][0]))
                        self.stu_name_index_tablewidget.setColumnCount(1)
                        for j in range(len(self.stu_name_for_tc[i])):
                            self.stu_name_index_tablewidget.setItem(i, j,
                                                                    QTableWidgetItem(str(self.stu_name_for_tc[i][j])))

                if dic_data['method'] == '<><>':
                    print("지난 채팅 내용 가져오기")
                    stu_record_temp = dic_data['text']
                    self.stu_record_temp1 = stu_record_temp
                    print(self.stu_record_temp1)
                    for i in range(len(self.stu_record_temp1)):
                        self.teacher_chat_view_list.insertItem(i,
                                                               f"{self.stu_record_temp1[i][6]}   {self.stu_record_temp1[i][4]}:{self.stu_record_temp1[i][5]}")

                if dic_data['method'] == '*()*()':
                    print("리스트위젯에 내가 쓴 글 인설트 하기2")
                    line_message_temp2 = dic_data['text']
                    self.line_message_to_widget2 = line_message_temp2
                    print('sdfsdf' + f"{self.line_message_to_widget2}")
                    self.teacher_chat_view_list.addItem(
                        f"{self.line_message_to_widget2[0]}  {self.line_message_to_widget2[1]}:{self.line_message_to_widget2[2]}")
                    self.teacher_text_edit.clear()
                    if self.line_message_to_widget2[3] == self.chat_name_lbl.text():
                        self.student_chat_view_list.addItem(
                            f"{self.line_message_to_widget2[0]}  {self.line_message_to_widget2[1]}:{self.line_message_to_widget2[2]}")
                    else:
                        pass

            ############# 연재 끝

        so.close()


if __name__ == "__main__":
    ip = '10.10.21.114'
    port = 55000

    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCREEN_FACTOR"] = "1"

    app = QApplication(sys.argv)
    mainWindow = Main(ip, port)
    mainWindow.show()
    app.exec_()
