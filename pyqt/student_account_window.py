import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from db_manager import db_manager


class StudentAccountWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.student_id = "S1234"
        self.db = db_manager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Student Resource Account")
        self.setGeometry(100, 100, 600, 400)

        borrowed_resources = [
            {
                "resource_id": "001",
                "resource_name": "Microphone",
                "due_date": "2023-11-30",
            },
            {"resource_id": "002", "resource_name": "Camera", "due_date": "2023-12-15"},
            {
                "resource_id": "003",
                "resource_name": "Flash drive",
                "due_date": "2023-12-10",
            },
        ]

        # ? fetching from database
        self.db.connect()
        self.db.cursor.execute(
            """
            SELECT *
            FROM Borrowed_Resources
            WHERE Borrower_ID in
            (
            SELECT Borrower_ID
            FROM Borrower
            WHERE Student_ID = 1
            );
            """
            # need to fix the checking of student-id
        )

        # print(self.db.cursor.fetchall())

        for row_index, row_data in enumerate(self.db.cursor.fetchall()):
            print(row_index, row_data)
            borrowed_resources.append(
                {
                    "resource_id": str(row_data[1]).zfill(3),
                    "resource_name": "Joe mama",
                    "due_date": row_data[3].strftime("%Y-%M-%D"),
                }
            )

        # borrowed_resources = None

        self.lbl_account = QLabel(f"Student Account: {self.student_id}")
        self.table_account = QTableWidget()
        self.table_account.setColumnCount(3)
        self.table_account.setHorizontalHeaderLabels(
            ["Resource ID", "Resource Name", "Due Date"]
        )
        self.table_account.setRowCount(len(borrowed_resources))

        self.db.close_connection()

        for row, resource in enumerate(borrowed_resources):
            self.table_account.setItem(
                row, 0, QTableWidgetItem(resource["resource_id"])
            )
            self.table_account.setItem(
                row, 1, QTableWidgetItem(resource["resource_name"])
            )
            self.table_account.setItem(row, 2, QTableWidgetItem(resource["due_date"]))

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_account)
        layout.addWidget(self.table_account)
        self.setLayout(layout)
