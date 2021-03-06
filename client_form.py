
from PyQt4 import QtCore, QtGui
import sys
import client_dialog
import client
from packet import packet
from client_thread import client_thread

def findChanges(after,before):
        len_before = len(before)
        len_after = len(after)
        if(len_after < len_before):
            for i in range(0,len_before):
                if i>=len_after:
                    return 'd',after[len_after:],len_after
                if(before[i] != after[i]):
                    return 'd',before[i],i
        elif(len_after > len_before):
            for i in range(0,len_after):
                if i>=len_before:
                    return 'd',before[len_before:],len_before
                if(before[i] != after[i]):
                    return 'a',after[i],i
        else:
            return 'x','c','0'

class client_form(QtGui.QMainWindow):

    (DefaultWidth, DefaultHeight) = (500, 600)

    def __init__(self, mode,my_host_name,my_port_name):
        super(client_form, self).__init__()
        self.mode = mode
        self.w_width = self.DefaultWidth
        self.w_height = self.DefaultHeight
        self.my_host_name = my_host_name
        self.my_port_name = my_port_name
        self.connection_thread = None
        self.__init_menu()
        self.__init_components()

    

    def __init_menu(self):
        self.menu = self.menuBar()

        self.connect_server = QtGui.QAction("Connect...", self)
        self.connect_server.triggered.connect(self.connect_dialog)

        self.disconnect_server = QtGui.QAction("Disconnect", self)
        self.disconnect_server.triggered.connect(self.disconnect_action)

        self.quit_action = QtGui.QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit)

        self.file_menu = self.menu.addMenu("&File")
        self.file_menu.addAction(self.connect_server)
        self.file_menu.addAction(self.disconnect_server)
        self.file_menu.addAction(self.quit_action)


    
            

    def onTextChanged(self):
        if self.te_workspace.text_status == False:
            return
        op,c,pos = findChanges(self.te_workspace.toPlainText(),self.current_data)
        if(op != 'x'):
            self.current_data = self.te_workspace.toPlainText()

            if self.connection_thread is not None:
                self.connection_thread.client.receiveExtraOperations(str(self.te_workspace.toPlainText()),op,c,pos)


    def __init_components(self):
        self.setWindowTitle("CS632 Project")
        self.setMinimumWidth(self.w_width)
        self.setMinimumHeight(self.w_height)
        self.main_widget = QtGui.QWidget()
        self.main_widget.setGeometry(0, 0, self.w_width, self.w_height)

        self.setCentralWidget(self.main_widget)
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        self.main_widget.setLayout(self.grid)


        self.te_line    = QtGui.QLineEdit()
        self.te_workspace = QtGui.QTextEdit()
        self.te_workspace.textChanged.connect(self.onTextChanged)

        self.operation_transformation = []

        self.te_workspace.setEnabled(False)

        self.te_log = QtGui.QTextEdit()
        self.te_log.setEnabled(False)
        self.te_workspace.setEnabled(True)
        self.te_workspace.text_status = True

        #labels
        self.lbl_status_value = QtGui.QLabel("Not Connected")
        self.lbl_textbox = QtGui.QLabel("Workspace")
        self.lbl_user_value = QtGui.QLabel("")
        self.current_data = "write here"
        self.operation_transformation = []
        self.te_workspace.setText("write here")
        #grid assign
    
        self.grid.addWidget(self.lbl_textbox, 3, 0, 1, 4)
        self.grid.addWidget(self.te_workspace, 4, 0, 4, 4)

        self.show()
        

    def workspace_received(self, workspace):
        #self.give_up_right_action()
        self.te_workspace.setText(workspace.get_data())

    def block_writing(self, workspace):
        self.te_workspace.text_status = False
        self.te_workspace.setEnabled(False)

    def enable_writing(self, workspace):
        self.te_workspace.text_status = True
        self.te_workspace.setEnabled(True)


    def connect_dialog(self):
        d = client_dialog.connect_dialog(self)
        d.connect_trigger = self.connect_to_server

   

    def connect_to_server(self, hostname, port):
        #WORKSPACE-01
        if self.connection_thread is None:
            self.connection_thread = client_thread(self, hostname, port,self.my_host_name,self.my_port_name)
            
            self.connection_thread.workspace_received.connect(self.workspace_received)
          
            self.connection_thread.block_writing.connect(self.block_writing)
            self.connection_thread.enable_writing.connect(self.enable_writing)

            self.connection_thread.user_assigned.connect(self.user_assigned)
            self.connection_thread.start()

    

    def disconnect_action(self):
        if self.connection_thread is not None:
            self.connection_thread.close()



    def user_assigned(self, user_id):
        self.lbl_user_value.setText(user_id)

    def quit(self):
        self.disconnect_action()
        self.close()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    print "hello"
    #args parsing
    nargs = len(sys.argv)
    i = 0
    _mode = client.client.NormalMode
    
    if(len(sys.argv) < 3) :
        print 'Usage : python telnet.py hostname port'
        sys.exit()
    host = sys.argv[1]
    port = int(sys.argv[2])

    while i < nargs:
        arg = sys.argv[i]

        if arg == '-d' or arg == '--debug':
            print "Debug Mode"
            _mode = client.client.DebugMode
        i += 1

    frame = client_form(_mode,host,port)
    sys.exit(app.exec_())