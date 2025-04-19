from PyQt6 import QtWidgets, uic
from datetime import datetime
from db_manager import db_manager


class EventInput(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("events.ui", self)
        self.db = db_manager()
        self.request_btn.clicked.connect(self.requestEvent)

    def requestEvent(self):
        self.db.connect()

        ename = self.event_name_text_edit.toPlainText()
        cname = self.club_combo_box.currentText()
        edate = datetime.strptime(self.date_text_edit.toPlainText(), '%d-%m-%Y')
        etime = datetime.strptime(self.time_text_edit.toPlainText(), "%H:%M")
        loc = self.location_combo_box.currentText()
        budget = int(self.budget.toPlainText())

        self.db.cursor.execute(
            """
            INSERT INTO Event_Request(Event_Request_ID, Event_Name, Club_Name, Date, Time, Location, Budget, Approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (0, ename, cname, edate, etime, loc, budget),
        )

        self.db.cursor.commit()

        self.db.close_connection()
