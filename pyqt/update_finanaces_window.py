from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from decimal import Decimal

from db_manager import db_manager


class UpdateFinancesWindow(QMainWindow):
    def __init__(self, selected_club):
        super().__init__()
        self.db = db_manager()
        self.setWindowTitle("Update Finances")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()

        reason_label = QLabel("Reason:")
        self.reason_input = QLineEdit()

        update_button = QPushButton("Update Finances")
        update_button.clicked.connect(lambda: self.update_finances(selected_club))

        layout.addWidget(amount_label)
        layout.addWidget(self.amount_input)
        layout.addWidget(reason_label)
        layout.addWidget(self.reason_input)
        layout.addWidget(update_button)

        central_widget.setLayout(layout)

    def update_finances(self, selected_club):
        amount = self.amount_input.text()
        reason = self.reason_input.text()

        self.db.connect()
        self.db.cursor.execute(
            """
            UPDATE Club_Funds_Tracker
            SET Amount = Amount + ?, Reason = ?
            WHERE Club_Name = ?
            """,
            (Decimal(amount), reason, selected_club),
        )
        self.db.cursor.commit()
        self.db.close_connection()
        print("Amount:", amount)
        print("Reason:", reason)
