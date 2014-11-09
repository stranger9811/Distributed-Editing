
import socket
import sys
from handle_connection import handle_connection
import workspace
import random
import packet


class server:

    (DefaultPort, DefaultWorkspace, MaxConnections) = (5499, 'workspace.txt', 25)
    (NormalMode, DebugMode) = (0, 1)

    def __init__(self, port=DefaultPort, workspace_file=DefaultWorkspace, max_connections=MaxConnections, mode=NormalMode):
        self.mode = mode
        self.port = port
        self.workspace_file = workspace_file
        self.workspace = workspace.file_workspace(self.workspace_file)
        self.access_write = None
        self.access_queued = []
        self.max_connections = max_connections

        self.bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.run = True
        self.threads = []

        self.usernames = []


    def get_thread(self, connection_id):
        for c in self.threads:
            if c.connection_id == connection_id:
                return c

        return None

    def send_message(self, message, excludes=[]):
        for c in self.threads:
            if c.connection_id not in excludes:
                p = packet.packet()
                p.packet_type = packet.packet.Message
                p.put_field("message", message)
                c.queued_packets.append(p)

  

    def get_username(self):
        i = random.randint(0, len(self.usernames) - 1)
        user = self.usernames.pop(i)
        return user

    def next_in_queued(self):
        if len(self.access_queued) > 0:
            success = False
            succeeding = self.access_queued[0]

            for thread in self.threads:
                print "thread id: " + str(thread.connection_id) + " / waiting id: " + str(succeeding)

                if thread.connection_id == succeeding:
                    print "find one with the same id"
                    thread.next_inline()
                    success = True

            if success:
                self.access_queued.remove(succeeding)

    def adding_access_queued(self, connection_id):
        if not connection_id in self.access_queued:
            self.access_queued.append(connection_id)

    def debug(self, message):
        if self.mode == self.DebugMode:
            print "[Debug] %s" % message
        #todo logfile output

    def clean_connection(self, connection):
        if self.access_write == connection.connection_id:
            self.access_write = None
            print "Removing write access from %d" % connection.connection_id
            self.next_in_queued()

        if connection.connection_id in self.access_queued:
            self.access_queued.remove(connection.connection_id)
            print "Removing in right access queued: %d" % connection.connection_id

    def start(self):
        print "Starting server"
        print "Listening on port %d" % self.port
        try:
            self.bind_socket.bind(('127.0.0.1', self.port))
        except socket.error as e:
            print "Unable to bind on port %d" % self.port
            self.debug("socket.error (%s, %s)" % (e.errno, e.strerror))
            self.run = False

        while self.run:
            try:
                self.bind_socket.listen(10)

                (client, address) = self.bind_socket.accept()

                print "Accepting connection from %s:%d" % (address[0], address[1])

                #thread creation
                client.settimeout(1)
                self.debug("Current threads count : %d" % len(self.threads))
                if len(self.threads) < self.max_connections:
                    thread = handle_connection(client, address, self)
                    self.threads.append(thread)
                    thread.start()
                else:
                    print "Maximum connection hitted !"

            except socket.error as e:
                self.debug("socket.error (%s, %s)" % (e.errno, e.strerror))


if __name__ == '__main__':

    _mode = server.NormalMode
    _port = server.DefaultPort
    _workspace = server.DefaultWorkspace

    nargs = len(sys.argv)
    i = 0

    while i < nargs:
        arg = sys.argv[i]

        if arg == '-d' or arg == '--debug':
            #debug mode  switch
            _mode = server.DebugMode
            print "Debug mode"
        elif arg == '-p' or arg == '--port':
            i += 1
            if i < nargs:
                _port = int(sys.argv[i])
        elif arg == '-w' or arg == '--workspace':
            i += 1
            if i < nargs:
                _workspace = sys.argv[i]
        i += 1

    #server init
    _server = server(_port, _workspace, server.MaxConnections, _mode)
    _server.start()