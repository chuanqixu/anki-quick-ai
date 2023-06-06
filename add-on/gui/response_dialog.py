import os, shutil

from PyQt6.QtCore import Qt, QSettings, QDir, QFileInfo
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QTextEdit, QFileDialog
from PyQt6.QtGui import QTextCursor



class ResponseDialog(QDialog):
    def __init__(self, initial_text, ai_thread, parent=None):
        super().__init__(parent)
        self.ai_thread = ai_thread

        self.settings = QSettings('Anki', 'Anki Quick AI')

        self.text_edit = QTextEdit(self)
        self.text_edit.setHtml(initial_text)
        self.text_edit.setReadOnly(True)

        self.curr_cursor = self.text_edit.textCursor()
        self.curr_cursor.movePosition(QTextCursor.End)

        self.save_text_button = QPushButton("Save Text", self)
        self.save_text_button.setFixedSize(120, 35)
        self.save_text_button.clicked.connect(self.save_text)

        self.regen_button = QPushButton("Run Again", self)
        self.regen_button.setFixedSize(120, 35)
        self.regen_button.setStyleSheet('QPushButton {background-color: #DC143C;}')
        # connect in controller.py

        self.save_audio_button = QPushButton("Save Audio", self)
        self.save_audio_button.setFixedSize(120, 35)
        self.save_audio_button.clicked.connect(self.save_audio)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_text_button)
        button_layout.addWidget(self.regen_button)
        button_layout.addWidget(self.save_audio_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_layout)

        # Restore the previous size of the dialog
        size = self.settings.value('DialogSize')
        if size:
            self.resize(size)
        else:
            self.resize(800, 600)  # Set default size
        
        # Restore the previous font size of the text edit
        font = self.text_edit.font()
        saved_font_size = self.settings.value('FontSize')
        if saved_font_size:
            font.setPointSize(int(saved_font_size))
        self.text_edit.setFont(font)

        self.setWindowModality(Qt.NonModal)

        # Connect signal
        ai_thread.start_one_iter.connect(self.append_html)
        ai_thread.new_text_ready.connect(self.append_text)
    
    def append_text(self, new_text):
        self.curr_cursor.insertText(new_text)
        self.curr_cursor.movePosition(QTextCursor.End)
    
    def append_html(self, prompt):
        self.curr_cursor.insertHtml(prompt)
        self.curr_cursor.movePosition(QTextCursor.End)

    def closeEvent(self, event):
        # Save the current size of the dialog when it's closed
        self.settings.setValue('DialogSize', self.size())

        # Save the current font size of the text edit
        current_font_size = self.text_edit.font().pointSize()
        self.settings.setValue('FontSize', current_font_size)

        # close thread
        if hasattr(self.ai_thread, "sound_play_thread"):
            pass

        # remove sound directory
        try:
            if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")):
                shutil.rmtree(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"))
        finally:
            super().closeEvent(event)

    def save_text(self):
        # Retrieve the last used path for text, or use home directory if none is stored
        last_path = self.settings.value('LastTextPath', QDir.homePath())
        last_file = self.settings.value('LastTextFile', 'anki_quick_ai_text.txt')

        # Use QFileDialog to get the save location
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Text", os.path.join(last_path, last_file), "Text Files (*.txt)")

        # If the user didn't cancel the dialog
        if file_path:
            # Extract the directory and file name from the chosen file name
            dest_dir, dest_file = os.path.split(file_path)

            # Save the path for future use
            self.settings.setValue('LastTextPath', QFileInfo(file_path).path())
            self.settings.setValue('LastTextFile', dest_file)

            with open(file_path, 'w') as file:
                file.write(self.text_edit.toPlainText())

    def save_audio(self):
        # Retrieve the last used path for audio, or use home directory if none is stored
        last_path = self.settings.value('LastAudioPath', QDir.homePath())
        last_dir = self.settings.value('LastAudioDir', 'anki_quick_ai_audio')

        # Use QFileDialog to get the save location
        file_dir_path, file_dir_name = QFileDialog.getSaveFileName(self, "Save Audio Files", os.path.join(last_path, last_dir))

        if file_dir_path:
            # Extract the directory and directory name from the chosen file name
            dir_path, dir_name = os.path.split(file_dir_path)

            # Save the directory and directory name for future use
            self.settings.setValue('LastAudioPath', dir_path)
            self.settings.setValue('LastAudioDir', dir_name)

            # Create the directory if it doesn't exist
            os.makedirs(file_dir_path, exist_ok=True)

            # Here, copy your audio directory to the selected path
            src_audio_dir = os.path.join(os.path.dirname(__file__), "output")
            for filename in os.listdir(src_audio_dir):
                if filename.endswith(".mp3"):
                    shutil.copy(os.path.join(src_audio_dir, filename), os.path.join(file_dir_path, filename))
