from aqt import mw

from aqt.browser import Browser
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDialog, QComboBox



class RunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.prompt_dict = mw.addonManager.getConfig(__name__)["prompt"]

        # prompt
        input_layout = QHBoxLayout()
        note_field_label = QLabel("Prompt:")
        input_layout.addWidget(note_field_label)
        self.prompt_box = QComboBox(self)
        self.prompt_box.addItems(self.prompt_dict.keys())
        input_layout.addWidget(self.prompt_box)
        self.prompt_box.currentIndexChanged.connect(self.prompt_changed)
        self.curr_prompt_name = self.prompt_box.currentText()
        layout.addLayout(input_layout)

        # Browse query
        if isinstance(self.parent(), Browser):
            query = self.parent().form.searchEdit.lineEdit().text()
        else:
            query = self.prompt_dict[self.curr_prompt_name]["default_query"]

        input_layout = QHBoxLayout()
        query_label = QLabel("Browse Query:")
        input_layout.addWidget(query_label)
        self.input_field_browse_query = QLineEdit(query)
        input_layout.addWidget(self.input_field_browse_query)
        layout.addLayout(input_layout)

        # Note field
        input_layout = QHBoxLayout()
        note_field_label = QLabel("Note Field:")
        input_layout.addWidget(note_field_label)
        self.input_field_note_field = QLineEdit(self.prompt_dict[self.curr_prompt_name]["default_note_field"])
        input_layout.addWidget(self.input_field_note_field)
        layout.addLayout(input_layout)

        # Instruction
        label = QLabel("Whether to run the add-on \"Anki Quick AI\"?\nIt may take seconds for AI to generate contents, and another seconds for sound generation,\ndepending on the length of the prompts.\nThis will be run in the background.\n When it finishes, a new window will pop up.")
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


    def prompt_changed(self, index):
        self.curr_prompt_name = self.prompt_box.itemData(index)
