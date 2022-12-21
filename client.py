from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QGridLayout,
    QWidget,
    QLabel,
)
from PyQt6.QtGui import QFont
from PyQt6 import QtCore
import threading
import socket


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clicked = []
        self.timers = []
        self.server_events = []
        self.setWindowTitle("Змейка")
        self.clicked_nums = []
        self.my_step = False
        self.game_table = QGridLayout()
        self.game_table.rowMinimumHeight(10)
        self.game_table.columnMinimumWidth(9)
        self.snake1 = []
        self.snake2 = []
        self.alert_label = QLabel()
        self.alert_label.setFont(QFont("Times", 20))
        self.game_table.addWidget(self.alert_label, 10, 2, 1, 4)
        self.user1_step = False
        self.user2_step = False
        self.widgets = {}

        for i in range(10):
            for j in range(10):

                btn = QPushButton("")
                btn.setFont(QFont("Times", 20))
                btn.setStyleSheet("QPushButton {background-color: #FFFFFF;}")
                btn.setFixedSize(60, 60)
                btn.clicked.connect(lambda _, r=i, c=j: self.btn_click(r, c))
                self.game_table.addWidget(btn, i, j)
                self.widgets[(i, j)] = btn

        widget = QWidget()
        widget.setLayout(self.game_table)
        self.setCentralWidget(widget)

    def btn_click(self, i, j, from_server=False):
        if len(self.snake1) <= len(self.snake2):
            self.user1_step = True
            self.user2_step = False
        else:
            self.user1_step = False
            self.user2_step = True
        click = int(str(i) + str(j))
        if from_server:
            if click not in self.clicked_nums and self.user1_step is True:
                if click not in self.snake1 and len(self.snake1) < 1:
                    self.snake1.append(click)
                    self.clicked_nums.append(int(str(i) + str(j)))
                    self.widgets[(i, j)].setStyleSheet("QPushButton {background-color: #FF0000;}")
                elif click not in self.snake1 and len(self.snake1) >= 1:
                    last_num1 = int(self.snake1[-1])
                    if (
                        last_num1 + 1 == int(click) or last_num1 - 1 == int(click) or last_num1 - 10 == int(click) or last_num1 + 10 == int(click)
                    ) and (click not in self.snake1):
                        self.snake1.append(click)
                        self.clicked_nums.append(click)
                        self.widgets[(i, j)].setStyleSheet("QPushButton {background-color: #FF0000;}")
                    if (
                        ((click + 1 in self.clicked_nums) and (click + 1 != last_num1))
                        or ((click + 10 in self.clicked_nums) and (click + 10 != last_num1))
                        or ((click - 1 in self.clicked_nums) and (click - 1 != last_num1))
                        or ((click - 10 in self.clicked_nums) and (click - 10 != last_num1))
                    ):
                        self.snake1.append(click)
                        self.widgets[(i, j)].setStyleSheet("QPushButton {background-color: #FF0000;}")
                        self.alert_label.setStyleSheet("QLabel {color: #008000;}")
                        window.alert_label.setText("Победа")
                        self.my_step = False
                        timer.stop()
                        self.game_table.update()
                        return 0
        else:
            if click not in self.clicked_nums and self.my_step is True:
                if click not in self.snake2 and len(self.snake2) < 1:
                    self.widgets[(i, j)].setStyleSheet("QPushButton {background-color: #0000FF;}")
                    self.snake2.append(click)
                    self.clicked_nums.append(click)
                elif click not in self.snake2 and len(self.snake2) >= 1:
                    last_num2 = int(self.snake2[-1])
                    if (
                        last_num2 + 1 == int(click) or last_num2 - 1 == int(click) or last_num2 - 10 == int(click) or last_num2 + 10 == int(click)
                    ) and (click not in self.snake2):
                        self.snake2.append(click)
                        self.clicked_nums.append(int(str(i) + str(j)))
                        self.widgets[(i, j)].setStyleSheet("QPushButton {background-color: #0000FF;}")
                    else:
                        return False
                    if (
                        ((click + 1 in self.clicked_nums) and (click + 1 != last_num2))
                        or ((click + 10 in self.clicked_nums) and (click + 10 != last_num2))
                        or ((click - 1 in self.clicked_nums) and (click - 1 != last_num2))
                        or ((click - 10 in self.clicked_nums) and (click - 10 != last_num2))
                    ):
                        self.snake2.append(click)
                        self.clicked_nums.append(int(str(i) + str(j)))
                        self.widgets[(i, j)].setStyleSheet("QPushButton {background-color: #0000FF;}")
                        server.send((str(i) + "_" + str(j)).encode("utf8"))
                        result = "Поражение"
                        self.alert_label.setStyleSheet("QLabel {color: #FF2222;}")
                        self.alert_label.setText(result)
                        self.my_step = False
                        timer.stop()
                        self.game_table.update()
                        return 0

        if (i, j) in window.clicked or (not self.my_step and not from_server):
            return 0
        if not from_server:
            server.send((str(i) + "_" + str(j)).encode("utf8"))
        self.clicked.append((i, j))


def tick():
    if window.server_events:
        if window.server_events[0] == "Ход противника":
            window.my_step = False
            window.alert_label.setText("Ход противника")
        elif window.server_events[0] == "Твой ход":
            window.my_step = True
            window.alert_label.setText("Ваш ход")
        else:
            i, j = window.server_events[0].split("_")
            window.btn_click(int(i), int(j), from_server=True)
        window.game_table.update()
        window.server_events.pop(0)


def server_listener():
    while True:
        window.server_events.append(server.recv(1024).decode("utf8"))


server = socket.socket()
server.connect(("localhost", 50008))
app = QApplication([])
window = MainWindow()
window.show()
timer = QtCore.QTimer()
timer.timeout.connect(tick)
timer.start(100)

threading.Thread(target=server_listener, daemon=True).start()
app.exec()
