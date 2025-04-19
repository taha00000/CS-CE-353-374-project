import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QCalendarWidget,
    QPushButton,
    QWidget,
)

from datetime import date

from db_manager import db_manager


def date_converter(QDate):
    return date(QDate.year(), QDate.month(), QDate.day())


class BorrowResourceWindow(QMainWindow):
    def __init__(self, student_id="S12345"):
        super().__init__()
        self.student_id = student_id
        self.resource_names = ["Resource 1", "Resource 2", "Resource 3"]
        self.init_ui()
        self.db = db_manager()

    def init_ui(self):
        self.setWindowTitle("Borrow a Resource")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.lbl_student = QLabel(f"Student ID: {self.student_id}")
        self.lbl_select_resource = QLabel("Select a Resource:")
        self.cb_resource_names = QComboBox()
        self.cb_resource_names.addItems(self.resource_names)
        self.lbl_tentative_due_date = QLabel("Select a Tentative Due Date:")
        self.calendar_due_date = QCalendarWidget()
        self.btn_borrow = QPushButton("Request Resource")
        self.btn_borrow.clicked.connect(self.borrow_resource)

        layout.addWidget(self.lbl_student)
        layout.addWidget(self.lbl_select_resource)
        layout.addWidget(self.cb_resource_names)
        layout.addWidget(self.lbl_tentative_due_date)
        layout.addWidget(self.calendar_due_date)
        layout.addWidget(self.btn_borrow)
        central_widget.setLayout(layout)

    def borrow_resource(self):
        self.db.connect()
        selected_resource = self.cb_resource_names.currentText()
        due_date = date_converter(self.calendar_due_date.selectedDate())
        print(f"Student ID: {self.student_id}")
        print(f"Selected Resource: {selected_resource}")
        # print(f"Tentative Due Date: {due_date.strftime("%Y-%m-%d")}")
        self.db.cursor.execute(
            """
            INSERT INTO Resource_Request([Resource_Request_ID], [Resource_ID],[Borrower_ID], [Due_Date], [Approved])
            VALUES (?, ?, ?, ?, ?)
            """,
            (0, 1, 69, due_date, 0)
        )

        self.db.commit()

        # TODO: find out how auto-increment works
        self.db.close_connection()