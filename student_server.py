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
""" 사용 예시
with conn_fetch() as cur:
    cur.execute(sql)
    result = cur.fetchall()
"""


def conn_commit():  # INSERT, UPDATE 등 값에 변화를 주는 SQL문 사용 시
    con = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db='eduapp', charset='utf8')
    return con
""" 사용 예시
with conn_commit() as con:
    with con.cursor() as cur:
        cur.execute(sql)
        con.commit()
"""


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

            # 아래는 각 기능에 따라 전송 대상 지정하는 함수, 참고용으로 놔둠
            if dic_data['method'] == 'chat':
                send_everyone(client_sockets, dic_data)
            elif dic_data['method'] == 'load_chat_result':
                send_chat_history(client_sockets, dic_data)
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
    for client in client_sockets:
        json_data = json.dumps(dic_data)
        client.sendall(json_data.encode())


def send_single(client_socket, dic_data):  # 개인정보가 담긴 기능을 전송할 때 사용
    json_data = json.dumps(dic_data)
    client_socket.sendall(json_data.encode())


def send_chat_history(client_sockets, dic_data):  # 대화 목록 불러오는 데에 사용
    result = dic_data['result']
    del dic_data['result']
    for i in result:
        for client in client_sockets:
            dic_data['data'] = [i[1], i[3], str(i[2])]
            json_data = json.dumps(dic_data)
            client.sendall(json_data.encode())
            time.sleep(0.05)


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
