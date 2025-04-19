# Importing essential modules
from PyQt6.QtWidgets import QApplication

from login import Login
import sys

def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
