from aqt import mw

from aqt.browser import Browser
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDialog, QComboBox

from .prompt_window import PromptConfigDialog



class RunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('Anki', 'Anki Quick AI')
        self.initUI()

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.prompt_dict = mw.addonManager.getConfig(__name__)["prompt"]

        # reload last prompt name
        prompt_name = self.settings.value('PromptName')

        # prompt
        input_layout = QHBoxLayout()
        note_field_label = QLabel("Prompt:")
        input_layout.addWidget(note_field_label)
        self.prompt_box = QComboBox(self)
        self.prompt_box.addItems(self.prompt_dict.keys())
        if prompt_name:
            self.prompt_box.setCurrentText(prompt_name)
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

        # Configure Prompt 
        self.prompt_config_button = QPushButton("Configure Prompt and Placeholder")
        self.prompt_config_button.clicked.connect(self.config_prompt)
        layout.addWidget(self.prompt_config_button)

        # Label
        instruction_label = QLabel("Configuration only applies this time.\nPlease configure in the configuration page for future usage.")
        layout.addWidget(instruction_label)

        # Run button
        self.run_button = QPushButton("Run")
        # one connect in controller.py
        self.run_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(self.run_button, 0, Qt.AlignmentFlag.AlignCenter)  # align button to the center

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(cancel_button, 0, Qt.AlignmentFlag.AlignCenter)  # align button to the center

    def prompt_changed(self, index):
        self.curr_prompt_name = self.prompt_box.itemText(index)

    def config_prompt(self):
        prompt_config_dialog = PromptConfigDialog(prompt_name=None, prompt_config_data=self.prompt_dict[self.curr_prompt_name], in_run_dialog=True)
        prompt_config_dialog.exec()
        if prompt_config_dialog.is_changed:
            self.prompt_dict[self.curr_prompt_name] = prompt_config_dialog.prompt_config_data

    def closeEvent(self, event):
        # Save the current size of the dialog when it's closed
        self.settings.setValue('PromptName', self.curr_prompt_name)
        super().closeEvent(event)
