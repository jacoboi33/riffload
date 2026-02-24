import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.ui.main_window import MainWindow

ASSETS = Path(__file__).parent / "assets"


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Riffload")
    app.setApplicationDisplayName("Riffload")
    app.setWindowIcon(QIcon(str(ASSETS / "logo.png")))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
