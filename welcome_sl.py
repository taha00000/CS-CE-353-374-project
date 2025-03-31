import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication

from view_resources import viewResources
from club_info import ClubInfo
from sl_view_events import PastEventsWindow
from student_life_office_window import StudentLifeOfficeWindow
from event_requests_window import EventRequestsWindow
from finances import FinancialDashboard

class welcomeScreenSL(QtWidgets.QMainWindow):
    def __init__(self, username):
        # Call the inherited classes __init__ method
        super(welcomeScreenSL, self).__init__()

        # Load the .ui file
        uic.loadUi("welcome_screen.ui", self)
        self.label_2.setText("Welcome, " + username)

        # connecting the buttons to the windows
        self.viewResources.clicked.connect(self.vr)
        self.viewClubs.clicked.connect(self.clubs)
        self.viewEvents.clicked.connect(self.view_events)
        self.resourceRequests.clicked.connect(self.rr)
        self.eventRequests.clicked.connect(self.er)
        self.clubFinances.clicked.connect(self.cf)

    # view resources
    def vr(self):
        self.hide()
        self.res_win = viewResources()
        self.res_win.show()

    # view clubs
    def clubs(self):
        self.hide()
        self.club_win = ClubInfo()
        self.club_win.show()

    # * view events
    def view_events(self):
        self.hide()
        self.events_win = PastEventsWindow()
        self.events_win.show()
    
    # * resource requests
    def rr(self):
        self.hide()
        self.res_req = StudentLifeOfficeWindow()
        self.res_req.show()
    
    # * event requests
    def er(self):
        self.hide()
        self.events_req = EventRequestsWindow()
        self.events_req.show()

    # * club finances
    def cf(self):
        self.hide()
        self.club_fin = FinancialDashboard()
        self.club_fin.show()