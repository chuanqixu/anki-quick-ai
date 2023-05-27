from aqt import mw
from aqt.utils import showInfo
from aqt.operations import QueryOp

import openai
import playsound
import os
import threading
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox

from .anki import get_note_field_value_list
from .gpt import call_openai, make_edge_tts_mp3



config = mw.addonManager.getConfig(__name__)

class AIThread(threading.Thread):
    def __init__(self, api_key, model, browse_cmd, note_field, prompt_list):
        super().__init__()
        openai.api_key = api_key
        self.model = model
        self.browse_cmd = browse_cmd
        self.note_field = note_field
        self.prompt_list = prompt_list
        self.field_value_list = None
        self.response_list = []
        self.daemon = True  # Set the thread as daemon
        self.success = False

    def run(self):
        self.success = False
        
        self.field_value_list = get_note_field_value_list(mw.col, self.browse_cmd, self.note_field)

        prompt = self.prompt_list[0].replace(f"#response#", str(self.field_value_list))
        response = call_openai(prompt, self.model)
        self.response_list.append(response)

        for i in range(1, len(self.prompt_list)):
            prompt = self.prompt_list[i].replace(f"#response#", response)
            response = call_openai(prompt, self.model)
            self.response_list.append(response)
        
        self.success = True


class SoundThread(threading.Thread):
    def __init__(self, response_list, sound_language_list):
        super().__init__()
        self.response_list = response_list
        self.sound_language_list = sound_language_list
        self.daemon = True  # Set the thread as daemon

    def run(self):
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "output")):
            os.makedirs(os.path.join(os.path.dirname(__file__), "output"))
        for i in range(len(self.response_list)):
            make_edge_tts_mp3(self.response_list[i], self.sound_language_list[i], os.path.join(os.path.dirname(__file__), "output", f"response_{i}.mp3"))
            playsound.playsound(os.path.join(os.path.dirname(__file__), "output", f"response_{i}.mp3"))


class ChooseWidget(QWidget):
    def __init__(self, query, call_widget=mw):
        super().__init__()
        self.call_widget = call_widget
        self.initUI(query)

    def initUI(self, query):
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Browse query
        input_layout = QHBoxLayout()
        explanation_label = QLabel("Browse Query:")
        input_layout.addWidget(explanation_label)
        input_field_browse_query = QLineEdit(query)
        input_layout.addWidget(input_field_browse_query)
        layout.addLayout(input_layout)

        # note field
        input_layout = QHBoxLayout()
        explanation_label = QLabel("Note Field:")
        input_layout.addWidget(explanation_label)
        input_field_note_field = QLineEdit(config["note_field"])
        input_layout.addWidget(input_field_note_field)
        layout.addLayout(input_layout)

        # Instruction
        label = QLabel("Whether to run the add-on \"Anki Quick AI\"?\nIt may take seconds for AI to generate contents, and another seconds for sound generation,\ndepending on the length of the prompts.")
        layout.addWidget(label)

        # Run button
        run_button = QPushButton("Run")
        run_button.clicked.connect(lambda : self.runAddon(input_field_browse_query.text(), input_field_note_field.text()))
        run_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(run_button, 0, Qt.AlignCenter)  # align button to the center

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        cancel_button.setFixedSize(100, 40)  # set the size of the button
        layout.addWidget(cancel_button, 0, Qt.AlignCenter)  # align button to the center

    def runAddon(self, query, note_field):
        # Logic to run your add-on goes here
        # print("Running Add-on")
        self.close()
        gen_response(query, note_field, call_widget=self.call_widget)


def show_response(field_value_list, prompt_list, response_list, parent):
    if len(prompt_list) != len(response_list):
        raise ValueError(f"Prompt length {len(prompt_list)} is not equal to response length {len(response_list)}")
    
    color = 'green'
    field_value_str = '<br>'.join(field_value_list)

    text = f"<font color='{color}'>Choosen values:</font><br>{field_value_str}<br><br>"
    for i in range(len(response_list)):
        text += f"<font color='{color}'>Prompt: {prompt_list[i]}:</font><br>Response: {response_list[i]}<br><br>"
    
    showInfo(text, parent)


def show_response_and_play_sound(ai_success, field_value_list, prompt_list, response_list, sound_language_list, parent=mw):
    if not ai_success:
        return
    # play sound
    if config["play_sound"]:
        music_thread = SoundThread(response_list, sound_language_list)
        music_thread.start()

    # show story
    show_response(field_value_list, prompt_list, response_list, parent)


def run_add_on(query, call_widget=mw):
    chooseWidget = ChooseWidget(query, call_widget)
    chooseWidget.show()


def format_prompt_list(prompt_list, placeholder_dict):
    promp_index_placeholder_value_dict = {}
    for placeholder, promp_index_value_dict in placeholder_dict.items():
        for index, value in promp_index_value_dict.items():
            index = int(index)
            if index in promp_index_placeholder_value_dict:
                promp_index_placeholder_value_dict[index][placeholder] = value
            else:
                promp_index_placeholder_value_dict[index] = {placeholder: value}
    
    formatted_prompt_list = []
    for index, prompt in enumerate(prompt_list):
        if index in promp_index_placeholder_value_dict:
            for key, value in promp_index_placeholder_value_dict[index].items():
                prompt = prompt.replace(f"#{key}#", value)
            formatted_prompt_list.append(prompt)
            # formatted_prompt_list.append(prompt.format(**(promp_index_placeholder_value_dict[index])))
        else:
            formatted_prompt_list.append(prompt)
    return formatted_prompt_list


def gen_response(query, note_field, call_widget=mw) -> None:
    config = mw.addonManager.getConfig(__name__)
    prompt_list = format_prompt_list(config["prompt_list"], config["placeholder"])
    ai_thread = AIThread(config["api_key"], config["model"], query, note_field, prompt_list)

    def run_ai_thread(ai_thread):
        ai_thread.start()
        ai_thread.join()

    op_story = QueryOp(
        # the active window (main window in this case)
        parent=call_widget,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: run_ai_thread(ai_thread),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda x: show_response_and_play_sound(ai_thread.success, ai_thread.field_value_list, config["prompt_list"], ai_thread.response_list, config["sound_language_list"], parent=call_widget)
    )

    op_story.with_progress(label="It may take seconds for AI to generate contents").run_in_background()
