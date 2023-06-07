import copy

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QInputDialog, QMessageBox, QLabel, QLineEdit, QTextEdit, QDialogButtonBox

from ..utils import find_placeholder
# from .config_window import conf
from ..ankiaddonconfig import ConfigManager
conf = ConfigManager()



class PromptNameTableDialog(QDialog):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager

        self.setWindowTitle('Configuration')

        self.main_layout = QVBoxLayout(self)

        self.button_layout = QHBoxLayout()

        self.create_button = QPushButton('Create')
        self.create_button.clicked.connect(self.create_item)
        self.button_layout.addWidget(self.create_button)

        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_item)
        self.button_layout.addWidget(self.update_button)

        self.copy_button = QPushButton('Copy')
        self.copy_button.clicked.connect(self.copy_item)
        self.button_layout.addWidget(self.copy_button)

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_item)
        self.button_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(self.button_layout)

        self.row_text_dict = {} # keep tracks of names in the table so that users can directly change in the table
        self.table = QTableWidget(0, 1)  # 0 rows, 1 column
        self.table.setColumnWidth(0, 400)
        self.table.itemDoubleClicked.connect(self.update_item)
        self.load_data()
        self.main_layout.addWidget(self.table)

        # self.table.itemChanged.connect(self.table_updated) # conflict with double click

    def load_data(self):
        self.table.setRowCount(0)
        prompt_data = self.config_manager["prompt"]

        for name in prompt_data:
            self.add_item(name)
        
        self.prompt_data = prompt_data

    def add_item(self, name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        item = self.table.item(row, 0)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

        self.row_text_dict[row] = name

    def create_item(self):
        prompt_config_dialog = PromptConfigDialog()
        prompt_config_dialog.exec_()

        if prompt_config_dialog.is_changed:
            prompt_name = prompt_config_dialog.input_field_prompt_name.text()
            self.add_item(prompt_name)
            self.prompt_data[prompt_name] = prompt_config_dialog.prompt_config_data

    def update_item(self):
        row = self.table.currentRow()
        item = self.table.item(row, 0)

        if item:
            old_name = item.text()
            prompt_config_dialog = PromptConfigDialog(old_name, self.prompt_data[old_name])
            prompt_config_dialog.exec_()

            if prompt_config_dialog.is_changed:
                prompt_name = prompt_config_dialog.input_field_prompt_name.text()
                item.setText(prompt_name)
                self.prompt_data[prompt_name] = prompt_config_dialog.prompt_config_data
                if old_name != prompt_name:
                    self.prompt_data.pop(old_name)
                    self.row_text_dict[row] = prompt_name

    def copy_item(self):
        item = self.table.currentItem()
        prompt_name = item.text()
        self.add_item(f"{prompt_name} copy")
        self.prompt_data[f"{prompt_name} copy"] = self.prompt_data[prompt_name]

    def delete_item(self):
        row = self.table.currentRow()

        if row > -1:
            box = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this item?')

            if box == QMessageBox.Yes:
                prompt_name = self.table.item(row, 0).text()
                self.table.removeRow(row)
                self.prompt_data.pop(prompt_name)
    
    def table_updated(self, item):
        # Get the old and new texts of the item
        row = item.row()
        old_text = self.row_text_dict.get(row)
        new_text = item.text()

        if not old_text:
            return

        if not new_text:
            self.row_text_dict.pop(row)
            self.prompt_data.pop(old_text)

        if old_text != new_text:
            # Update the stored text of the item
            self.row_text_dict[row] = new_text

            # Remove the old text from the list and add the new text
            self.prompt_data[new_text] = self.prompt_data.pop(old_text)



class PromptConfigDialog(QDialog):
    def __init__(self, prompt_name=None, prompt_config_data=None, in_run_dialog=False):
        super().__init__()
        self.prompt_config_data = copy.deepcopy(prompt_config_data)
        self.in_run_dialog = in_run_dialog
        self.is_changed = False

        layout = QVBoxLayout()
        self.setLayout(layout)

        if not in_run_dialog:
            # Prompt
            input_layout = QHBoxLayout()
            label = QLabel("Prompt Name:")
            input_layout.addWidget(label)
            self.input_field_prompt_name = QLineEdit(prompt_name)
            input_layout.addWidget(self.input_field_prompt_name)
            layout.addLayout(input_layout)

            # Browse query
            input_layout = QHBoxLayout()
            label = QLabel("Default Browse Query:")
            input_layout.addWidget(label)
            query = self.prompt_config_data["default_query"] if self.prompt_config_data else None
            self.input_field_browse_query = QLineEdit(query)
            input_layout.addWidget(self.input_field_browse_query)
            layout.addLayout(input_layout)

            # Note field
            input_layout = QHBoxLayout()
            label = QLabel("Default Note Field:")
            input_layout.addWidget(label)
            note_field = self.prompt_config_data["default_note_field"] if self.prompt_config_data else None
            self.input_field_note_field = QLineEdit(note_field)
            input_layout.addWidget(self.input_field_note_field)
            layout.addLayout(input_layout)

        # Prompt
        prompt_list = self.prompt_config_data["prompt"] if self.prompt_config_data else None
        self.prompt_table_dialog = TableDialog("Prompt:", prompt_list, button=True, create_dialog=PromptInputDialog, editable=False)
        self.prompt_table_dialog.table.itemDoubleClicked.connect(self.double_click_item)
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
        
        if not self.in_run_dialog:
            self.prompt_config_data["default_query"] = self.input_field_browse_query.text()
            self.prompt_config_data["default_note_field"] = self.input_field_note_field.text()
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
    
    def double_click_item(self, item):
        dialog = PromptInputDialog(item.text(), self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            item.setText(dialog.get_input_text())



class TableDialog(QDialog):
    changed = pyqtSignal()
    def __init__(self, name, data = None, button=False, create_dialog=None, editable=True):
        super().__init__()
        self.create_dialog = create_dialog
        self.editable = editable

        self.main_layout = QVBoxLayout(self)

        self.data = data if data else []

        self.title_layout = QHBoxLayout()

        label = QLabel(f"<b>{name}</b>")
        self.title_layout.addWidget(label)

        if button:
            self.add_button = QPushButton('Add')
            self.add_button.clicked.connect(self.create_item)
            self.add_button.setFixedSize(80, 35)
            self.title_layout.addWidget(self.add_button)

            self.delete_button = QPushButton('Delete')
            self.delete_button.clicked.connect(self.delete_item)
            self.delete_button.setFixedSize(80, 35)
            self.title_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(self.title_layout)

        self.table = QTableWidget(0, 1)  # 0 rows, 1 column
        self.table.setColumnWidth(0, 350)
        self.table.setHorizontalHeaderLabels(["Value"])
        self.load_data()
        self.main_layout.addWidget(self.table)

        self.table.itemChanged.connect(self.table_updated)

    def load_data(self):
        for name in self.data:
            self.add_item(name)

    def add_item(self, name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        item = self.table.item(row, 0)
        if not self.editable:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def update_item(self, data):
        self.data = data
        self.table.setRowCount(0)
        self.load_data()

    def table_updated(self, item):
        row = item.row()
        if row < len(self.data):
            self.data[row] = item.text()
        else:
            self.data.append(item.text())
        self.changed.emit()

    def create_item(self):
        dialog = self.create_dialog(text=None, parent=self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            name = dialog.get_input_text()
            self.add_item(name)
            self.save_data()

    def delete_item(self):
        row = self.table.currentRow()

        if row > -1:
            box = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this item?')

            if box == QMessageBox.Yes:
                self.table.removeRow(row)
                self.save_data()

    def save_data(self):
        data = []

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            data.append(item.text())

        self.data = data

        self.changed.emit()



class PromptInputDialog(QDialog):
    def __init__(self, text=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Edit Prompt')

        layout = QVBoxLayout(self)

        self.instructions = QLabel("Keyword placeholder:\n#field_value#: values in cards.\n#response#: previous response from OpenAI.\n#language#: language specified below.\n\nCustom placeholder: sandwich the placeholder with #.\n\nEnter the prompt here.")
        layout.addWidget(self.instructions)

        self.textEdit = QTextEdit(text, self)
        layout.addWidget(self.textEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def get_input_text(self):
        return self.textEdit.toPlainText()



class PlaceholderTableDialog(QDialog):
    def __init__(self, placeholder_dict = None):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self.placeholder_dict = copy.deepcopy(placeholder_dict)

        label = QLabel("<b>Placeholder:</b>")
        self.main_layout.addWidget(label)

        self.table = QTableWidget(0, 3)  # 0 rows, 1 column
        self.table.setHorizontalHeaderLabels(["Index", "Name", "Value"])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 200)
        self.load_data()
        self.main_layout.addWidget(self.table)

        self.table.itemChanged.connect(self.table_updated)

    def load_data(self):
        if self.placeholder_dict:
            keys = list(self.placeholder_dict.keys())
            keys.sort(key=int)
            for i in keys:
                for name in self.placeholder_dict[i]:
                    self.add_item(i, name, self.placeholder_dict[i][name])

    def add_item(self, i, name, value):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(i))
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(value))

        item = self.table.item(row, 0)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item = self.table.item(row, 1)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def update_item(self, placeholder_dict):
        self.placeholder_dict = placeholder_dict
        self.table.setRowCount(0)
        self.load_data()

    def table_updated(self, item):
        row = item.row()
        if item.column() == 2:
            i = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text()
            value = self.table.item(row, 2).text()
            if i in self.placeholder_dict:
                if name in self.placeholder_dict[i]:
                    self.placeholder_dict[i][name] = value

    def save_data(self):
        placeholder_dict = {}
        for row in range(self.table.rowCount()):
            i = self.table.item(row, 0).text()
            name = self.table.item(row, 1).text()
            value = self.table.item(row, 2).text()
            if i not in placeholder_dict:
                placeholder_dict[i] = {name: value}
            else:
                placeholder_dict[i][name] = value
        self.placeholder_dict = placeholder_dict
