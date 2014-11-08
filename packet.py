
import random
import re
from constants import constants

packet_seed = random.randint(0, 100000)
packet_iterator = 0


def get_packet_id():
    global packet_seed
    global packet_iterator

    pid = packet_iterator + packet_seed

    packet_iterator += 1

    return pid


#character escaping chars
chars_table = { ',' : '--COMMA--', ':' : '--..--' }

def escape_chars(text):
    global chars_table

    for k in chars_table:
        text = text.replace(k, chars_table[k])

    return text


def unescape_chars(text):
    global chars_table

    for k in chars_table:
        text = text.replace(chars_table[k], k)

    return text


class packet_exception(Exception):
    pass


class packet:
    (flag,doc_name,talk_to_server,is_new_file) = (1,"workspace.txt",2,1); 
    (Error, Ping, ConnectionInit, UserIdAssignation, Closing, Workspace, Right, ReleaseRight, WorkspaceUpdate, WriteUpdate, Message) = (-1000, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)  # Other type to add

    def __init__(self,text_data=None):
        self.packet_id = -1
        self.packet_type = constants().Dummy
        self.stamp = 0
        self.my_host_name = None
        self.my_port_name = None
        self.data = None
        self.fields = {}
        self.list_of_ip = []
        if text_data is not None:
            self.__from_string(text_data)
        else:
            self.packet_id = get_packet_id()
            self.packet_type = self.Ping
            self.fields = {}

    def __from_string(self, text_data):
        list = text_data.split(",,,")
        print "text_data",text_data
        for type_data in list:
            content = type_data.split(":")
            if content[0] == "packet_type":
                self.packet_type = int(content[1])
            elif content[0] == "my_host_name":
                self.my_host_name = content[1]
            elif content[0] == "data":
                self.data = content[1]
            elif content[0] == "my_port_name":
                self.my_port_name = int(content[1])
            elif content[0] == "list_of_ip":
                c = content[1].split("!")
                print "content[1]",c
                for x in c:

                    q = re.sub("[^\w]", " ", x).split()
                    print "q ",q
                    self.list_of_ip.append([q[0],int(q[1])])
                print self.list_of_ip


    def put_field(self, key, value):
        if value is str:
            self.fields[key] = value
        else:
            self.fields[key] = str(value)

    def get_field(self, key):
        return self.fields[key]

    def get_int(self, key):
        return int(self.fields[key])

    def get_bool(self, key):
        if self.fields[key] == 'True':
            return True
        else:
            return False

    def to_string(self):
        data = ""
        if self.packet_type:
            data = data + "packet_type:" + str(self.packet_type) + ",,,"
        if self.my_host_name:
            data = data + "my_host_name:" + str(self.my_host_name) + ",,,"
        if self.data:
            data = data + "data:" + self.data + ",,,"
        if self.list_of_ip != []:
            list_str = ""
            for x in range(0,len(self.list_of_ip)-1):
                list_str = list_str + str(self.list_of_ip[x]) + "!"
            list_str = list_str + str(self.list_of_ip[-1])
            data = data + "list_of_ip:" + list_str + ",,,"
        if self.my_port_name:
            data = data + "my_port_name:" + str(self.my_port_name)
        print "packet data is " + data
        return data
