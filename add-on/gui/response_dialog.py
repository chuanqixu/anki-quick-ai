import os, shutil, time

from PyQt6.QtCore import Qt, QSettings, QDir, QFileInfo, QUrl
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QTextEdit, QFileDialog, QSlider, QWidget
from PyQt6.QtGui import QTextCursor
from PyQt6.QtMultimedia import QMediaPlayer, QMediaPlayer, QAudioOutput



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

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.text_edit)
        self.main_layout.addLayout(button_layout)

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
        self.ai_thread.start_one_iter.connect(self.append_html)
        self.ai_thread.new_text_ready.connect(self.append_text)
        self.ai_thread.finished_gen_sound.connect(self.add_audio_player_widget)

        # Audio sliders
        self.audio_player_widget_dict = {}

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

        # close thread and release resources so that they can be deleted
        if hasattr(self.ai_thread, "sound_play_thread"):
            self.ai_thread.sound_play_thread.terminate()
        for audio_player_widget in self.audio_player_widget_dict.values():
            audio_player_widget.media_player.stop()
            audio_player_widget.media_player.setSource(QUrl())
            self.main_layout.removeWidget(audio_player_widget)

        # remove sound directory
        # try:
        #     # pass
        #     if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")):
        #         shutil.rmtree(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"))
        # finally:
        #     super().closeEvent(event)
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

    def add_audio_player_widget(self, filename):
        audio_player_widget = AudioPlayerWidget(filename)
        i = int(filename.split("_")[-1].split(".")[0])
        self.main_layout.addWidget(audio_player_widget)
        self.audio_player_widget_dict[i] = audio_player_widget
        if self.ai_thread.play_sound and i == 0:
            self.audio_player_widget_dict[i].media_player.mediaStatusChanged.connect(lambda status: self.auto_play_audio(status, i + 1))
            self.audio_player_widget_dict[i].play_audio()

    def auto_play_audio(self, status, i):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.audio_player_widget_dict[i - 1].media_player.mediaStatusChanged.disconnect()
            if i + 1 < len(self.ai_thread.prompt_list):
                self.audio_player_widget_dict[i].media_player.mediaStatusChanged.connect(lambda status: self.auto_play_audio(status, i + 1))
            self.audio_player_widget_dict[i].play_audio()



class AudioPlayerWidget(QWidget):
    def __init__(self, filename):
        super().__init__()

        self.is_playing = False

        # Create play and pause buttons
        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.play_audio)

        # Create slider
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.sliderMoved.connect(self.seek_audio)

        # Set layout
        layout = QHBoxLayout()
        layout.addWidget(self.play_button)
        layout.addWidget(self.seek_slider)

        self.setLayout(layout)

        # Load audio file
        self.media_player = QMediaPlayer()
        self.media_player.setSource(QUrl.fromLocalFile(filename))
        self.media_player.positionChanged.connect(self.update_seek_slider)
        self.media_player.durationChanged.connect(self.update_duration)
        self.audio = QAudioOutput()
        self.media_player.setAudioOutput(self.audio)

        self.seek_slider.setMaximum(self.media_player.duration())

    def play_audio(self):
        if self.is_playing:
            self.media_player.pause()
        else:
            self.media_player.play()
        self.is_playing = not self.is_playing

    def seek_audio(self, position):
        self.media_player.setPosition(position)

    def update_seek_slider(self, position):
        self.seek_slider.setValue(position)

    def update_duration(self, duration):
        self.seek_slider.setRange(0, duration)
