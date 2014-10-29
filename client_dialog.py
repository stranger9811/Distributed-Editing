
from PyQt4 import QtGui, QtCore
import server

class connect_dialog(QtGui.QDialog):

    (Width, Height) = (200, 60)

    def __init__(self, parent):
        super(connect_dialog, self).__init__(parent)
        self.__init_components()

        self.connect_trigger = None

    def __init_components(self):

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        #buttons
        self.btn_connect = QtGui.QPushButton("Connect")
        self.btn_connect.clicked.connect(self.__connect_trigger)

        self.btn_cancel = QtGui.QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.close)

        #labels
        self.lbl_hostname = QtGui.QLabel("Hostname : ")
        self.lbl_port = QtGui.QLabel("Port : ")

        #text edit
        self.te_hostname = QtGui.QLineEdit("127.0.0.1")
        self.te_port = QtGui.QLineEdit(str(server.server.DefaultPort))

        #adding widget to the layout
        self.grid.addWidget(self.lbl_hostname, 0, 0)
        self.grid.addWidget(self.lbl_port, 1, 0)

        self.grid.addWidget(self.te_hostname, 0, 1)
        self.grid.addWidget(self.te_port, 1, 1)

        self.grid.addWidget(self.btn_connect, 2, 0)
        self.grid.addWidget(self.btn_cancel, 2, 1)

        #dialog init
        self.setLayout(self.grid)
        self.setGeometry(100, 100, self.Width, self.Height)
        self.setWindowTitle("Connect to a server")
        self.show()

    def __connect_trigger(self):
        host = str(self.te_hostname.text())
        port = int(str(self.te_port.text()))
        if self.connect_trigger is not None:
            self.connect_trigger(host, port)

        self.close()