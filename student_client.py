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

form_class = uic.loadUiType("main.ui")[0]


class User:
    def __init__(self, info):  # 유저가 로그인 시 클라이언트에 로그인 중인 유저 정보 저장
        self.num = info[0]
        self.uid = info[1]
        self.upw = info[2]
        self.uname = info[3]
        self.type = info[4]


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
            """ 예시
            if dic_data['method'] == 'check_id_result':
                print(dic_data['result'])
                if dic_data['result']:
                    self.form.label_regist_id.setText('사용 가능한 아이디입니다')
                    self.form.isIDChecked = True
                else:
                    self.form.label_regist_id.setText('이미 사용 중인 아이디입니다')
                    self.form.isIDChecked = False
            """

    # 여기서부터 def send_기능명(self, 매개변수): 이런 식으로 기능별 서버로 데이터 전송하는 코드 작성
    """ 예시
    def send_check_id(self, input_id):
        data = {"method": 'check_id', "input_id": input_id, "result": bool()}
        print(data['method'])
        json_data = json.dumps(data)
        self.client_socket.sendall(json_data.encode())
    """


class WindowClass(QMainWindow, form_class):
    login_user = None
    isIDChecked = False
    isPWRuleChecked = False
    isPWSameChecked = False

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.thread = ThreadClass(self)  # 스레드에 GUI 같이 넘겨주기


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
