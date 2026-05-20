from PySide6.QtCore import *
import os
import sys
from PySide6.QtWidgets import *

class OpenFile:
    def __init__(self, textArea: QTextEdit):
        self.textArea = textArea

    def OpenFile(self):
        filePath, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if filePath:
            try:
                # If the file size is too large then a warning message appears
                maxFileSize = 5 * 1024 * 1024  # 5 MB
                if os.path.getsize(filePath) > maxFileSize:
                    QMessageBox.warning(self, "File Too Large", "The selected file is too large. Please select a file smaller than 5 MB.")
                    return

                # This opens the file and sets the text area to the content of the file
                with open(filePath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    self.textArea.setPlainText(content)
                    self.setWindowTitle(f"Emotional Speech Synthesis - {filePath}")
                    self.statusBar().showMessage(f"Opened file: {filePath}")
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Could not open file: {e}")
