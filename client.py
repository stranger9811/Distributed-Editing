import socket
from server import server  # for default port
from packet import packet
import workspace
import workspace_diff
import time
import sys
import thread
from constants import constants





class client_status:
    def __init__(self, can_write=False, is_waiting=False):
        self.can_write = can_write
        self.is_waiting = is_waiting


class client:
    (BufferSize) = 2048
    (NormalMode, DebugMode) = (0, 1)

    def __init__(self, hostname, port=server.DefaultPort, mode=NormalMode, file_name = "workspace.txt"):
        self.mode = mode
        self.hostname = hostname
        self.port = port
        self.file_name = file_name
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_id = None
        self.workspace = workspace.workspace()
        self.pending_diff = None
        self.peers = []
        self.set_of_operation = []
        self.can_write = True
        self.is_waiting = False

        self.workspace_received = None
        self.workspace_received2 = None
        self.block_writing = None
        self.enable_writing = None
        self.write_status_changed = None
        self.write_update = None
        self.user_assigned = None
        self.message_received = None

        self.queued_packets = []
        self.sent_packets = []
        self.received_packets = []

        self.buffer_size = self.BufferSize


        #event handling
        self.disconnected = None

    def __user_assigned(self):
        if self.user_assigned is not None:
            self.user_assigned()

    def __message_recevied(self, message):
        if self.message_received is not None:
            self.message_received(message)

    def sendOperationToAllPeers(self,operation, peers):
        print "sending ", operation, " to all peers",peers

    def get_client_status(self):
        return client_status(self.can_write, self.is_waiting)

    def __workspace_received(self):
        if self.workspace_received is not None:
            self.workspace_received(self.workspace)

    def __block_writing(self):
        if self.block_writing is not None:
            self.block_writing(self.workspace)

    def __enable_writing(self):
        if self.enable_writing is not None:
            self.enable_writing(self.workspace)

    def __workspace_received2(self):
        print "inside workspace_received2"
        if self.workspace_received2 is not None:
            print "inside if condition..."
            self.workspace_received2(self.workspace)

    def make_diff(self, new_text):
    
        self.workspace.set_data(new_text)


    def receiveExtraOperations(self,operation, s,pos):
        print " new operation to be done", operation, s,pos
        self.set_of_operation.append([operation, s,pos])
        


    def debug(self, message):
        if self.mode == self.DebugMode:
            print "[Debug] %s" % message



    def __disconnected(self):
        if self.disconnected is not None:
            self.disconnected()

    def connect(self):
        try:

            self.socket.connect((self.hostname, self.port))

            self.connected = True
            return True
        except socket.error as e:
            print "Unable to connect to %s:%d" % (self.hostname, self.port)

        return False

    def connect_peer(self,hostname,port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((hostname, port))

            self.connected = True
            return True
        except socket.error as e:
            print "Unable to connect to %s:%d" % (hostname, port)

        return False

    def loop(self,my_host_name,my_port_name):
        constant = constants()
        print my_host_name,my_port_name
        while self.connected:
            try:
                send_packet = packet()
                send_packet.packet_type = constant.JOIN
                send_packet.my_host_name = my_host_name
                send_packet.my_port_name = my_port_name
                print "details packet_type",send_packet.packet_type
                send_packet.doc_name = self.file_name
                self.__send(send_packet)

                recv_packet = self.__receive()
                self.socket.close();
                print "can write ",self.can_write
                self.bind_socket.bind((my_host_name,my_port_name))
                print "creating server at ",my_host_name,my_port_name
                self.bind_socket.listen(10)
                if recv_packet.packet_type == constant.NewFile:  #new file created.
                    while 1:
                        print "waiting to accept....."
                        thread.start_new_thread(self.sendOperationToAllPeers,(self.set_of_operation,self.peers))
            
                        peer_socket, peer_address = self.bind_socket.accept()

                        print "connection accepted ....."
                        try:
                            recv_peer_packet = self.__peer_receive(peer_socket)
                            # <packet_type 1000: my_host_name: my_port_name> 
                            if recv_peer_packet.packet_type == constant.NewConnection:
                                self.peers.append([recv_peer_packet.my_host_name, recv_peer_packet.my_port_name])
                               
                                send_packet = packet()
                                send_packet.packet_type = constant.Ack
                                self.__peer_send(peer_socket,send_packet)

                            if recv_peer_packet.packet_type == constant.getData:
                                print "some peer wants my data workspace.data"
                                send_packet = packet()
                                print "my workspace data before is ", self.workspace.get_data()
                                self.__workspace_received2()
                                time.sleep(1.3)
                                print "my workspace data is ", self.workspace.get_data()
                                send_packet.data = self.workspace.get_data()
                                self.__peer_send(peer_socket,send_packet)
                            peer_socket.close()
                        except:
                            peer_socket.close()
                            print "error 265"
                    
                else:
                    print "joining existing file list_of_ip: ",recv_packet.list_of_ip
                    self.__block_writing()
                    for peer in recv_packet.list_of_ip:
                        print "perr details are: ", peer
                        self.connect_peer(peer[0],peer[1])
                        send_packet = packet()
                        send_packet.packet_type = constant.NewConnection
                        send_packet.my_host_name = my_host_name
                        send_packet.my_port_name = my_port_name
                        self.__send(send_packet)
                        recv_peer_ack = self.__receive()
                    peer = recv_packet.list_of_ip[0]
                    self.connect_peer(peer[0],peer[1])
                    send_packet.packet_type = constant.getData
                    self.__send(send_packet)
                    recv_peer_data = self.__receive()
                    self.workspace.set_data(recv_peer_data.data)
                    print "recv_data ", recv_peer_data.data
                    self.__workspace_received()

                    print "recv_packet data:",recv_peer_data.data
                    while 1:
                        if len(self.peers) != 0 and len(self.set_of_operation)!=0:
                            thread.start_new_thread(self.sendOperationToAllPeers,(self.set_of_operation,self.peers))
                        print "waiting to accept....."
                        peer_socket, peer_address = self.bind_socket.accept()
                        print "connection accepted ....."
                        try:
                            recv_peer_packet = self.__peer_receive(peer_socket)
                            # <packet_type 1000: my_host_name: my_port_name> 
                            if recv_peer_packet.packet_type == constant.NewConnection:
                                self.peers.append([recv_peer_packet.my_host_name, recv_peer_packet.my_port_name])
                               
                                send_packet = packet()
                                send_packet.packet_type = constant.Ack
                                self.__peer_send(peer_socket,send_packet)

                            if recv_peer_packet.packet_type == constant.getData:
                                print "some peer wants my data workspace.data"
                                send_packet = packet()
                                print "my workspace data before is ", self.workspace.get_data()
                                self.__workspace_received2()
                                time.sleep(1.3)
                                print "my workspace data is ", self.workspace.get_data()
                                send_packet.data = self.workspace.get_data()
                                self.__peer_send(peer_socket,send_packet)
                            peer_socket.close()
                        except:
                            peer_socket.close()
                            print "error 265"
                    # send_packet = packet()
                    # send_packet.packet_type = constant.getData
                    # self.__send(send_packet)
                    # recv_peer_ack = self.__receive()




            except socket.error as e:
                print "Socket error [%s, %s]" % (e.errno, e.strerror)
                self.connected = False
                self.__disconnected()

            time.sleep(0.2)

    def __peer_send(self,peer_socket,to_send):
        print "sending packet packet_type:", to_send.packet_type
        peer_socket.send(to_send.to_string())

    def __peer_receive(self,peer_socket):
        data = peer_socket.recv(self.buffer_size)
        recv_packet = packet(data)
        return recv_packet

    def __receive(self):
        sock_data = self.socket.recv(self.buffer_size)
        recv_packet = packet(sock_data)
        return recv_packet

    def __send(self, to_send):
        print "sending packet packet_type:", to_send.packet_type
        self.sent_packets.append(to_send)
        self.socket.send(to_send.to_string())

    def __queued(self, to_add):
        self.queued_packets.append(to_add)

    def close(self):
        if self.connected:
            send_packet = packet()
            send_packet.packet_type = packet.Closing

            self.__send(send_packet)
            self.connected = False

            self.__disconnected()


if __name__ == '__main__':
    print "pydtxtedit Console client"
    print "GUI To implement..."

    _host = '127.0.0.1'
    _port = server.DefaultPort

    nargs = len(sys.argv)
    i = 0

    while i < nargs:
        arg = sys.argv[i]

        if arg == '-h' or arg == '--hostname':
            i += 1
            if i < nargs:
                _host = sys.argv[i]
        elif arg == '-p' or arg == '--port':
            i += 1
            if i < nargs:
                _port = int(sys.argv[i])
        i += 1

    _client = client(_host, _port)
    if _client.connect():
        _client.loop()