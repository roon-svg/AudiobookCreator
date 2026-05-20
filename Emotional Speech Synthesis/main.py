from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import MainWindow
import sys

print("Hello")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Make and show window
    editor = MainWindow.MainWindow()
    editor.show()
    
    # this allows the application to run until the user closes it
    sys.exit(app.exec())

