from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow


class Application:
    def __init__(self, argv):
        self.qapp = QApplication(argv)
        self.qapp.setApplicationName("ConvertTools")
        self.qapp.setOrganizationName("ConvertTools")
        self.window = MainWindow()

    def run(self):
        self.window.show()
        return self.qapp.exec()
