import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QVBoxLayout,
    QMessageBox,
)


class ResourceRequestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Student Resource Request")
        self.setGeometry(100, 100, 400, 150)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.lbl_resource = QLabel("Select a Resource:")
        self.resource_combobox = QComboBox()
        self.resource_combobox.addItems(
            ["Textbooks", "Laptop", "Study Room", "Lab Equipment"]
        )

        self.lbl_due_date = QLabel("Due Date (MM/DD/YYYY):")
        self.txt_due_date = QLineEdit()

        self.btn_publish_request = QPushButton("Publish Request")
        self.btn_publish_request.clicked.connect(self.publish_request)

        layout.addWidget(self.lbl_resource)
        layout.addWidget(self.resource_combobox)
        layout.addWidget(self.lbl_due_date)
        layout.addWidget(self.txt_due_date)
        layout.addWidget(self.btn_publish_request)

        central_widget.setLayout(layout)

    def publish_request(self):
        resource = self.resource_combobox.currentText()
        due_date = self.txt_due_date.text()

        if resource and due_date:
            QMessageBox.information(
                self, "Request Published", f"Resource: {resource}\nDue Date: {due_date}"
            )
        else:
            QMessageBox.critical(
                self, "Error", "Please select a resource and provide a due date."
            )