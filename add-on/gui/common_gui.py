from abc import abstractmethod
import copy

from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QMessageBox, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QWidget, QComboBox, QScrollArea, QCheckBox

from ..ankiaddonconfig import ConfigManager

conf = ConfigManager()


class NameTableWidget(QWidget):
    def __init__(self, config_name, config_manager, config_dialog_class):
        super().__init__()
        self.config_name = config_name
        self.config_manager = config_manager
        self.config_dialog_class = config_dialog_class

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
        data = self.config_manager[self.config_name]

        for name in data:
            self.add_item(name)
        
        self.data = data

    def add_item(self, name):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        item = self.table.item(row, 0)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        self.row_text_dict[row] = name

    def create_item(self):
        config_dialog = self.config_dialog_class()
        config_dialog.exec()

        if config_dialog.is_changed:
            name = config_dialog.item_name.text()
            self.add_item(name)
            self.data[name] = config_dialog.config_data

    def update_item(self):
        row = self.table.currentRow()
        item = self.table.item(row, 0)

        if item:
            old_name = item.text()
            config_dialog = self.config_dialog_class(old_name, self.data[old_name])
            config_dialog.exec()

            if config_dialog.is_changed:
                name = config_dialog.item_name.text()
                item.setText(name)
                self.data[name] = config_dialog.config_data
                if old_name != name:
                    self.data.pop(old_name)
                    self.row_text_dict[row] = name

    def copy_item(self):
        item = self.table.currentItem()
        name = item.text()
        self.add_item(f"{name} copy")
        self.data[f"{name} copy"] = self.data[name]

    def delete_item(self):
        row = self.table.currentRow()

        if row > -1:
            box = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this item?')

            if box == QMessageBox.StandardButton.Yes:
                name = self.table.item(row, 0).text()
                self.table.removeRow(row)
                self.data.pop(name)

    def table_updated(self, item):
        # Get the old and new texts of the item
        row = item.row()
        old_text = self.row_text_dict.get(row)
        new_text = item.text()

        if not old_text:
            return

        if not new_text:
            self.row_text_dict.pop(row)
            self.data.pop(old_text)

        if old_text != new_text:
            # Update the stored text of the item
            self.row_text_dict[row] = new_text

            # Remove the old text from the list and add the new text
            self.data[new_text] = self.data.pop(old_text)



class ConfigDialog(QDialog):
    @abstractmethod
    def init_gui_not_in_run(self):
        pass

    @abstractmethod
    def init_gui(self):
        pass

    @abstractmethod
    def save_not_in_run(self):
        pass

    @abstractmethod
    def save(self):
        pass

    def _save(self):
        if not self.config_data:
            self.config_data = {}

        if not self.in_run_dialog:
            self.save_not_in_run()
        self.save()

        self.is_changed = True
        self.save()
        self.close()

    def __init__(self, config_name=None, item_name=None, config_data=None, in_run_dialog=False):
        super().__init__()
        self.config_name = config_name
        self.item_name = item_name
        self.settings = QSettings('Anki', 'Anki Quick AI')
        self.config_data = copy.deepcopy(config_data)
        self.in_run_dialog = in_run_dialog
        self.is_changed = False

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)

        label = QLabel("Hover mouse on text to see more details!")
        self.main_layout.addWidget(label)
        self.main_layout.addSpacing(10)

        if not in_run_dialog:
            self.init_gui_not_in_run()
        self.init_gui()

        button_layout = QHBoxLayout()
        # save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save)
        save_button.setFixedSize(100, 40)  # set the size of the button
        button_layout.addWidget(save_button, 0, Qt.AlignmentFlag.AlignCenter)  # align button to the center

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setFixedSize(100, 40)  # set the size of the button
        button_layout.addWidget(cancel_button, 0, Qt.AlignmentFlag.AlignCenter)  # align button to the center

        self.main_layout.addLayout(button_layout)

        # Restore the previous size of the dialog
        size = self.settings.value(f'{self.config_name}ConfigDialogSize')
        if size:
            self.resize(size)
        else:
            self.resize(800, 600)  # Set default size

    def closeEvent(self, event):
        # Save the current size of the dialog when it's closed
        self.settings.setValue(f'{self.config_name}ConfigDialogSize', self.size())
        super().closeEvent(event)



class TableWidget(QWidget):
    changed = pyqtSignal()
    def __init__(self, name, data = None, button=False, create_dialog=None, editable=True, tooltip=None):
        super().__init__()
        self.create_dialog = create_dialog
        self.editable = editable

        self.main_layout = QVBoxLayout(self)

        self.data = data if data else []

        self.title_layout = QHBoxLayout()

        label = QLabel(f"<b>{name}</b>")
        if tooltip:
            label.setToolTip(tooltip)
        self.title_layout.addWidget(label)

        if button:
            self.add_button = QPushButton('Add')
            self.add_button.clicked.connect(self.create_item)
            self.add_button.setFixedSize(90, 30)
            self.title_layout.addWidget(self.add_button)

            self.delete_button = QPushButton('Delete')
            self.delete_button.clicked.connect(self.delete_item)
            self.delete_button.setFixedSize(90, 30)
            self.title_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(self.title_layout)

        self.table = QTableWidget(0, 1)
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
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    
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
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            name = dialog.get_input_text()
            self.add_item(name)
            self.save_data()

    def delete_item(self):
        row = self.table.currentRow()

        if row > -1:
            box = QMessageBox.question(self, 'Delete', 'Are you sure you want to delete this item?')

            if box == QMessageBox.StandardButton.Yes:
                self.table.removeRow(row)
                self.save_data()

    def save_data(self):
        data = []

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            data.append(item.text())

        self.data = data

        self.changed.emit()
