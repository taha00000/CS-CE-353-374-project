# Importing essential modules
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from welcome_sl import welcomeScreenSL
from welcome_student import welcomeScreenStudent
from db_manager import db_manager
import sys


class Login(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(Login, self).__init__()

        # Load the .ui file
        uic.loadUi("login.ui", self)
        self.login_btn.clicked.connect(self.loginBtn)

    def loginBtn(self):
        # ? determining user type
        if "@" in self.userID.toPlainText():
            temp = self.userID.toPlainText().strip().split("@")
            username = temp[0]
            if temp[1][:2] == "st":
                usertype = "Student"
            else:
                usertype = "SL"
            del temp
            print(usertype)

            # printing out password for testing purposes
            print(self.passwordEntry.text())
            self.hide()
            if usertype == "SL":
                self.club_info = welcomeScreenSL(username)
            else:
                self.club_info = welcomeScreenStudent(username)
            self.club_info.show()
        else:
            print("Invalid email, please re-enter!")
        self.userID.setPlainText("")
        self.passwordEntry.setText("")
