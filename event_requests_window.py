import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from db_manager import db_manager

class EventRequestsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.db = db_manager()

    def init_ui(self):
        self.setWindowTitle("Event Requests")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.lbl_requests = QLabel("Event Requests:")
        layout.addWidget(self.lbl_requests)

        self.table_requests = QTableWidget()
        self.table_requests.setColumnCount(4)
        self.table_requests.setHorizontalHeaderLabels(
            ["Event Request ID", "Club Name", "Event Name", "Event Description"]
        )
        layout.addWidget(self.table_requests)

        self.btn_approve = QPushButton("Approve Event")
        self.btn_approve.clicked.connect(self.approve_event)
        layout.addWidget(self.btn_approve)

        self.btn_reject = QPushButton("Reject Event")
        layout.addWidget(self.btn_reject)

        central_widget.setLayout(layout)

    def load_event_requests(self):
        event_requests = [
            {
                "event_request_id": 1,
                "club_name": "Science Club",
                "event_name": "Science Fair",
                "event_description": "An exhibition of science projects",
            },
            {
                "event_request_id": 2,
                "club_name": "Music Club",
                "event_name": "Concert",
                "event_description": "Live music performance",
            },
        ]
        self.table_requests.setRowCount(len(event_requests))
        for i, request in enumerate(event_requests):
            self.table_requests.setItem(
                i, 0, QTableWidgetItem(str(request["event_request_id"]))
            )
            self.table_requests.setItem(i, 1, QTableWidgetItem(request["club_name"]))
            self.table_requests.setItem(i, 2, QTableWidgetItem(request["event_name"]))
            self.table_requests.setItem(
                i, 3, QTableWidgetItem(request["event_description"])
            )

    def approve_event(self):
        selected_row = self.table_requests.currentRow()
        if selected_row != -1:
            event_request_id = self.table_requests.item(selected_row, 0).text()
            print(f"Approved Event Request ID: {event_request_id}")
