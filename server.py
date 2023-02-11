import socketserver
import pymysql

import json

import socket
import time
from _thread import *
from datetime import datetime

# client_sockets = list()

HOST = '127.0.0.1'
PORT = 9000
DB_HOST = '10.10.21.116'
DB_USER = 'eduapp_admin'
DB_PASSWORD = 'admin1234'

host_str = '10.10.21.116'
user_str = 'eduapp_admin'
password_str = 'admin1234'


def conn_fetch():  # SELECT문 사용 시
    con = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db='eduapp', charset='utf8')
    cur = con.cursor()
    return cur


def conn_commit():  # INSERT, UPDATE 등 값에 변화를 주는 SQL문 사용 시
    con = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db='eduapp', charset='utf8')
    return con


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        (ip, port) = self.client_address
        client = self.request, (ip, port)
        if client not in Multi_server.clients:
            Multi_server.clients.append(client)
        print(ip, ":", str(port), '가 연결되었습니다.')
        Multi_server.receive_messages(self.request)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MultiChatServer:
    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []
        self.final_received_message = ""  # 최종 수신 메시지

    # 데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages(self, c_socket):
        while True:
            try:
                data = c_socket.recv(9999)
                dic_data = json.loads(data.decode())
                print(dic_data)
                if not data:  # 연결이 종료됨
                    break
            except:
                continue
            else:
                # self.final_received_message = incoming_message.decode('utf-8')

                ###########################현도 시작
                if dic_data['method'] == '001':
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        json_data = json.dumps(dic_data)
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == '002':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            for i in range(1, 6):
                                if dic_data['text'][i] != '':
                                    sql = f"INSERT INTO quiz(topic,content,answer) values('{dic_data['text'][0]}', '{dic_data['text'][i]}', '{dic_data['text'][i + 5]}')"
                                    cur.execute(sql)
                                    con.commit()
                    ###################################################### Data base 접속 end

                if dic_data['method'] == '003':
                    print("abc")
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"select distinct topic from quiz"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ###################################################### Data base 접속 end
                    data = {'method': '003', 'text': rows}
                    json_data = json.dumps(data)
                    print(rows)
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == '004':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"select content from quiz where topic = '{dic_data['text']}';"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ###################################################### Data base 접속 end

                    print(rows)
                    data = {'method': '004', 'text': rows}
                    json_data = json.dumps(data)
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == '005':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"SELECT * FROM quiz_result;"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ###################################################### Data base 접속 end
                    print(rows)
                    data = {'method': '005', 'text': rows}
                    print(data)
                    json_data = json.dumps(data)
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())
                if dic_data['method'] == '006':
                    print("a")
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"SELECT * FROM study where title = '{dic_data['text']}' and user_id = '{dic_data['user_id']}';"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ###################################################### Data base 접속 end
                    print(len(rows))
                    data = {'method': '006', 'text': len(rows)}
                    json_data = json.dumps(data)
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == '007':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"INSERT INTO study values('{dic_data['user_id']}','{dic_data['text']}')"
                            cur.execute(sql)
                            con.commit()
                    ###################################################### Data base 접속 end

                if dic_data['method'] == '008':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"SELECT * FROM study"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ###################################################### Data base 접속 end
                    data = {'method': '008', 'text': rows}
                    json_data = json.dumps(data)
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == '009':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp',
                                          charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            sql = f"SELECT * FROM study where user_id = '{dic_data['user_id']}'"
                            cur.execute(sql)
                            rows = cur.fetchall()
                    ###################################################### Data base 접속 end
                    data = {'method': '009', 'text': rows}
                    json_data = json.dumps(data)
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                ###########################현도 끝

                ###########################가미 시작
                if dic_data['method'] == 'check_id':
                    print(dic_data['method'], dic_data['input_id'])
                    dic_data['method'] = 'check_id_result'
                    sql = f"SELECT * FROM member WHERE uid = '{dic_data['input_id']}'"
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()
                        if len(result) == 0:
                            dic_data['result'] = True
                        else:
                            dic_data['result'] = False
                    json_data = json.dumps(dic_data)
                    # for client in self.clients:
                    #     socket, (ip, port) = client
                    c_socket.sendall(json_data.encode())

                if dic_data['method'] == 'login':
                    print(dic_data['method'], dic_data['uid'], dic_data['upw'])
                    dic_data['method'] = 'login_result'
                    sql = f"SELECT * FROM member WHERE uid = '{dic_data['uid']}' and upw = '{dic_data['upw']}'"
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()
                        print(result)
                        if len(result) == 0:
                            dic_data['result'] = False
                            print("a")
                        else:
                            print("b")
                            dic_data['result'] = True
                            dic_data['login_info'] = result[0]
                    print("abc")
                    print(dic_data)
                    json_data = json.dumps(dic_data)
                    # for client in self.clients:
                    #     socket, (ip, port) = client
                    c_socket.sendall(json_data.encode())

                if dic_data['method'] == 'registration':
                    print(dic_data['method'], dic_data['uid'], dic_data['upw'], dic_data['uname'], dic_data['auth'])
                    dic_data['method'] = 'registration_result'
                    sql = f"INSERT INTO member (uid, upw, uname, auth) VALUES " \
                          f"('{dic_data['uid']}', '{dic_data['upw']}', '{dic_data['uname']}', '{dic_data['auth']}')"
                    print(sql)
                    with conn_commit() as con:
                        with con.cursor() as cur:
                            cur.execute(sql)
                            con.commit()
                    dic_data['result'] = True

                    if dic_data['auth'] == 's':
                        sql = f"SELECT num FROM member WHERE uid = '{dic_data['uid']}' AND upw = '{dic_data['upw']}' " \
                              f"AND uname = '{dic_data['uname']}' AND auth = '{dic_data['auth']}'"
                        print(sql)
                        with conn_fetch() as cur:
                            cur.execute(sql)
                            num = cur.fetchall()[0][0]
                            print(num)
                        sql = f"INSERT INTO student (student_num) VALUES ({num})"
                        print(sql)
                        with conn_commit() as con:
                            with con.cursor() as cur:
                                cur.execute(sql)
                                con.commit()

                if dic_data['method'] == 'load_table':
                    print(dic_data['method'], dic_data['member_num'])
                    sql = "SELECT a.num, b.uname, a.title, a.teacher_num FROM qna a " \
                          "LEFT JOIN member b on a.student_num = b.num"
                    print(sql)
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()
                        print(result)
                        dic_data['method'] = 'load_table_result'
                        dic_data['result'] = result
                    # ##
                    # json_data = json.dumps(dic_data)
                    # for client in self.clients:
                    #     socket, (ip, port) = client
                    #     socket.sendall(json_data.encode())
                    # ##
                    result = dic_data['result']
                    del dic_data['result']
                    count = 0
                    for i in range(len(result)):
                        for client in self.clients:
                            dic_data['data'] = result[i]
                            dic_data['index'] = count
                            json_data = json.dumps(dic_data)
                            socket, (ip, port) = client
                            socket.sendall(json_data.encode())
                            time.sleep(0.05)
                            count += 1

                if dic_data['method'] == 'qna_detail':
                    print(dic_data['method'], dic_data['qna_num'])
                    # sql = f"SELECT * FROM qna WHERE num = {dic_data['qna_num']}"
                    sql = f"SELECT a.num, b.num, b.uid, b.uname, a.title, a.content, " \
                          f"c.uid, c.uname, a.answer, a.add_time, a.edit_time " \
                          f"FROM qna a " \
                          f"LEFT JOIN member b on a.student_num = b.num LEFT JOIN member c on a.teacher_num = c.num " \
                          f"WHERE a.num = {dic_data['qna_num']}"
                    print(sql)
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()
                        print(result)
                        dic_data['method'] = 'qna_detail_result'
                        dic_data['result'] = result[0]

                    json_data = json.dumps(dic_data)
                    for client in self.clients:
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == 'add_question':
                    print(dic_data['method'], dic_data['member_num'])
                    sql = f"INSERT INTO qna (student_num, title, content, add_time) VALUES " \
                          f"({dic_data['member_num']}, '{dic_data['title']}', '{dic_data['content']}', '{dic_data['add_time']}')"
                    print(sql)
                    with conn_commit() as con:
                        with con.cursor() as cur:
                            cur.execute(sql)
                            con.commit()
                            dic_data['method'] = 'add_question_result'
                            dic_data['result'] = True

                    json_data = json.dumps(dic_data)
                    for client in self.clients:
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == 'edit_question':
                    print(dic_data['method'], dic_data['qna_num'])
                    sql = f"SELECT title, content FROM qna WHERE num = {dic_data['qna_num']}"
                    print(sql)
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()

                    dic_data['method'] = 'edit_question_result'

                    if result[0][0] == dic_data['title'] and result[0][1] == dic_data['content']:
                        dic_data['result'] = False

                    else:
                        title = dic_data['title']
                        content = dic_data['content']
                        edit_time = dic_data['edit_time']
                        sql = f"UPDATE qna SET title = '{title}', content = '{content}', edit_time = '{edit_time}' " \
                              f"WHERE num = {dic_data['qna_num']}"
                        print(sql)
                        with conn_commit() as con:
                            with con.cursor() as cur:
                                cur.execute(sql)
                                con.commit()
                                dic_data['result'] = True

                    json_data = json.dumps(dic_data)
                    for client in self.clients:
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == 'delete_question':
                    sql = f"DELETE FROM qna WHERE num = {dic_data['qna_num']}"
                    print(sql)
                    with conn_commit() as con:
                        with con.cursor() as cur:
                            cur.execute(sql)
                            con.commit()
                            dic_data['method'] = 'delete_question_result'
                            dic_data['result'] = True

                    json_data = json.dumps(dic_data)
                    for client in self.clients:
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == 'answer':
                    sql = f"SELECT answer FROM qna WHERE num = {dic_data['qna_num']}"
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()

                    dic_data['method'] = 'answer_result'

                    if result[0][0] == dic_data['answer']:
                        dic_data['result'] = False

                    else:
                        sql = f"UPDATE qna SET teacher_num = {dic_data['member_num']}, answer = '{dic_data['answer']}' " \
                              f"WHERE num = {dic_data['qna_num']}"
                        print(sql)
                        with conn_commit() as con:
                            with con.cursor() as cur:
                                cur.execute(sql)
                                con.commit()
                                dic_data['method'] = 'answer_result'
                                dic_data['result'] = True

                    json_data = json.dumps(dic_data)
                    for client in self.clients:
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == 'point_grade':
                    sql = f"SELECT * FROM student WHERE student_num = {dic_data['member_num']}"
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        result = cur.fetchall()[0]
                        print(result)
                        dic_data['method'] = 'point_grade_result'
                        dic_data['point'] = result[1]
                        dic_data['grade'] = result[2]

                    json_data = json.dumps(dic_data)
                    for client in self.clients:
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                if dic_data['method'] == 'load_quiz_score':
                    sql = f"SELECT * FROM quiz_result WHERE student_num = {dic_data['member_num']}"
                    print(sql)
                    with conn_fetch() as cur:
                        cur.execute(sql)
                        dic_data['result'] = cur.fetchall()
                        dic_data['method'] = 'load_quiz_score_result'

                    result = dic_data['result']
                    del dic_data['result']
                    count = 0
                    for i in range(len(result)):
                        for client in self.clients:
                            dic_data['data'] = result[i]
                            dic_data['index'] = count
                            json_data = json.dumps(dic_data)
                            socket, (ip, port) = client
                            socket.sendall(json_data.encode())
                            time.sleep(0.05)
                            count += 1

                ########연재 시작
                if dic_data['method'] == '!!!':
                    print("sdsd")
                    print(dic_data)
                    self.quizname_server = dic_data
                    self.quizname(c_socket, dic_data)

                if dic_data['method'] == '@@@':
                    self.quizcontent_server = dic_data
                    self.quizcontent(c_socket, dic_data)

                if dic_data['method'] == '^^^':
                    self.quizscore_server = dic_data
                    self.quiz_score_storage(c_socket, dic_data)

                if dic_data['method'] == '%%%':
                    self.cb_server = dic_data
                    self.cb_pro_server(c_socket, dic_data)

                # if dic_data['method'] == '^0^':
                #     self.temp_login = dic_data
                #     self.asd(c_socket, dic_data)

                if dic_data['method'] == '^*^*':
                    self.pro_name_find = dic_data
                    self.pro_name_chat(c_socket, dic_data)

                if dic_data['method'] == '#$#$':
                    self.line_message_stu = dic_data
                    self.message_to_listwidget(c_socket, dic_data)

                # -----------교사 채팅----------------------
                if dic_data['method'] == '(**':
                    self.index_student_name = dic_data
                    self.find_stuname_in_tw(c_socket, dic_data)

                if dic_data['method'] == '<><>':
                    self.name_to_chat_tc = dic_data
                    self.name_to_chat_tctc(c_socket, dic_data)

                if dic_data['method'] == '*()*()':
                    print('여긴 오나?')
                    self.send_all_chat_widget_tc = dic_data
                    self.chat_to_stu_line(c_socket, dic_data)

                ######### 연재 끝

        c_socket.close()

    def quizname(self, senders_socket, dic_data):
        print("*(*(*(")
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select distinct topic from eduapp.quiz")
        topic = curs.fetchall()
        print(topic)

        conn.commit()
        data = {'method': '!!!', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

    def quizcontent(self, senders_socket, dic_data):
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select content from eduapp.quiz where topic = '{self.quizcontent_server['text']}'")
        content_row = curs.fetchall()
        print(content_row)
        b = [x[0] for x in content_row]
        print(b)
        curs.execute(f"select answer from eduapp.quiz where topic = '{self.quizcontent_server['text']}'")
        answer_row = curs.fetchall()
        print(answer_row)
        c = [x[0] for x in answer_row]
        print(c)
        quiz_dic = {name: value for name, value in zip(c, b)}
        topic = quiz_dic

        data = {'method': '@@@', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

        # if dic_data['method'] == '^^^':

    def quiz_score_storage(self, senders_socket, dic_data):
        b = self.quizscore_server['text']
        self.name_stunum_point_grade_list = []

        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()

        if len(b) == 9:
            print(b)
            print("asfasfasfa")
            curs.execute(f"select num from member where uname = '{b[8]}'")
            login_pk = curs.fetchall()

            curs.execute(
                f"insert into quiz_result (quiz_datetime, student_num, topic, answer1, answer2, answer3, answer4, answer5, count)"
                f"values ('{b[6]}', '{login_pk[0][0]}', '{b[5]}', '{b[0]}', '{b[1]}', '{b[2]}', '{b[3]}', '{b[4]}', '{b[7]}')")
            curs.fetchall()
            b.append(login_pk[0][0])
            print(b)
            self.quiz_solve_name = b[8]  # 이름

            # ----------------------------------------------포인트 계산 시작--------------------------------------------------
            conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                                   autocommit=True)
            curs = conn.cursor()

            curs.execute(f"select convert(avg(count),signed integer) from quiz_result where student_num = '{b[9]}'")
            avg_from_sql = curs.fetchall()
            print(avg_from_sql)
            self.avg = avg_from_sql[0][0]
            print(self.avg)  # 평균 구함

            curs.execute(f"select convert(sum(count), signed integer) from quiz_result where student_num = '{b[9]}'")
            sum_from_sql = curs.fetchall()
            print(sum_from_sql)
            self.sum = sum_from_sql[0][0]
            print(self.sum)  # 합산 구함

            self.name_stunum_point_grade_list.append(f"{b[9]}")
            self.name_stunum_point_grade_list.append(f"{b[8]}")

            self.point = self.sum * 5  # 문제 하나당 5점

            if self.avg >= 4:
                self.name_stunum_point_grade_list.append('A')
            if 4 > self.avg >= 3:
                self.name_stunum_point_grade_list.append('B')
            if 3 > self.avg >= 2:
                self.name_stunum_point_grade_list.append('C')
            if 2 > self.avg >= 1:
                self.name_stunum_point_grade_list.append('D')

            self.name_stunum_point_grade_list.append(f"{self.point}")

            print(self.name_stunum_point_grade_list)

            curs.execute(
                f"update student set point = '{self.name_stunum_point_grade_list[3]}', grade = '{self.name_stunum_point_grade_list[2]}' where student_num = '{self.name_stunum_point_grade_list[0]}'")
            curs.fetchall()


        elif len(b) == 8:
            print(b)
            print("four")
            curs.execute(f"select num from member where uname = '{b[7]}'")
            login_pk = curs.fetchall()

            curs.execute(
                f"insert into quiz_result (quiz_datetime, student_num, topic, answer1, answer2, answer3, answer4, count)"
                f"values ('{b[5]}', '{login_pk[0][0]}', '{b[4]}', '{b[0]}', '{b[1]}', '{b[2]}', '{b[3]}', '{b[6]}')")
            curs.fetchall()
            b.append(login_pk[0][0])
            print(b)
            self.quiz_solve_name2 = b[7]  # 이름

            # ----------------------------------------------포인트 계산 시작--------------------------------------------------
            conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                                   autocommit=True)
            curs = conn.cursor()
            curs.execute(f"select a.quiz_datetime, a.student_num, b.uname, a.answer1, a.answer2, a.answer3, a.answer4, a.answer5, a.count from quiz_result a\
                                                    left join member b\
                                                    on a.student_num = b.num\
                                                    where b.uname = '{self.quiz_solve_name2}'")

            self.quiz_result_0 = curs.fetchall()  # 각 학생 채점 전체 이중튜플
            print(self.quiz_result_0)



        elif len(b) == 6:
            print(b)
            print("two")
            curs.execute(f"select num from member where uname = '{b[5]}'")
            login_pk = curs.fetchall()

            curs.execute(f"insert into quiz_result (quiz_datetime, student_num, topic, answer1, answer2, count)"
                         f"values ('{b[3]}', '{login_pk[0][0]}', '{b[2]}', '{b[0]}', '{b[1]}', '{b[4]}')")
            curs.fetchall()
            b.append(login_pk[0][0])
            print(b)
            self.quiz_solve_name3 = b[5]  # 이름

            # ----------------------------------------------포인트 계산 시작--------------------------------------------------
            conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                                   autocommit=True)
            curs = conn.cursor()
            curs.execute(f"select a.quiz_datetime, a.student_num, b.uname, a.answer1, a.answer2, a.answer3, a.answer4, a.answer5, a.count from quiz_result a\
                                                    left join member b\
                                                    on a.student_num = b.num\
                                                    where b.uname = '{self.quiz_solve_name3}'")

            self.quiz_result_0 = curs.fetchall()  # 각 학생 채점 전체 이중튜플
            print(self.quiz_result_0)

        # %%%

    def cb_pro_server(self, senders_socket, dic_data):
        print("%%%%%")
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select uname from member where auth = 't'")
        topic = curs.fetchall()
        print(topic)
        print(type(topic))
        data = {'method': '%%%', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

    def asd(self, senders_socket, dic_data):  # temp
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select uname, auth from member where uid = '{self.temp_login['text']}'")
        topic = curs.fetchall()
        print(topic)
        print(type(topic))

        data = {'method': '^0^', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

        # ^*^*

    def pro_name_chat(self, senders_socket, dic_data):
        # self.pro_name_find
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select a.num, a.sender_num, b.uname, a.receiver_num, c.uname, a.message, a.send_time from consulting a\
                           left join member b on a.sender_num = b.num\
                           left join member c on a.receiver_num = c.num\
                           where c.uname = '{self.pro_name_find['text']}'\
                           order by send_time desc LIMIT 10")
        topic = curs.fetchall()
        print(topic)
        print(type(topic))
        data = {'method': '^*^*', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

        # #$#$

    def message_to_listwidget(self, senders_socket, dic_data):
        self.line_message_stu
        b = self.line_message_stu['text']
        print('SFSFSFSFFSFSF')
        print(b)
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select distinct num from member where uname = '{b[3]}'")
        a = curs.fetchall()
        c = a[0][0]
        b.append(c)  # 받는 사람 pk 어펜드
        curs.execute(f"select distinct num from member where uname = '{b[1]}'")
        d = curs.fetchall()
        e = d[0][0]
        b.append(e)  # 보내는 사람 pk 어펜드 리스트 [학생이 교사한테 메세지 보낸 시간, 보낸 학생, 메세지 내용, 받는 교수, 교수 pk, 학생 pk]
        print(b)
        curs.execute(f"insert into consulting (sender_num, receiver_num, message, send_time)\
                          values ('{b[5]}', '{b[4]}','{b[2]}', '{b[0]}')")
        curs.fetchall()  # 여기까지가 학생이 보낸 메시지를 db에 저장해서 선생 클라에서 써먹기 위한 식
        topic = b

        data = {'method': '#$#$', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

        # 2023년 20시
        # (**
        # -------------------교사 채팅-------------------------------------------

    def find_stuname_in_tw(self, senders_socket, dic_data):
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select distinct uname from member where auth = 's'")
        topic = curs.fetchall()
        print(topic)

        data = {'method': '(**', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

    def name_to_chat_tctc(self, senders_socket, dic_data):
        print(self.name_to_chat_tc)
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select a.num, a.sender_num, b.uname, a.receiver_num, c.uname, a.message, a.send_time from consulting a\
                           left join member b on a.sender_num = b.num\
                           left join member c on a.receiver_num = c.num\
                           where c.uname = '{self.name_to_chat_tc['text']}'\
                           order by send_time desc LIMIT 10")
        topic = curs.fetchall()
        print(topic)
        print(type(topic))

        data = {'method': '<><>', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

    def chat_to_stu_line(self, senders_socket, dic_data):
        b = self.send_all_chat_widget_tc['text']
        print(b)
        conn = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8',
                               autocommit=True)
        curs = conn.cursor()
        curs.execute(f"select distinct num from member where uname = '{b[3]}'")
        a = curs.fetchall()
        c = a[0][0]
        b.append(c)  # 받는 사람 pk 어펜드
        curs.execute(f"select distinct num from member where uname = '{b[1]}'")
        d = curs.fetchall()
        e = d[0][0]
        b.append(e)  # 보내는 사람 pk 어펜드 리스트 [학생이 교사한테 메세지 보낸 시간, 보낸 교수, 메세지 내용, 받는 학생, 학생 pk, 교수 pk]
        print(b)
        curs.execute(f"insert into consulting (sender_num, receiver_num, message, send_time)\
                                  values ('{b[5]}', '{b[4]}','{b[2]}', '{b[0]}')")
        curs.fetchall()

        topic = b
        print(topic)

        data = {'method': '*()*()', 'text': topic}
        json_data = json.dumps(data)
        for client in self.clients:
            socket, (ip, port) = client
            socket.sendall(json_data.encode())

    ####################연재 끝###################################

    def send_everyone(self, client_sockets, dic_data):  # 채팅과 같은 접속 인원 모두에게 데이터를 전송할 때 사용
        print('send:', dic_data['method'])
        for client in client_sockets:
            json_data = json.dumps(dic_data)
            client.sendall(json_data.encode())

    def send_single(self, client_socket, dic_data):  # 개인정보가 담긴 기능을 전송할 때 사용
        print("789")
        print(dic_data)
        # json_data = json.dumps(dic_data)
        # client_socket.sendall(json_data.encode())
        print('send:', dic_data['method'])
        for client in client_socket:
            json_data = json.dumps(dic_data)
            client.sendall(json_data.encode())

    def send_big_data(self, client_sockets, dic_data):  # 테이블에 값이 많은 경우 데에 사용
        print('send:', dic_data['method'])
        result = dic_data['result']
        del dic_data['result']
        count = 0
        for i in range(len(result)):
            for client in client_sockets:
                dic_data['data'] = result[i]
                dic_data['index'] = count
                json_data = json.dumps(dic_data)
                client.sendall(json_data.encode())
                time.sleep(0.05)
                count += 1

        # self.send_all_clients(c_socket)


###########################가미 끝


if __name__ == "__main__":
    Multi_server = MultiChatServer()
    HOST, PORT = "10.10.21.114", 55000
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
