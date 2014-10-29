
import random
import re


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

    def __init__(self, text_data=None):
        self.packet_id = -1
        self.packet_type = self.Ping
        self.stamp = 0
        self.fields = {}

        if text_data is not None:
            self.__from_string(text_data)
        else:
            self.packet_id = get_packet_id()
            self.packet_type = self.Ping
            self.fields = {}

    def __from_string(self, text_data):
        packet_pattern = re.compile("\\[Packet:(?P<packet_id>[0-9]+):(?P<packet_type>[\\-0-9]+):(?P<stamp>[0-9]+)\\]\\((?P<packet_data>.*)\\)", re.DOTALL)
        m = packet_pattern.match(text_data)

        if m:
            self.packet_id = int(m.group("packet_id"))
            self.packet_type = int(m.group("packet_type"))
            self.stamp = int(m.group("stamp"))
            data = m.group("packet_data")

            if len(data) > 0:
                fields = data.split(',')
                for f in fields:
                    fvars = f.split(':')
                    if len(fvars) == 2:
                        key = fvars[0]
                        fdata = fvars[1]
                        self.fields[key] = unescape_chars(fdata)
        else:
            if text_data is None:
                raise packet_exception(0, "Parsing error [Empty Packet]")
            else:
                raise packet_exception(1, "Parsing error [Raw Data: %s]" % text_data)

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

        for k in self.fields:
            fdata = "%s:%s," % (k, escape_chars(self.fields[k]))
            data += fdata

        data = data.rstrip(',')
        #[Packet:Id:Type:Stamp](Data,...)
        data = "[Packet:%d:%d:%d](%s)" % (self.packet_id, self.packet_type, self.stamp, data)
        return data
