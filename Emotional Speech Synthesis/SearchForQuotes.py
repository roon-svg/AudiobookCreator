from PySide6.QtGui import QTextCharFormat, QTextCursor, Qt
import re
from PySide6.QtWidgets import QTextEdit

class QuoteSearch:
    def __init__(self, textArea: QTextEdit):
        self.textArea = textArea
        # This sets up the highlihting format for the quotes, which is light gray
        format = QTextCharFormat()
        format.setBackground(Qt.lightGray)
        self.format = format

        #self.pattern = [r'"(.*?)"|(?<!\w)\'(.*?)\'(?<!\w)']
        self.pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"|\b\'([^\'\\]*(?:\\.[^\'\\]*)*)\'\b'

    def searchForQuotes(self):
        results = []
        
        text = self.textArea.toPlainText()
        cursor = self.textArea.textCursor()

        self.textArea.blockSignals(True)  # Disable signals to prevent UI updates during processing

        # This goes through the text and finds any quotes, then adds them to a list and highlights them in the text area
        for pattern in self.pattern:
            for match in re.finditer(pattern, text):
                quote = match.group()
                results.append(quote)
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(self.format)

                self.textArea.blockSignals(False)  # Re-enable signals after processing
        return results