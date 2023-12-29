import typing, pdb
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QFrame, QWidget, QScrollArea, QHBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal, QFile, QTextStream, Qt

class Manage_rooms(QDialog):
    ui_operation_signal = pyqtSignal(str)
    def __init__(self, Rooms, Rooms_rights):
        super().__init__()
        self.rooms = Rooms
        self.room_rights = Rooms_rights
        self.POPUP = None

        #print(self.rooms)
        #print(self.room_rights)

    def gen_ui(self, POPUP):
        # Create labels and buttons for the popup
        #print(self.room_rights)

        self.POPUP = POPUP

        self.POPUP.setWindowTitle('Manage My Rooms')
        self.POPUP.resize(523, 900)
        self.POPUP.setMinimumSize(QtCore.QSize(523, 900))
        self.POPUP.setMaximumSize(QtCore.QSize(523, 900))
        self.POPUP.setAutoFillBackground(False)
        self.POPUP.setStyleSheet("background-color: #59536D;")

        self.frames = []
        self.buttons = []
        current_height_for_frames = 20

        for room in self.rooms:
            print(f"creating room widget for {room[1]}")
            frame = QWidget(self.POPUP)
            frame.setGeometry(QtCore.QRect(30, current_height_for_frames, 461, 160))

            frame.setObjectName(f"frame_{room[0]}")

            label = QLabel(frame)
            label.setGeometry(QtCore.QRect(20, 10, 411, 31))
            font = QtGui.QFont()
            font.setPointSize(18)
            label.setFont(font)
            label.setStyleSheet("border: none;\n"
    "border-bottom: 2px solid #365531;\n"
    "border-radius: 0px")
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            label.setObjectName(f"label_{room[0]}")
            label_2 = QLabel(frame)
            label_2.setGeometry(QtCore.QRect(120, 50, 211, 41))
            label_2.setStyleSheet("background-color:  #B7B4B4;\n"
    "border: 1px solid gray;\n""color: black;")
            label_2.setObjectName(f"label_2_{room[0]}")
            pushButton = QPushButton(frame)
            pushButton.setGeometry(QtCore.QRect(80, 100, 281, 40))
            pushButton.setObjectName(f"pushButton_{room[0]}")

            label.setText(f"{room[1]}")

            for rights in self.room_rights:
                if int(room[0]) == int(rights[2]):
                    if rights[3] == "YES":
                        frame.setStyleSheet("background-color: #00C113;\n"
                                            "border: 2px solid #019210;\n"
                                            "border-radius: 10px;")
                        label_2.setText("Access -> YES")
                        pushButton.setText("Already have access to this room")
                        pushButton.setStyleSheet("background-color: #019210;")
                        pushButton.setEnabled(False)
                    elif rights[3] == "NO":
                        frame.setStyleSheet("background-color: #FF0000;\n"
                                            "border: 2px solid #9b0000;\n"
                                            "border-radius: 10px;")
                        label_2.setText("Access -> NO")
                        pushButton.setText("Ask for access to this room")
                        pushButton.setStyleSheet("background-color: #9b0000;")
                    elif rights[3] == "YES_IF_ASK":
                        frame.setStyleSheet("background-color: #D18438;\n"
                                            "border: 2px solid #af6e2e;\n"
                                            "border-radius: 10px;")
                        pushButton.setText("Ask for access to this room")
                        pushButton.setStyleSheet("background-color: #af6e2e;")
                        label_2.setText("Access -> ON DEMAND")
                    elif rights[3] == "PENDING":
                        frame.setStyleSheet("background-color: #247BC2;\n"
                                            "border: 2px solid #1d5f94;\n"
                                            "border-radius: 10px;")
                        label_2.setText("Access -> PENDING APPROVAL")
                        pushButton.setText("Already sent a demand for this room")
                        pushButton.setStyleSheet("background-color: #1d5f94;")
                        pushButton.setEnabled(False)


            self.frames.append(frame)
            self.buttons.append(pushButton)
            current_height_for_frames = current_height_for_frames + 170
    
        QtCore.QMetaObject.connectSlotsByName(self.POPUP)

    def destroy(self):
        print("DESTROYING MYSELF (MANAGE ROOMS)")
        # Close and destroy the entire window
        self.POPUP.accept()

        self.close()
        self.deleteLater()

    def perform_ui_operation(self, operation):
        if operation == "destroy":
            self.destroy()


class Manage_demands(QDialog):
    ui_operation_signal = pyqtSignal(str)
    def __init__(self, demands):
        super().__init__()
        self.POPUP = None
        self.demands = demands

        #print(f"[Manage_demands init demands : {self.demands}]")

        # style_file = QFile("styles_manage_demands.css")
        # style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
        # stylesheet = QTextStream(style_file).readAll()
        # self.setStyleSheet(stylesheet)

    def destroy(self):
        print("DESTROYING MYSELF (MANAGE DEMANDS)")
        self.POPUP.accept()

        self.close()
        self.deleteLater()

    def perform_ui_operation(self, operation):
        if operation == "destroy":
            self.destroy()
        else:
            pass

    def gen_ui(self, POPUP):
        self.POPUP = POPUP

        self.POPUP.setWindowTitle('Manage User Demands')
        self.POPUP.resize(500, 800)
        self.POPUP.setMinimumSize(QtCore.QSize(500, 800))
        self.POPUP.setMaximumSize(QtCore.QSize(500, 800))
        self.POPUP.setAutoFillBackground(False)
        self.POPUP.setStyleSheet("background-color:  #59536D;")

        
        self.scroll_area = QScrollArea(self.POPUP)
        self.scroll_area.setGeometry(0, 0, 500, 800)
        self.scroll_area.setStyleSheet("background-color: #59536D;")
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget(self.scroll_area)

        scroll_layout = QVBoxLayout(self.scroll_widget)
        

        self.frames = []
        self.button_lists = []
        # current_height_for_frames = 20

        for demand in self.demands:
            
            frame = QWidget(self.POPUP)
            frame_layout = QVBoxLayout(frame)

            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame.setMinimumHeight(140)
            frame.setMaximumHeight(200)
            frame.setStyleSheet("background-color: #DCAB5F;\n""border: 2px solid black;\n""border-radius: 20px")

            
            label = QLabel(f"Demand from {demand['username']} to join {demand['room_name']}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("border: 20px solid #00000000;\n")
            
            
            button1 = QPushButton("ACCEPT")
            button2 = QPushButton("DENY")

            button1.setFixedWidth(150)
            button2.setFixedWidth(150)

            button1.setStyleSheet("background-color: #65b891;\n""font-weight: bolder;\n""border-radius: 10px;")
            button2.setStyleSheet("background-color: #a34545;\n""font-weight: bolder;\n""border-radius: 10px;")

            button_layout = QHBoxLayout()
            button_layout.addWidget(button1)
            button_layout.addWidget(button2)

            button_layout.setContentsMargins(0, 0, 0, 20)

            frame_layout.addWidget(label)
            frame_layout.addLayout(button_layout)

            scroll_layout.addWidget(frame)

            self.frames.append(frame)
            self.button_lists.append([button1, button2, demand['demand_id'], demand['uid']])
        
        if len(self.demands) == 0:
            frame = QWidget(self.POPUP)
            frame_layout = QVBoxLayout(frame)

            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame.setMinimumHeight(140)
            frame.setMaximumHeight(200)
            frame.setStyleSheet("background-color: #DCAB5F;\n""border: 2px solid black;\n""border-radius: 20px")
            
            label = QLabel("No pending demands right now..")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("border: 20px solid #00000000;\n")
            frame_layout.addWidget(label)

            scroll_layout.addWidget(frame)
        else:
            pass



        self.scroll_area.setWidget(self.scroll_widget)


class Manage_friends(QDialog):
    ui_operation_signal = pyqtSignal(str)
    def __init__(self, friend_requests):
        super().__init__()
        self.POPUP = None
        self.friend_requests = friend_requests
    
        print(f"Current number of friend requests : {len(self.friend_requests)}")

    def destroy(self):
        print("DESTROYING MYSELF (MANAGE DEMANDS)")
        self.POPUP.accept()

        self.close()
        self.deleteLater()

    def perform_ui_operation(self, operation):
        if operation == "destroy":
            self.destroy()
        else:
            pass

    def gen_ui(self, POPUP):
        self.POPUP = POPUP

        #setup of basic layout
        self.POPUP.setWindowTitle('Manage Friends')
        self.POPUP.resize(500, 800)
        self.POPUP.setMinimumSize(QtCore.QSize(500, 800))
        self.POPUP.setMaximumSize(QtCore.QSize(500, 800))
        self.POPUP.setAutoFillBackground(False)
        self.POPUP.setStyleSheet("background-color: #59536D;")

        self.scroll_area = QScrollArea(self.POPUP)
        self.scroll_area.setGeometry(25, 180, 450, 590)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #d4cbb6;\n""border: none;\n""border-radius: 10px;")
        

        self.scroll_widget = QWidget(self.scroll_area)
        self.scroll_widget.setStyleSheet("background-color: #00FFFFFF;\n""border: 2px solid black;\n""border-radius: 10px;")
        
        scroll_layout = QVBoxLayout(self.scroll_widget)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #setup of 'add friend' part
        self.add_friend_frame = QWidget(self.POPUP)
        self.add_friend_frame.setGeometry(35, 10, 430, 155)
        self.add_friend_frame.setStyleSheet("background-color: #d4cbb6;\n""border: 2px solid black;\n""border-radius: 10px;")
        
        form_layout = QVBoxLayout(self.add_friend_frame)
        text_input_and_button_layout = QHBoxLayout()

        self.label = QLabel("Add a Friend :")
        self.label.setStyleSheet("border: none;\n""font-size: 20px;\n""color: black;")

        self.form_input = QLineEdit()
        self.form_input.setPlaceholderText("Username")
        self.form_input.setStyleSheet("color: black;\n""background-color: white;\n")
        self.form_input.setFixedHeight(40)

        self.send_button = QPushButton("Add friend")
        self.send_button.setStyleSheet("background-color: #019210;\n""font-weight: bold;")

        form_layout.addWidget(self.label)
        form_layout.addLayout(text_input_and_button_layout)
        
        text_input_and_button_layout.addWidget(self.form_input)
        text_input_and_button_layout.addWidget(self.send_button)


        #setup of 'friend requests' part

        self.frames = []
        self.button_lists = []

        
        for request in self.friend_requests:

            frame = QWidget(self.POPUP)
            frame_layout = QVBoxLayout(frame)

            frame.setMinimumHeight(140)
            frame.setMaximumHeight(200)
            frame.setFixedWidth(350)

            frame.setStyleSheet("background-color: #DCAB5F;\n""border: 2px solid black;\n""border-radius: 20px")

            label = QLabel(f"Friend request from {request[1]}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("border: 20px solid #00000000;\n")
        
            button1 = QPushButton("ACCEPT")
            button2 = QPushButton("DENY")

            button1.setFixedWidth(150)
            button2.setFixedWidth(150)
        
            button1.setStyleSheet("background-color: #65b891;\n""font-weight: bolder;\n""border-radius: 10px;")
            button2.setStyleSheet("background-color: #a34545;\n""font-weight: bolder;\n""border-radius: 10px;")

            button_layout = QHBoxLayout()
            button_layout.addWidget(button1)
            button_layout.addWidget(button2)

            button_layout.setContentsMargins(0, 0, 0, 20)

            frame_layout.addWidget(label)
            frame_layout.addLayout(button_layout)

            scroll_layout.addWidget(frame)

            self.frames.append(frame)
            self.button_lists.append([button1, button2, request[0]])

        
        if len(self.friend_requests) == 0:
            frame = QWidget(self.POPUP)
            frame_layout = QVBoxLayout(frame)

            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame.setMinimumHeight(140)
            frame.setMaximumHeight(200)
            frame.setStyleSheet("background-color: #DCAB5F;\n""border: 2px solid black;\n""border-radius: 20px")
            
            label = QLabel("No friend requests right now")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("border: 20px solid #00000000;\n")
            frame_layout.addWidget(label)

            scroll_layout.addWidget(frame)
        else:
            pass

        self.scroll_area.setWidget(self.scroll_widget)





