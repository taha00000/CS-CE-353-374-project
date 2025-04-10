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


# Main Window Class
class db_manager(QtWidgets.QMainWindow):
    # server = 'HU-DOPX-GCL11\MSSQLSERVER02'
    server = "CTRL-ALT-DEL\SPARTA"  # specific to my machine only
    # database = "Student Life"  # Name of your Northwind database
    database = "Trial database"  # Name of your Northwind database
    # use_windows_authentication = False  # Set to True to use Windows Authentication
    use_windows_authentication = True  # Set to True to use Windows Authentication
    username = "sa"  # Specify a username if not using Windows Authentication
    password = "Fall2022.dbms"  # Specify a password if not using Windows Authentication
    cursor = None

    def __init__(self):
        # Call the inherited classes __init__ method
        super(db_manager, self).__init__()
        # Create the connection string based on the authentication method chosen
        if self.use_windows_authentication:
            self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
        else:
            self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"

    def connect(self):
        self.connection = pyodbc.connect(self.connection_string)
        self.cursor = self.connection.cursor()

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Query execution error: {str(e)}")

    def commit(self):
        self.connection.commit()

    def close_connection(self):
        self.connection.close()
