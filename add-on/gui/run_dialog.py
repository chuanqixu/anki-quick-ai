from aqt import mw

from aqt.browser import Browser
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDialog, QComboBox

from .prompt_window import PromptConfigDialog, TableDialog, PlaceholderTableDialog, conf
from ..utils import find_placeholder
from .prompt_window import PromptConfigDialog


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

        # Configure Prompt 
        self.prompt_config_button = QPushButton("Configure Prompt and Placeholder")
        self.prompt_config_button.clicked.connect(self.config_prompt)
        layout.addWidget(self.prompt_config_button)

        # Run button
        self.run_button = QPushButton("Run")
        # one connect in controller.py
        self.run_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(self.run_button, 0, Qt.AlignCenter)  # align button to the center

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(cancel_button, 0, Qt.AlignCenter)  # align button to the center

    def prompt_changed(self, index):
        self.curr_prompt_name = self.prompt_box.itemData(index)

    def config_prompt(self):
        prompt_config_dialog = PromptConfigDialog(prompt_name=None, prompt_config_data=self.prompt_dict[self.curr_prompt_name], in_run_dialog=True)
        prompt_config_dialog.exec_()
        if prompt_config_dialog.is_changed:
            self.prompt_dict[self.curr_prompt_name] = prompt_config_dialog.prompt_config_data



class PromptConfigDialogInRun(QDialog):
    def __init__(self, prompt_config_data=None):
        super().__init__()
        self.prompt_config_data = prompt_config_data
        self.is_changed = False

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Prompt
        prompt_list = self.prompt_config_data["prompt"] if self.prompt_config_data else None
        self.prompt_table_dialog = TableDialog("Prompt:", prompt_list, button=True)
        self.prompt_table_dialog.changed.connect(self.update_placeholder)
        self.prompt_table_dialog.changed.connect(self.update_language)
        layout.addWidget(self.prompt_table_dialog)
        label = QLabel("Keyword placeholder:\n#field_value#: values in cards.\n#response#: previous response from OpenAI.\n#language#: language specified below.")
        layout.addWidget(label)

        # Placeholder
        placeholder_dict = self.prompt_config_data["placeholder"] if self.prompt_config_data else None
        self.placeholder_table_dialog = PlaceholderTableDialog(placeholder_dict)
        layout.addWidget(self.placeholder_table_dialog)
        label = QLabel("Placeholder should be used in prompts inside ##.\nEx., #p# is replaced with placeholder named \"p\".")
        layout.addWidget(label)

        # Language list
        language_list = self.prompt_config_data["language"] if self.prompt_config_data else None
        self.language_table_dialog = TableDialog("Language:", language_list, button=False)
        layout.addWidget(self.language_table_dialog)
        label = QLabel("Language can be used in prompts as placeholder with #language#.\nThis will be used as the language for sound generation for prompts.\nThe order is corresponding to prompts' order.")
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        # save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_prompt)
        save_button.setFixedSize(100, 40)  # set the size of the button
        button_layout.addWidget(save_button, 0, Qt.AlignCenter)  # align button to the center

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setFixedSize(100, 40)  # set the size of the button
        button_layout.addWidget(cancel_button, 0, Qt.AlignCenter)  # align button to the center

        layout.addLayout(button_layout)

    def save_prompt(self):
        if not self.prompt_config_data:
            self.prompt_config_data = {}
        self.prompt_config_data["prompt"] = self.prompt_table_dialog.data
        self.prompt_config_data["placeholder"] = self.placeholder_table_dialog.placeholder_dict
        self.prompt_config_data["language"] = self.language_table_dialog.data
        self.is_changed = True
        self.close()

    def update_placeholder(self):
        updated_placeholder_dict = {}
        for i, prompt in enumerate(self.prompt_table_dialog.data):
            placeholder_list = find_placeholder(prompt)
            if placeholder_list:
                i = str(i + 1)
                updated_placeholder_dict[i] = {}
                for name in placeholder_list:
                    if self.placeholder_table_dialog.placeholder_dict and i in self.placeholder_table_dialog.placeholder_dict:
                        if name in self.placeholder_table_dialog.placeholder_dict[i]:
                            updated_placeholder_dict[i][name] = self.placeholder_table_dialog.placeholder_dict[i][name]
                        else:
                            updated_placeholder_dict[i][name] = ""
                    else:
                        updated_placeholder_dict[i][name] = ""
        self.placeholder_table_dialog.update_item(updated_placeholder_dict)

    def update_language(self):
        if not self.language_table_dialog.data:
            self.language_table_dialog.data = []
        len_diff = len(self.prompt_table_dialog.data) - len(self.language_table_dialog.data)

        if len_diff > 0:
            self.language_table_dialog.update_item(self.language_table_dialog.data + [conf["general"]["default_sound_language"]] * len_diff)
        else:
            self.language_table_dialog.update_item(self.language_table_dialog.data[:len(self.prompt_table_dialog.data)])
