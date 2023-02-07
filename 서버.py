import socketserver
import pymysql
import time
import json


host_str = '10.10.21.116'
user_str = 'eduapp_admin'
password_str = 'admin1234'


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

                if dic_data['method'] == '001':
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        json_data = json.dumps(dic_data)
                        socket, (ip, port) = client
                        socket.sendall(json_data.encode())

                elif dic_data['method'] == '002':


                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8')
                    with con:
                        with con.cursor() as cur:
                            for i in range(1,6):
                                if dic_data['text'][i] != '':
                                    sql = f"INSERT INTO quiz(topic,content,answer) values('{dic_data['text'][0]}', '{dic_data['text'][i]}', '{dic_data['text'][i+5]}')"
                                    cur.execute(sql)
                                    con.commit()
                    ###################################################### Data base 접속 end

                elif dic_data['method'] == '003':
                    print("abc")
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8')
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


                elif dic_data['method'] == '004':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8')
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

                elif dic_data['method'] == '005':
                    ###################################################### Data base 접속 start
                    con = pymysql.connect(host=host_str, user=user_str, password=password_str, db='eduapp', charset='utf8')
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



        # self.send_all_clients(c_socket)
        c_socket.close()


if __name__ == "__main__":
  Multi_server = MultiChatServer()
  HOST, PORT = "10.10.21.112", 55000
  with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
    server.serve_forever()