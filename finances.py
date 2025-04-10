import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QComboBox,
    QPushButton,
)
import matplotlib.pyplot as plt
from db_manager import db_manager


class FinancialDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Dashboard")
        self.setGeometry(100, 100, 800, 500)

        self.db = db_manager()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.club_dropdown = QComboBox()

        self.db.connect()

        self.db.cursor.execute("SELECT Club_Name FROM Club_Funds_Tracker")

        clubs = []
        for row_data in self.db.cursor.fetchall():
            clubs.append(row_data[0])

        print(clubs)

        self.db.close_connection()

        self.club_dropdown.addItems(
            # ["Science Club", "Literature Club", "Music Club"]
            clubs
        )  # Add club names
        self.club_dropdown.currentIndexChanged.connect(self.populate_table)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(
            ["Purpose", "Amount", "Final Balance"]
        )

        self.graph_button = QPushButton("Show Graph")
        self.graph_button.clicked.connect(self.show_graph)

        layout.addWidget(QLabel("Select Club:"))
        layout.addWidget(self.club_dropdown)
        layout.addWidget(QLabel("Financial Details"))
        layout.addWidget(self.table_widget)
        layout.addWidget(self.graph_button)

        central_widget.setLayout(layout)

        self.populate_table()

    def populate_table(self):
        # Dummy financial data (replace with data from your database based on the selected club)
        club_finances = {
            "Science Club": [
                ("Equipment Purchase", -500),
                ("Event Earnings", 800),
                ("Event Expenses", -300),
                ("Donation", 200),
            ],
            "Literature Club": [
                ("Book Purchase", -400),
                ("Workshop Expenses", -200),
                ("Membership Fee", 100),
            ],
            "Music Club": [
                ("Instrument Rental", -600),
                ("Concert Earnings", 1000),
                ("Concert Expenses", -400),
                ("Sponsorship", 300),
            ],
        }

        # db part for retrieving finance details

        self.db.connect()

        self.db.cursor.execute("SELECT * FROM Club_Funds_Tracker")

        # for row_index, row_data in enumerate(self.db.cursor.fetchall()):
        #     print(row_data)
        #     club_finances.update({row_data[0]:(row_data[2], str(row_data[1]))})
        for row_index, row_data in enumerate(self.db.cursor.fetchall()):
            club_name = row_data[0]
            amount = row_data[1]
            purpose = row_data[2]
            # Check if the club exists in club_finances, if not, add it with an empty list
            if club_name not in club_finances:
                club_finances[club_name] = []
            # Append a tuple with purpose and amount to the club's finances list
            club_finances[club_name].append((purpose, amount))
        print(club_finances)
        
        self.db.close_connection()

        selected_club = self.club_dropdown.currentText()
        finances = club_finances.get(selected_club, [])

        self.table_widget.setRowCount(len(finances))
        final_balance = 0
        for row, (purpose, amount) in enumerate(finances):
            final_balance += amount
            self.table_widget.setItem(row, 0, QTableWidgetItem(purpose))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(amount)))
            self.table_widget.setItem(row, 2, QTableWidgetItem(str(final_balance)))

        self.financial_data = finances
        print(self.financial_data)

    def show_graph(self):
        if not hasattr(self, "financial_data"):
            return

        final_balance = 0

        x_labels = [data[0] for data in self.financial_data]
        # y_values = [
        #     final_balance + int(data[1]) for data in self.financial_data
        # ]  # Use the final balance data

        y_values = []
        for y in self.financial_data:
            print(y)
            final_balance += int(y[1])
            y_values.append(final_balance)


        plt.figure(figsize=(8, 5))
        plt.plot(
            x_labels,
            y_values,
            marker="o",
            color="skyblue",
            linestyle="-",
            linewidth=2,
            markersize=8,
        )
        plt.xlabel("Purpose")
        plt.ylabel("Amount (PKR)")
        plt.title("Financial Standing and Final Balance")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


# def main():
#     app = QApplication(sys.argv)
#     window = FinancialDashboard()
#     window.show()
#     sys.exit(app.exec())


# if __name__ == "__main__":
#     main()
