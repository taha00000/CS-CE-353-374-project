from PyQt6 import QtWidgets, uic

from update_finanaces_window import UpdateFinancesWindow
from db_manager import db_manager


class ClubInfo(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("club_info.ui", self)
        self.db = db_manager()
        clubs = []
        self.db.connect()
        self.db.cursor.execute("SELECT Club_Name FROM Clubs")
        for r in self.db.cursor.fetchall():
            clubs.append(r[0])
        print(clubs)
        self.db.close_connection()
        self.club_combo_box.addItems(clubs)
        self.club_combo_box.currentIndexChanged.connect(
            lambda: self.populate(self.club_combo_box.currentText())
        )
        self.update_funds_btn.clicked.connect(self.updateFinances)

    def populate(self, selected_club):
        print(selected_club)
        self.db.connect()
        self.db.cursor.execute(
            "SELECT SUM(AMOUNT) FROM Club_Funds_Tracker WHERE Club_Name = ?",
            selected_club,
        )
        for row_data in self.db.cursor.fetchall():
            total_funds = str(row_data[0])
        self.db.close_connection()
        self.funds_text_edit.setText(total_funds)

    def updateFinances(self):
        self.hide()
        self.uf = UpdateFinancesWindow(self.club_combo_box.currentText())
        self.uf.show()
