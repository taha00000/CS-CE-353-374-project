import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication


from borrow_resource_window import BorrowResourceWindow
from student_account_window import StudentAccountWindow
from event_input import EventInput
from view_attendance import ViewAttendanceWindow
from event_feedback_window import EventFeedbackWindow

class welcomeScreenStudent(QtWidgets.QMainWindow):
    def __init__(self, username):
        # Call the inherited classes __init__ method
        super(welcomeScreenStudent, self).__init__()

        # Load the .ui file
        uic.loadUi("welcome_screen_student.ui", self)
        self.label_2.setText("Welcome, " + username)

        self.viewBorrowedResources.clicked.connect(self.vbr)
        self.requestResource.clicked.connect(self.req_r)
        self.requestEvent.clicked.connect(self.req_e)
        self.eventFeedback.clicked.connect(self.ef)
        self.viewAttendance.clicked.connect(self.view_attendance)

    # * view borrowed resources
    def vbr(self):
        self.hide()
        self.bor_res_win = StudentAccountWindow()
        self.bor_res_win.show()

    #*  request resources
    def req_r(self):
        self.hide()
        self.req_res = BorrowResourceWindow()
        self.req_res.show()

    # * request events
    def req_e(self):
        self.hide()
        self.req_ev = EventInput()
        self.req_ev.show()

    # * view attendance
    def view_attendance(self):
        self.hide()
        self.attendance = ViewAttendanceWindow()
        self.attendance.show()

    # * event feedback
    def ef(self):
        self.hide()
        self.event_fb = EventFeedbackWindow()
        self.event_fb.show()
