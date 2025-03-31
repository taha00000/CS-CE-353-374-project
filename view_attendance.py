import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)


class ViewAttendanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("View Member Attendance")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        event_label = QLabel("Event Name:")
        self.event_name = QLabel("Sample Event Name")

        table_label = QLabel("Member Attendance:")
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(2)
        self.attendance_table.setHorizontalHeaderLabels(["Member Name", "Attendance"])
        self.attendance_table.setRowCount(
            5
        )  # You can adjust the number of rows based on your needs

        # Fill the table with sample attendance data
        for row in range(5):
            member_name = QTableWidgetItem("Member " + str(row + 1))
            attendance_status = QTableWidgetItem(
                "Present" if row % 2 == 0 else "Absent"
            )

            self.attendance_table.setItem(row, 0, member_name)
            self.attendance_table.setItem(row, 1, attendance_status)

        layout.addWidget(event_label)
        layout.addWidget(self.event_name)
        layout.addWidget(table_label)
        layout.addWidget(self.attendance_table)

        central_widget.setLayout(layout)