import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication


class viewResources(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(viewResources, self).__init__()

        # Load the .ui file
        uic.loadUi("view_resource.ui", self)

    # def view_resouces(self):

