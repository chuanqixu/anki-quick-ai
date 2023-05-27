from aqt import mw

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QDialog, QTextEdit



class RunDialog(QDialog):
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.initUI(query)

    def initUI(self, query):
        config = mw.addonManager.getConfig(__name__)

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Browse query
        input_layout = QHBoxLayout()
        explanation_label = QLabel("Browse Query:")
        input_layout.addWidget(explanation_label)
        self.input_field_browse_query = QLineEdit(query)
        input_layout.addWidget(self.input_field_browse_query)
        layout.addLayout(input_layout)

        # note field
        input_layout = QHBoxLayout()
        explanation_label = QLabel("Note Field:")
        input_layout.addWidget(explanation_label)
        self.input_field_note_field = QLineEdit(config["note_field"])
        input_layout.addWidget(self.input_field_note_field)
        layout.addLayout(input_layout)

        # Instruction
        label = QLabel("Whether to run the add-on \"Anki Quick AI\"?\nIt may take seconds for AI to generate contents, and another seconds for sound generation,\ndepending on the length of the prompts.")
        layout.addWidget(label)

        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(self.run_button, 0, Qt.AlignCenter)  # align button to the center

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(cancel_button, 0, Qt.AlignCenter)  # align button to the center



class ResponseDialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.settings = QSettings('Anki', 'Anki Quick AI')

        self.text_edit = QTextEdit(self)
        self.text_edit.setHtml(text)
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)

        # Restore the previous size of the dialog
        size = self.settings.value('DialogSize')
        if size:
            self.resize(size)
        else:
            self.resize(800, 600)  # Set default size

    def closeEvent(self, event):
        # Save the current size of the dialog when it's closed
        self.settings.setValue('DialogSize', self.size())
        super().closeEvent(event)
