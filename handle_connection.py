
import threading
import socket
from packet import packet, packet_exception
import random
import hashlib
import time
import workspace_diff
from constants import constants


#global vars
doc_index = {}
current_connection_id = 0

def check_connection():
    global doc_index
    global current_connection_id
    cid = current_connection_id
    current_connection_id += 1
    return cid



class handle_connection(threading.Thread):

    (BufferSize) = 2048

    def __init__(self, client, address, master):
        threading.Thread.__init__(self)
        self.address = address
        self.connection_id = check_connection()
        self.client = client
        self.master = master
        self.connected = False
        self.buffer_size = self.BufferSize
        self.user_id = None

        self.sent_packets = []
        self.queued_packets = []

    def __generate_user_id(self):
        if self.user_id is None:

            self.user_id = self.master.get_username()
            self.master.debug("User id : %s" % self.user_id)

    def run(self):
        self.connected = True
        print "Connection %d started" % self.connection_id
        constant = constants()
        try:
            recv_data = self.client.recv(self.buffer_size)
            try:
                recv_packet = packet(recv_data)
            except packet_exception as e:
                self.master.debug("[%d] Invalid Packet, closing connection" % self.connection_id)
                self.connected = False
            print "packet type is ",recv_packet.packet_type
            if recv_packet.packet_type == constant.JOIN:
                doc = recv_packet.doc_name
                print doc, "this is the doc... 1"
                print doc_index;
                if doc in doc_index.keys():
                    send_packet  = packet()
                    send_packet.packet_type = constant.Dummy
                    send_packet.list_of_ip = doc_index[doc]
                    self.__send(send_packet)
                    doc_index[doc].append([recv_packet.my_host_name,recv_packet.my_port_name]);
                else:
                    doc = recv_packet.doc_name
                    print doc, "this is the doc... 2"
                    print doc_index;
                    print "i am in else...",recv_packet.my_host_name,recv_packet.my_port_name
                    print "doc_index",doc_index
                    doc_index[doc] = list([[recv_packet.my_host_name,recv_packet.my_port_name]]);
                    print "doc_index",doc_index
                    send_packet  = packet()
                    send_packet.packet_type  = constant.NewFile
                    self.__send(send_packet)

                print "client want to join " + doc

        except socket.timeout:
            #timeout hit
            print "[%d] Client timed out, terminating thread" % self.connection_id
            self.connected = False

        except socket.error as e:
            self.master.debug("socket.error (%d, %s)" % (e.errno, e.strerror))
            if e.errno == 10054:
                print "Connection closed by the client..."
                self.connected = False

        #little nap for the cpu
        time.sleep(0.3)

        self.terminate()

   


    def __error(self, message):
        error_packet = packet()
        error_packet.packet_type = packet.Error
        error_packet.fields['message'] = message
        print "[%d] Sending error packet..." % self.connection_id
        self.__send(error_packet)

    def __send(self, to_send):
        self.sent_packets.append(to_send)
        self.client.send(to_send.to_string())

    

    def terminate(self):
        self.connected = False
        print "Connection %d ended" % self.connection_id
        self.client.close()
        self.master.clean_connection(self)
        self.master.threads.remove(self)