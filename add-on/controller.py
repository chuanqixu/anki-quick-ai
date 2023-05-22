from aqt import mw
from aqt.utils import showInfo
from aqt.operations import QueryOp

import openai
import playsound
import os
import threading
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from .anki import get_note_field_value_list
from .gpt import call_openai, make_edge_tts_mp3



class AIThread(threading.Thread):
    def __init__(self, api_key, model, browse_cmd, prompt_list, language_list):
        super().__init__()
        openai.api_key = api_key
        self.model = model
        self.browse_cmd = browse_cmd
        self.prompt_list = prompt_list
        self.language_list = language_list
        self.field_value_list = None
        self.response_list = []
        self.daemon = True  # Set the thread as daemon

    def run(self):
        self.field_value_list = get_note_field_value_list(self.browse_cmd)

        prompt = self.prompt_list[0].format(language=self.language_list[0], value_list=self.field_value_list)
        response = call_openai(prompt, self.model)
        self.response_list.append(response)

        for i in range(1, len(self.prompt_list)):
            prompt = self.prompt_list[i].format(language=self.language_list[i], response=response)
            response = call_openai(prompt, self.model)
            self.response_list.append(response)


class SoundThread(threading.Thread):
    def __init__(self, response_list, language_list):
        super().__init__()
        self.response_list = response_list
        self.language_list = language_list
        self.daemon = True  # Set the thread as daemon

    def run(self):
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "output")):
            os.makedirs(os.path.join(os.path.dirname(__file__), "output"))
        for i in range(len(self.response_list)):
            make_edge_tts_mp3(self.response_list[i], self.language_list[i], os.path.join(os.path.dirname(__file__), "output", f"response_{i}.mp3"))
            playsound.playsound(os.path.join(os.path.dirname(__file__), "output", f"response_{i}.mp3"))


class ChooseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Whether to run the add-on \"Anki AI Conversation\"?\nIt may take seconds for AI to generate contents, and another seconds for sound generation.")
        layout.addWidget(label)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.runAddon)
        layout.addWidget(run_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        layout.addWidget(cancel_button)

    def runAddon(self):
        # Logic to run your add-on goes here
        # print("Running Add-on")
        self.close()
        gen_response()


def show_response(field_value_list, prompt_list, response_list):
    if len(prompt_list) != len(response_list):
        raise ValueError(f"Prompt length {len(prompt_list)} is not equal to response length {len(response_list)}")
    
    color = 'green'
    field_value_str = '<br>'.join(field_value_list)

    text = f"<font color='{color}'>Choosen values:</font><br>{field_value_str}<br><br>"
    for i in range(len(response_list)):
        text += f"<font color='{color}'>Prompt: {prompt_list[i]}:</font><br>Response: {response_list[i]}<br><br>"
    
    showInfo(text)


def show_response_and_play_sound(field_value_list, prompt_list, response_list, language_list):
    # play sound
    if mw.addonManager.getConfig(__name__)["play_sound"]:
        music_thread = SoundThread(response_list, language_list)
        music_thread.start()

    # show story
    show_response(field_value_list, prompt_list, response_list)


def choose_running_add_on():
    mw.chooseWidget = ChooseWidget()
    mw.chooseWidget.show()


def gen_response() -> None:
    config = mw.addonManager.getConfig(__name__)

    ai_thread = AIThread(config["api_key"], config["model"], config["query"], config["prompt_list"], config["language_list"])

    def run_story_thread(story_thread):
        story_thread.start()
        story_thread.join()

    op_story = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: run_story_thread(ai_thread),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda x: show_response_and_play_sound(ai_thread.field_value_list, config["prompt_list"], ai_thread.response_list, config["language_list"])
    )

    op_story.with_progress(label="It may take seconds for AI to generate contents").run_in_background()
