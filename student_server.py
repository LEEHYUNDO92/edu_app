import socket
import time
from _thread import *
import json
import pymysql
from datetime import datetime

client_sockets = list()

HOST = '127.0.0.1'
PORT = 9000
DB_HOST = '10.10.21.116'
DB_USER = 'eduapp_admin'
DB_PASSWORD = 'admin1234'


def conn_fetch():  # SELECT문 사용 시
    con = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db='eduapp', charset='utf8')
    cur = con.cursor()
    return cur


def conn_commit():  # INSERT, UPDATE 등 값에 변화를 주는 SQL문 사용 시
    con = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db='eduapp', charset='utf8')
    return con


def threaded(client_socket, addr):
    while True:
        try:
            data = client_socket.recv(9999)
            if not data:
                print('>> Disconnected by ' + addr[0], ':', addr[1])
                break
            dic_data = json.loads(data.decode())  # json 데이터를 다시 파이썬 코드로 변환

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
                    else:
                        dic_data['result'] = True
                        dic_data['login_info'] = result[0]

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

            if dic_data['method'] == 'delete_question':
                sql = f"DELETE FROM qna WHERE num = {dic_data['qna_num']}"
                print(sql)
                with conn_commit() as con:
                    with con.cursor() as cur:
                        cur.execute(sql)
                        con.commit()
                        dic_data['method'] = 'delete_question_result'
                        dic_data['result'] = True

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

            if dic_data['method'] == 'point_grade':
                sql = f"SELECT * FROM quiz_result " \
                      f"WHERE student_num = {dic_data['member_num']} " \
                      f"ORDER BY topic, quiz_datetime"
                print(sql)
                with conn_fetch() as cur:
                    cur.execute(sql)
                    result = cur.fetchall()
                    dic_data['method'] = 'point_grade_result'
                    print(result)

                dic_data['point'] = 0
                all_question = 0
                temp_topic = ''
                t1, t2, t3, t4, t5 = 0, 0, 0, 0, 0
                for i in range(len(result)):
                    if result[i][2] != temp_topic:
                        dic_data['point'] += t1 + t2 + t3 + t4 + t5
                        temp_topic = result[i][2]
                        t1, t2, t3, t4, t5 = 0, 0, 0, 0, 0
                        if result[i][3] == 'o':
                            t1 = 5
                        if result[i][4] == 'o':
                            t2 = 5
                        if result[i][5] == 'o':
                            t3 = 5
                        if result[i][6] == 'o':
                            t4 = 5
                        if result[i][7] == 'o':
                            t5 = 5
                        for j in range(3, 8):
                            if result[i][j] is None:
                                break
                            all_question += 1
                    else:
                        if result[i][3] == 'o' and t1 == 0:
                            t1 = 4
                        if result[i][4] == 'o' and t2 == 0:
                            t2 = 4
                        if result[i][5] == 'o' and t3 == 0:
                            t3 = 4
                        if result[i][6] == 'o' and t4 == 0:
                            t4 = 4
                        if result[i][7] == 'o' and t5 == 0:
                            t5 = 4

                    if i == len(result) - 1:
                        dic_data['point'] += t1 + t2 + t3 + t4 + t5

                    print(t1, t2, t3, t4, t5, dic_data['point'])
                dic_data['max_point'] = all_question * 5
                print(all_question, dic_data['max_point'])

            # 아래는 각 기능에 따라 전송 대상 지정하는 함수, 참고용으로 놔둠
            if dic_data['method'] == 'chat':
                send_everyone(client_sockets, dic_data)
            elif dic_data['method'] == 'load_table_result':
                send_big_data(client_sockets, dic_data)
            else:
                send_single(client_socket, dic_data)

        except ConnectionResetError as e:
            print('>> Disconnected by ' + addr[0], ':', addr[1])
            break
    if client_socket in client_sockets:
        client_sockets.remove(client_socket)
        print('remove client list:', len(client_sockets))

    client_socket.close()


def send_everyone(client_sockets, dic_data):  # 채팅과 같은 접속 인원 모두에게 데이터를 전송할 때 사용
    print('send:', dic_data['method'])
    for client in client_sockets:
        json_data = json.dumps(dic_data)
        client.sendall(json_data.encode())


def send_single(client_socket, dic_data):  # 개인정보가 담긴 기능을 전송할 때 사용
    print('send:', dic_data['method'])
    json_data = json.dumps(dic_data)
    client_socket.sendall(json_data.encode())


def send_big_data(client_sockets, dic_data):  # 테이블에 값이 많은 경우 데에 사용
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


print('>> Server Start')
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

try:
    while True:
        print('>> Wait')
        client_socket, addr = server_socket.accept()
        client_sockets.append(client_socket)
        start_new_thread(threaded, (client_socket, addr))
        print("참가자 수 : ", len(client_sockets))

except Exception as e:
    print('에러는? : ', e)

finally:
    server_socket.close()
