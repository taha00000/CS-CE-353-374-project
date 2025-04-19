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
import sys
import pyodbc

# Replace these with your own database connection details
# server = 'HU-DOPX-GCL11\MSSQLSERVER02'
server = "CTRL-ALT-DEL\SPARTA"  # specific to my machine only
database = "Student Life"  # Name of your Northwind database
# use_windows_authentication = False  # Set to True to use Windows Authentication
use_windows_authentication = True  # Set to True to use Windows Authentication
username = "sa"  # Specify a username if not using Windows Authentication
password = "Fall2022.dbms"  # Specify a password if not using Windows Authentication


# Create the connection string based on the authentication method chosen
if use_windows_authentication:
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
else:
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"


# Main Window Class
class Login(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(Login, self).__init__()

        # Load the .ui file
        uic.loadUi("login.ui", self)
        self.login_btn.clicked.connect(self.loginBtn)

    def loginBtn(self):
        # ? determining user type
        temp = self.userID.toPlainText().strip().split("@")
        if temp[1][:2] == "st":
            usertype = "Student"
        else:
            usertype = "SL"
        del temp
        print(usertype)

        # printing out password for testing purposes
        print(self.passwordEntry.text())
        self.userID.setPlainText("")
        self.passwordEntry.setText("")

        self.hide()
        self.club_info = welcomeScreenSL()
        self.club_info.show()


class welcomeScreenSL(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(welcomeScreenSL, self).__init__()

        # Load the .ui file
        uic.loadUi("welcome_screen.ui", self)


def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
