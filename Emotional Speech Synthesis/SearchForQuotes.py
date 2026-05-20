from PySide6.QtGui import QTextCharFormat, QTextCursor, Qt
import re
from PySide6.QtWidgets import QTextEdit

class QuoteSearch:
    def __init__(self, textArea: QTextEdit):
        #self.textArea = textArea
        format = QTextCharFormat()
        format.setBackground(Qt.lightGray)
        self.format = format

        self.pattern = [r'"(.*?)"|(?<!\w)\'(.*?)\'(?<!\w)']

    def searchForQuotes(self):
        results = []
        
        text = self.textArea.toPlainText()
        cursor = self.textArea.textCursor()

        for pattern in self.pattern:
            for match in re.finditer(pattern, text):
                quote = match.group()
                results.append(quote)
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(self.format)
        return results