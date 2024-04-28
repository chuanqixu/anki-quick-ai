import os, shutil

from PyQt6.QtCore import Qt, QSettings, QDir, QFileInfo, QUrl, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QTextEdit, QFileDialog, QSlider, QWidget, QSpacerItem, QScrollArea, QSizePolicy
from PyQt6.QtGui import QTextCursor, QFontMetrics
from PyQt6.QtMultimedia import QMediaPlayer, QMediaPlayer, QAudioOutput


class PromptRunnable(QRunnable):
    def __init__(self, func):
        super().__init__()
        self.func = func

    @pyqtSlot()
    def run(self):
        self.func()


class ResponseDialog(QDialog):
    def __init__(self, initial_text, ai_thread, parent=None):
        super().__init__(parent)
        self.ai_thread = ai_thread
        self.response_widget_list = []
        self.settings = QSettings('Anki', 'Anki Quick AI')
        self.saved_font_size = self.settings.value('FontSize')

        self.field_value_widget = ResponseWidget(initial_text, self, self.saved_font_size, False)

        self.response_scroll_widget = QWidget()
        self.response_layout = QVBoxLayout(self.response_scroll_widget)
        self.response_layout.addWidget(self.field_value_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow the widget to resize
        self.scroll_area.setWidget(self.response_scroll_widget)


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

        self.prompt_text_edit = PromptTextEdit("Input new prompt here", self, self.saved_font_size)
        self.prompt_text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.main_layout = QVBoxLayout(self)
        # self.main_layout.addLayout(self.response_layout)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.prompt_text_edit)
        self.main_layout.addLayout(button_layout)

        # Restore the previous size of the dialog
        size = self.settings.value('DialogSize')
        if size:
            self.resize(size)
        else:
            self.resize(800, 600)  # Set default size

        self.setWindowModality(Qt.WindowModality.NonModal)

        # Connect signal
        self.ai_thread.start_one_iter.connect(self.new_response_widget)
        self.ai_thread.new_text_ready.connect(self.append_text)
        self.ai_thread.finished_gen_sound.connect(self.add_audio_player_widget)
        self.prompt_text_edit.new_prompt_signal.connect(self.input_prompt)

        # Audio sliders
        self.audio_player_widget_dict = {}

    def append_text(self, new_text):

        # FIXCOL: Issue found when appending text to the last response widget
        # Due to the parent of the widget being the Anki Card Browser
        # The start_one_iter signal doesn't work as expected
        if not self.response_widget_list:
            self.new_response_widget("Something went wrong when initializing the response widget.")

        self.response_widget_list[-1].append_text(new_text)

    def new_response_widget(self, prompt):
        response_widget = ResponseWidget(prompt, self, self.saved_font_size)
        self.response_widget_list.append(response_widget)

        for i in reversed(range(self.response_layout.count())):
            item = self.response_layout.itemAt(i)
            if isinstance(item, QSpacerItem):
                self.response_layout.removeItem(item)
                break

        self.response_layout.addWidget(response_widget)
        self.response_layout.addStretch()

    def input_prompt(self, prompt):
        runnable = PromptRunnable(lambda: self.ai_thread.response(prompt))
        QThreadPool.globalInstance().start(runnable)

    def closeEvent(self, event):
        # Save the current size of the dialog when it's closed
        self.settings.setValue('DialogSize', self.size())

        # Save the current font size of the text edit
        font_size_to_save = self.field_value_widget.text_edit.font().pointSize()
        for reponse_widget in self.response_widget_list:
            font_size = reponse_widget.text_edit.font().pointSize()
            if font_size > font_size_to_save:
                font_size_to_save = font_size
        self.settings.setValue('FontSize', font_size_to_save)

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

            text = self.field_value_widget.text_edit.toPlainText()
            text += "\n"
            for response_widget in self.response_widget_list:
                text += f"\n{response_widget.text_edit.toPlainText()}\n"
            with open(file_path, 'w') as file:
                file.write(text)

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
        if not self.response_widget_list:
            self.new_response_widget("Something went wrong when initializing the response widget.")


        audio_player_widget = AudioPlayerWidget(filename)
        i = int(filename.split("_")[-1].split(".")[0])
        self.response_widget_list[i].add_audio_player_widget(audio_player_widget)
        self.audio_player_widget_dict[i] = audio_player_widget
        if self.ai_thread.play_sound and i == 0:
            self.audio_player_widget_dict[i].media_player.mediaStatusChanged.connect(lambda status: self.auto_play_audio(status, i + 1))
            self.audio_player_widget_dict[i].play_audio()

    def auto_play_audio(self, status, i):
        # TODO: automatically play when finishing generating
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.audio_player_widget_dict[i - 1].media_player.mediaStatusChanged.disconnect()
            if i not in self.audio_player_widget_dict:
                return
            if i + 1 < len(self.ai_thread.prompt_list):
                self.audio_player_widget_dict[i].media_player.mediaStatusChanged.connect(lambda status: self.auto_play_audio(status, i + 1))
            self.audio_player_widget_dict[i].play_audio()



class ResponseWidget(QWidget):
    def __init__(self, prompt=None, parent=None, font_size=None, add_spacer=True):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self.adjust_height)
        self.text_edit.setHtml(prompt)
        self.text_edit.setReadOnly(True)

        if font_size:
            font = self.text_edit.font()
            font.setPointSize(int(font_size))
            self.text_edit.setFont(font)
        self.fm = QFontMetrics(self.font())
        self.text_edit.setMinimumHeight(self.fm.lineSpacing() * 6)

        self.main_layout.addWidget(self.text_edit)
        self.curr_cursor = self.text_edit.textCursor()
        self.curr_cursor.movePosition(QTextCursor.MoveOperation.End)

        if add_spacer:
            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.main_layout.addItem(spacer)

    def append_text(self, new_text, is_html=False):
        if is_html:
            self.curr_cursor.insertHtml(new_text)
        else:
            self.curr_cursor.insertText(new_text)

        self.curr_cursor.movePosition(QTextCursor.MoveOperation.End)

    def adjust_height(self):
        doc_height = self.text_edit.document().size().height()
        if self.text_edit.height() != doc_height:
            self.text_edit.setMinimumHeight(doc_height + 10)

    def add_audio_player_widget(self, audio_player_widget):
        self.main_layout.removeItem(self.main_layout.itemAt(self.main_layout.count() - 1))
        self.main_layout.addWidget(audio_player_widget)



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



class PromptTextEdit(QTextEdit):
    new_prompt_signal = pyqtSignal(str)

    def __init__(self, instruction_text="", parent=None, font_size=None):
        super().__init__(parent)
        self.font_size = font_size
        if font_size:
            font = self.font()
            font.setPointSize(int(font_size))
            self.setFont(font)
        self.fm = QFontMetrics(self.font())

        self.instruction_text = instruction_text
        self.has_instruction = True
        self.setText(instruction_text)
        self.document().contentsChanged.connect(self.clear_instruction)

        self.setFixedHeight(self.fm.lineSpacing() + 10)

        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.textChanged.connect(self.adjust_height)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not (event.modifiers() & Qt.Key.ShiftModifier):
                event.accept()
                self.new_prompt_signal.emit(self.toPlainText())
                self.clear()
                self.setFixedHeight(self.fm.lineSpacing() + 10)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def clear_instruction(self):
        if self.has_instruction:
            self.has_instruction = False
            self.clear()

    def adjust_height(self):
        doc_height = self.document().size().height()
        max_height = self.fm.lineSpacing() * 5
        new_height = min(max_height, doc_height)
        if self.height() != new_height:
            self.setFixedHeight(new_height)
