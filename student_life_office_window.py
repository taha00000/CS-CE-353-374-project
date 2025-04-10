import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from datetime import datetime
from db_manager import db_manager


class StudentLifeOfficeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Student Life Office Requests")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.db = db_manager()

        self.lbl_requests = QLabel("Pending Requests:")
        layout.addWidget(self.lbl_requests)

        self.table_requests = QTableWidget()
        self.table_requests.setColumnCount(4)
        self.table_requests.setHorizontalHeaderLabels(
            ["Request ID", "Resource ID", "Borrower ID", "Due Date"]
        )
        layout.addWidget(self.table_requests)

        self.btn_approve = QPushButton("Approve Request")
        self.btn_reject = QPushButton("Reject Request")
        self.btn_approve.clicked.connect(self.approve_request)
        layout.addWidget(self.btn_approve)
        layout.addWidget(self.btn_reject)

        self.setLayout(layout)
        self.load_requests()

    def load_requests(self):
        requests = [
            {
                "request_id": 1,
                "resource_id": 101,
                "borrower_id": 201,
                "due_date": "10/15/2023",
            },
            {
                "request_id": 2,
                "resource_id": 102,
                "borrower_id": 202,
                "due_date": "10/18/2023",
            },
        ]

        self.db.connect()

        self.db.cursor.execute("SELECT * FROM Resource_Request")

        for row_data in self.db.cursor.fetchall():
            requests.append(
                {
                    "request_id": row_data[0],
                    "resource_id": row_data[1],
                    "borrower_id": row_data[2],
                    "due_date": row_data[3].strftime("%Y-%m-%d"),
                }
            )

        self.db.close_connection()
        self.table_requests.setRowCount(len(requests))
        for i, request in enumerate(requests):
            self.table_requests.setItem(
                i, 0, QTableWidgetItem(str(request["request_id"]))
            )
            self.table_requests.setItem(
                i, 1, QTableWidgetItem(str(request["resource_id"]))
            )
            self.table_requests.setItem(
                i, 2, QTableWidgetItem(str(request["borrower_id"]))
            )
            self.table_requests.setItem(i, 3, QTableWidgetItem(request["due_date"]))

    def approve_request(self):
        selected_row = self.table_requests.currentRow()
        if selected_row != -1:
            request_id = self.table_requests.item(selected_row, 0).text()
            print(f"Approved Request ID: {request_id}")


# def main():
#     app = QApplication(sys.argv)
#     window = StudentLifeOfficeWindow()
#     requests = [
#         {
#             "request_id": 1,
#             "resource_id": 101,
#             "borrower_id": 201,
#             "due_date": "10/15/2023",
#         },
#         {
#             "request_id": 2,
#             "resource_id": 102,
#             "borrower_id": 202,
#             "due_date": "10/18/2023",
#         },
#     ]
#     window.load_requests(requests)
#     window.show()
#     sys.exit(app.exec())
