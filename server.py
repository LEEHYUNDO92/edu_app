import socketserver
import pymysql
import time

host_str = '10.10.21.112'
user_str = 'root3'
password_str = '123456789'


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
        self.user_list = []
        self.game_list = []
        self.game_player_list = []
        self.final_received_message = ""  # 최종 수신 메시지
        self.room_select = "chat_all"

    # 데이터를 수신하여 모든 클라이언트에게 전송한다.
    def receive_messages(self, c_socket):
        while True:
            try:
                incoming_message = c_socket.recv(512)
                if not incoming_message:  # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_received_message = incoming_message.decode('utf-8')

                # DB에 수신 메시지 넣어줌
                if self.final_received_message[-3:] == '001':
                    for client in self.clients:  # 목록에 있는 모든 소켓에 대해
                        socket, (ip, port) = client
                        socket.sendall((self.final_received_message[:-3] + "001").encode())

                # self.send_all_clients(c_socket)
        c_socket.close()


if __name__ == "__main__":
    Multi_server = MultiChatServer()
    HOST, PORT = "127.0.0.1", 9000
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
