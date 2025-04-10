import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
)


class EventFeedbackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.student_id = 'S1223'
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Event Feedback")
        self.setGeometry(100, 100, 400, 300)

        self.lbl_student = QLabel(f"Student ID: {self.student_id}")
        self.lbl_select_event = QLabel("Select the Event:")
        self.cb_event = QComboBox()
        self.cb_event.addItem("DiscO")
        self.cb_event.addItem("Event 2")
        self.cb_event.addItem("Event 3")
        self.lbl_feedback = QLabel("Provide Feedback:")
        self.txt_feedback = QTextEdit()
        self.btn_submit = QPushButton("Submit Feedback")
        self.btn_submit.clicked.connect(self.submit_feedback)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_student)
        layout.addWidget(self.lbl_select_event)
        layout.addWidget(self.cb_event)
        layout.addWidget(self.lbl_feedback)
        layout.addWidget(self.txt_feedback)
        layout.addWidget(self.btn_submit)
        self.setLayout(layout)

    def submit_feedback(self):
        selected_event = self.cb_event.currentText()
        feedback_text = self.txt_feedback.toPlainText()
        print(f"Student ID: {self.student_id}")
        print(f"Selected Event: {selected_event}")
        print(f"Feedback: {feedback_text}")
