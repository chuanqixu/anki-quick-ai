import copy
from aqt import mw

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QMessageBox, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QWidget, QComboBox, QScrollArea, QCheckBox

from .common_gui import NameTableWidget, ConfigDialog, TableWidget
from ..utils import find_placeholder
from ..ankiaddonconfig import ConfigManager
from ..anki import get_note_type_names_fields_dict

conf = ConfigManager()

class PromptNameTableWidget(NameTableWidget):
    def __init__(self, config_manager):
        super().__init__("prompt", config_manager, PromptConfigDialog)

class PromptConfigDialog(ConfigDialog):
    def init_gui_not_in_run(self):
        # Prompt
        input_layout = QHBoxLayout()
        label = QLabel("<b>Prompt Name:</b>")
        label.setToolTip("Name for this configuration.")
        input_layout.addWidget(label)
        self.item_name = QLineEdit(self.item_name)
        input_layout.addWidget(self.item_name)
        self.main_layout.addLayout(input_layout)
        self.main_layout.addSpacing(10)

        # Browse query
        input_layout = QHBoxLayout()
        label = QLabel("<b>Default Browse Query:</b>")
        label.setToolTip("Default query used in every run. This can be quickly changed in the run dialog.")
        input_layout.addWidget(label)
        query = self.config_data["default_query"] if self.config_data else None
        self.input_field_browse_query = QLineEdit(query)
        input_layout.addWidget(self.input_field_browse_query)
        self.main_layout.addLayout(input_layout)

        label = QLabel('See more details on how to specify query: <a href="https://docs.ankiweb.net/searching.html">Official Doc</a>')
        label.setOpenExternalLinks(True)
        self.main_layout.addWidget(label)
        self.main_layout.addSpacing(10)

    def init_gui(self):
        # Note field
        note_field_dict = self.config_data["note_field"] if self.config_data else None
        self.note_field_table_widget = NoteFieldTableWidget(note_field_dict)
        self.main_layout.addWidget(self.note_field_table_widget)
        label = QLabel("\"Other Note Type\" is for all unspecified note types.")
        self.main_layout.addWidget(label)
        self.main_layout.addSpacing(10)

        agentic_behavior = bool(self.config_data["agentic_behavior"]) if self.config_data and self.config_data.get("agentic_behavior") else False
        self.agentic_behavior = QCheckBox("Per note agentic behavior")
        self.agentic_behavior.setChecked(agentic_behavior)
        self.main_layout.addWidget(self.agentic_behavior)
        self.main_layout.addSpacing(10)

        # System Prompt
        input_layout = QVBoxLayout()
        label = QLabel("<b>System Prompt:</b>")
        label.setToolTip("System prompts are special messages used to steer the behavior of ChatGPT. It is like one general guidance for the AI.")
        input_layout.addWidget(label)
        system_prompt_text_edit = self.config_data["system_prompt"] if self.config_data else None
        self.system_prompt_text_edit = QTextEdit(system_prompt_text_edit)
        input_layout.addWidget(self.system_prompt_text_edit)
        self.main_layout.addLayout(input_layout)
        self.main_layout.addSpacing(10)

        # Prompt
        prompt_list = self.config_data["prompt"] if self.config_data else None
        self.prompt_table_widget = TableWidget("Prompt:", prompt_list, button=True, create_dialog=PromptInputDialog, editable=False)
        self.prompt_table_widget.table.itemDoubleClicked.connect(self.double_click_item)
        self.prompt_table_widget.changed.connect(self.update_placeholder)
        self.prompt_table_widget.changed.connect(self.update_language)
        self.main_layout.addWidget(self.prompt_table_widget)
        # label = QLabel("""
        # Placeholder should be used in prompts inside ##.
        # Ex., #p# is replaced with values specified in placeholder below.

        # Keyword placeholder:
        # #field_value#: values in cards.
        # #response#: previous response from OpenAI.
        # #language#: language specified below.
        # """)
        # layout.addWidget(label)
        self.main_layout.addSpacing(10)

        # Placeholder
        placeholder_dict = self.config_data["placeholder"] if self.config_data else None
        self.placeholder_table_widget = PlaceholderTableWidget(placeholder_dict)
        self.main_layout.addWidget(self.placeholder_table_widget)
        self.main_layout.addSpacing(10)

        # Language list
        language_list = self.config_data["language"] if self.config_data else None
        self.language_table_widget = TableWidget("Language:", language_list, button=False, tooltip="Language will be used for edge-tts sound generation. Language can also be used in prompts as placeholder with #language#.")
        self.main_layout.addWidget(self.language_table_widget)
        self.main_layout.addSpacing(10)

        self.scroll_area.setWidget(self.content_widget)

    def save_not_in_run(self):
        self.config_data["default_query"] = self.input_field_browse_query.text()

    def save(self):
        self.config_data["note_field"] = self.note_field_table_widget.note_field_dict
        self.config_data["system_prompt"] = self.system_prompt_text_edit.toPlainText()
        self.config_data["prompt"] = self.prompt_table_widget.data
        self.config_data["placeholder"] = self.placeholder_table_widget.placeholder_dict
        self.config_data["language"] = self.language_table_widget.data
        self.config_data["agentic_behavior"] = self.agentic_behavior.isChecked()

    def __init__(self, item_name=None, config_data=None, in_run_dialog=False):
        super().__init__("prompt", item_name, config_data, in_run_dialog)

    def update_placeholder(self):
        updated_placeholder_dict = {}
        for i, prompt in enumerate(self.prompt_table_widget.data):
            placeholder_list = find_placeholder(prompt)
            if placeholder_list:
                i = str(i + 1)
                updated_placeholder_dict[i] = {}
                for name in placeholder_list:
                    if self.placeholder_table_widget.placeholder_dict and i in self.placeholder_table_widget.placeholder_dict:
                        if name in self.placeholder_table_widget.placeholder_dict[i]:
                            updated_placeholder_dict[i][name] = self.placeholder_table_widget.placeholder_dict[i][name]
                        else:
                            updated_placeholder_dict[i][name] = ""
                    else:
                        updated_placeholder_dict[i][name] = ""
        self.placeholder_table_widget.update_item(updated_placeholder_dict)

    def update_language(self):
        if not self.language_table_widget.data:
            self.language_table_widget.data = []
        len_diff = len(self.prompt_table_widget.data) - len(self.language_table_widget.data)

        if len_diff > 0:
            self.language_table_widget.update_item(self.language_table_widget.data + [conf["general"]["default_sound_language"]] * len_diff)
        else:
            self.language_table_widget.update_item(self.language_table_widget.data[:len(self.prompt_table_widget.data)])
    
    def double_click_item(self, item):
        dialog = PromptInputDialog(item.text(), self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            item.setText(dialog.get_input_text())


class PromptInputDialog(QDialog):
    def __init__(self, text=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Edit Prompt')

        layout = QVBoxLayout(self)

        self.instructions = QLabel("Keyword placeholder:\n#field_value#: values in cards.\n#response#: previous response from AI.\n#language#: language specified below. \n\nAgentic keyword placeholder: \n#json_fields#: expected result from AI in order to edit card field values \n\nCustom placeholder: sandwich the placeholder with #.\n\nEnter the prompt here.")
        layout.addWidget(self.instructions)

        self.textEdit = QTextEdit(text, self)
        layout.addWidget(self.textEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def get_input_text(self):
        return self.textEdit.toPlainText()



class PlaceholderTableWidget(QWidget):
    def __init__(self, placeholder_dict = None):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self.placeholder_dict = copy.deepcopy(placeholder_dict)

        label = QLabel("<b>Placeholder:</b>")
        self.main_layout.addWidget(label)

        self.table = QTableWidget(0, 3)
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
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item = self.table.item(row, 1)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

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



class NoteFieldTableWidget(QWidget):
    def __init__(self, note_field_dict = None):
        super().__init__()
        self.note_type_names_fields_dict = get_note_type_names_fields_dict(mw.col)
        self.note_type_names_fields_dict["Other Note Type"] = []

        self.main_layout = QVBoxLayout(self)

        self.note_field_dict = copy.deepcopy(note_field_dict)

        self.title_layout = QHBoxLayout()
        label = QLabel("<b>Note Field:</b>")
        label.setToolTip("Only text in the specified fields will be selected.")
        self.title_layout.addWidget(label)

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.create_item)
        self.add_button.setFixedSize(90, 30)
        self.title_layout.addWidget(self.add_button)

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_item)
        self.delete_button.setFixedSize(90, 30)
        self.title_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(self.title_layout)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Note Type", "Selected Field"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 150)
        self.load_data()
        self.main_layout.addWidget(self.table)

        self.table.cellChanged.connect(self.table_updated)

    def load_data(self):
        if self.note_field_dict:
            keys = list(self.note_field_dict.keys())
            keys.sort()
            for note_type in keys:
                for field_name in self.note_field_dict[note_type]:
                    self.add_item(note_type, field_name)

    def add_item(self, note_type, field_name):
        row = self.table.rowCount()
        self.table.insertRow(row)

        note_type_combo = QComboBox(self)
        note_type_combo.addItems(self.note_type_names_fields_dict.keys())
        note_type_combo.setCurrentText(note_type)

        self.table.setCellWidget(row, 0, note_type_combo)

        if note_type == "Other Note Type":
            self.table.setItem(row, 1, QTableWidgetItem(field_name))
        else:
            field_name_combo = QComboBox(self)
            field_name_combo.addItems(self.note_type_names_fields_dict[note_type])
            field_name_combo.setCurrentText(field_name)
            field_name_combo.currentTextChanged.connect(self.table_updated)
            self.table.setCellWidget(row, 1, field_name_combo)

        def update_note_field(note_type):
            if note_type == "Other Note Type":
                field_name = "Front"
                if note_type in self.note_field_dict and len(self.note_field_dict[note_type]) > 0:
                    field_name = self.note_field_dict[note_type][0]
                self.table.setCellWidget(row, 1, None)
                self.table.setItem(row, 1, QTableWidgetItem(field_name))
            else:
                field_name_combo = QComboBox(self)
                field_name_combo.addItems(self.note_type_names_fields_dict[note_type])
                self.table.setCellWidget(row, 1, field_name_combo)
                field_name_combo.currentTextChanged.connect(self.table_updated)
            self.table_updated()

        note_type_combo.currentTextChanged.connect(update_note_field)

    def create_item(self):
        dialog = NoteFieldDialog(self.note_type_names_fields_dict)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            note_type, field_value = dialog.get_input_text()
            self.add_item(note_type, field_value)
            self.save_data()

    def delete_item(self):
        row = self.table.currentRow()

        if row > -1:
            box = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this item?')

            if box == QMessageBox.StandardButton.Yes:
                self.table.removeRow(row)
                self.save_data()

    def update_item(self, note_field_dict):
        self.note_field_dict = note_field_dict
        self.table.setRowCount(0)
        self.load_data()

    def table_updated(self):
        self.save_data()

    def save_data(self):
        note_field_dict = {}
        for row in range(self.table.rowCount()):
            note_type = self.table.cellWidget(row, 0).currentText()

            widget = self.table.cellWidget(row, 1)
            if isinstance(widget, QComboBox):
                field_name = widget.currentText()
            else:
                item = self.table.item(row, 1)
                field_name = item.text() if item else ""
            if note_type not in note_field_dict:
                note_field_dict[note_type] = [field_name]
            else:
                if field_name not in note_type:
                    note_field_dict[note_type].append(field_name)
        self.note_field_dict = note_field_dict



class NoteFieldDialog(QDialog):
    def __init__(self, note_type_names_fields_dict, parent = None):
        super().__init__(parent=parent)
        self.note_type_names_fields_dict = note_type_names_fields_dict

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        label = QLabel("<b>Note Type:</b>")
        self.main_layout.addWidget(label)

        self.note_type_combo = QComboBox(self)
        self.main_layout.addWidget(self.note_type_combo)
        self.note_type_combo.addItems(self.note_type_names_fields_dict.keys())

        self.main_layout.addSpacing(10)


        label = QLabel("<b>Field Name:</b>")
        self.main_layout.addWidget(label)

        if self.note_type_combo.currentText() == "Other Note Type":
            self.field_name_widget = QLineEdit("Front")
        else:
            self.field_name_widget = QComboBox(self)
            self.field_name_widget.addItems(self.note_type_names_fields_dict[self.note_type_combo.currentText()])
        self.main_layout.addWidget(self.field_name_widget)

        def update_note_field(note_type):
            if note_type == "Other Note Type":
                field_name_widget = QLineEdit("Front")
            else:
                field_name_widget = QComboBox(self)
                field_name_widget.addItems(self.note_type_names_fields_dict[note_type])

            index = self.main_layout.indexOf(self.field_name_widget)
            self.main_layout.removeWidget(self.field_name_widget)
            self.field_name_widget.setParent(None)
            self.main_layout.insertWidget(index, field_name_widget)
            self.field_name_widget = field_name_widget

        self.note_type_combo.currentTextChanged.connect(update_note_field)

        self.main_layout.addSpacing(10)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.main_layout.addWidget(buttonBox, alignment=Qt.AlignmentFlag.AlignCenter)

    def get_input_text(self):
        field_name = self.field_name_widget.text() if isinstance(self.field_name_widget, QLineEdit) else self.field_name_widget.currentText()
        return self.note_type_combo.currentText(), field_name
