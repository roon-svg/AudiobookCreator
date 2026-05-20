import sys
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import TextArea
import AudioSynthesis
import SearchForQuotes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # This is setting up the window title and geometry
        self.setWindowTitle("Audiobook Maker")
        self.setGeometry(100, 100, 600, 400)

        # This os setting up the text boxc
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        mainLayout = QVBoxLayout(self.centralWidget)

        # This sets up the text area
        self.textArea = QTextEdit()
        mainLayout.addWidget(self.textArea)

        # This sets up the header
        headerLayout = QHBoxLayout()
        self.createHeader(headerLayout)
        mainLayout.addLayout(headerLayout)


        self.current_file = None

    def createHeader(self, headerLayout):
        # Here are all of the different buttons that are going to be on the header
        button_file = QPushButton("File")
        button_anger = QPushButton("Anger")
        button_sadness = QPushButton("Sadness")
        button_happiness = QPushButton("Happiness")
        button_neutral = QPushButton("Neutral")
        button_search = QPushButton("Search")
        button_make = QPushButton("Make Audiobook")

        headerLayout.addStretch()
        headerLayout.addWidget(button_file)
        headerLayout.addWidget(button_anger)
        headerLayout.addWidget(button_sadness)
        headerLayout.addWidget(button_happiness)
        headerLayout.addWidget(button_neutral)
        headerLayout.addWidget(button_search)
        headerLayout.addWidget(button_make)

        self.SearchForQuotes = SearchForQuotes.QuoteSearch(self.textArea)
        self.TextArea = TextArea.OpenFile(self.textArea)
        self.AudioSynthesis = AudioSynthesis.AudioSynthesier(self.textArea)


        # This allows for the buttons to do functions when clicked
        button_file.clicked.connect(self.TextArea.OpenFile)
        button_anger.clicked.connect(lambda: self.apply_emotion("Anger"))
        button_sadness.clicked.connect(lambda: self.apply_emotion("Sadness"))
        button_happiness.clicked.connect(lambda: self.apply_emotion("Happiness"))
        button_neutral.clicked.connect(lambda: self.apply_emotion("Neutral"))
        button_search.clicked.connect(lambda: self.SearchForQuotes.searchForQuotes())
        button_make.clicked.connect(lambda: self.AudioSynthesis.MakeAudiobook())
    

    def apply_emotion(self, emotion):
        cursor = self.textArea.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            if emotion == "Anger":
                fmt.setBackground(QColor("red"))
            elif emotion == "Sadness":
                fmt.setBackground(QColor("blue"))
            elif emotion == "Happiness":
                fmt.setBackground(QColor("yellow"))
            elif emotion == "Neutral":
                fmt.setBackground(QBrush(Qt.transparent))
            cursor.mergeCharFormat(fmt)
        else:
            self.statusBar().showMessage("ERROR: Not able to highlight")
