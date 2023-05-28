from aqt import mw, gui_hooks
from aqt.qt import QAction, qconnect

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import QThread

import openai
import playsound
import os
import asyncio
import queue
import time

from .anki import get_note_field_value_list
from .ai import call_openai, make_edge_tts_mp3
from .gui import RunDialog, ResponseDialog
from .utils import remove_html_tags, format_prompt_list



IS_BROWSE_OPEN = False

AUDIO_FILE_QUEUE = queue.Queue()

class AIThread(QThread):
    def __init__(self, query, note_field, prompt_list, ai_config=None):
        super().__init__()
        self.ai_config = ai_config
        if not ai_config:
            self.ai_config = mw.addonManager.getConfig(__name__)

        self.query = query
        self.note_field = note_field
        self.prompt_list = prompt_list
        self.field_value_list = None
        self.response_list = []
        self.success = False

    def run(self):
        self.success = False

        self.field_value_list = get_note_field_value_list(mw.col, self.query, self.note_field)
        prompt = self.prompt_list[0].replace(f"#response#", str(self.field_value_list))

        # TODO: check api_key and model is given
        self.api_key = self.ai_config.pop("api_key")
        self.model = self.ai_config.pop("model")

        openai.api_key = self.api_key
        response = call_openai(self.model, prompt, **self.ai_config)
        self.response_list.append(response)

        for i in range(1, len(self.prompt_list)):
            prompt = self.prompt_list[i].replace(f"#response#", response)
            response = call_openai(self.model, prompt, **self.ai_config)
            self.response_list.append(response)

        self.success = True


class SoundPlayThread(QThread):
    def __init__(self, audio_file_queue):
        super().__init__()
        self.audio_file_queue = audio_file_queue

    def run(self):
        while True:
            filename = self.audio_file_queue.get()
            while not filename:
                filename = self.audio_file_queue.get()
                time.sleep(0.1)
            if filename == "#end":
                break
            else:
                playsound.playsound(filename)


class SoundGenThread(QThread):
    def __init__(self, response_list, language_list, loop, audio_file_queue):
        super().__init__()
        self.response_list = response_list
        self.language_list = language_list
        self.loop = loop
        self.audio_file_queue = audio_file_queue

    def run(self):
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "output")):
            os.makedirs(os.path.join(os.path.dirname(__file__), "output"))

        for i, response in enumerate(self.response_list):
            response = remove_html_tags(response)
            make_edge_tts_mp3(response, self.language_list[i], os.path.join(os.path.dirname(__file__), "output", f"response_{i}.mp3"), self.loop)
            filename = os.path.join(os.path.dirname(__file__), "output", f"response_{i}.mp3")
            self.audio_file_queue.put(filename)
        self.audio_file_queue.put("#end")


def show_response(field_value_list, prompt_list, response_list, parent=None):
    if len(prompt_list) != len(response_list):
        raise ValueError(f"Prompt length {len(prompt_list)} is not equal to response length {len(response_list)}")

    color = 'green'
    field_value_str = '<br>'.join(field_value_list)

    text = f"<font color='{color}'>Choosen values:</font><br>{field_value_str}<br><br>"
    for i, response in enumerate(response_list):
        text += f"<font color='{color}'>Prompt:<br>{prompt_list[i]}:</font><br>Response:<br>{response}<br><br>"

    if not IS_BROWSE_OPEN:
        parent = mw
    dialog = ResponseDialog(text, parent)
    dialog.setModal(False)
    dialog.show()


def show_response_and_play_sound(ai_success, field_value_list, prompt_list, response_list, language_list, parent=None):
    if not ai_success:
        return
    # play sound
    if mw.addonManager.getConfig(__name__)["play_sound"]:
        loop = asyncio.get_event_loop()
        sound_gen_thread = SoundGenThread(response_list, language_list, loop, AUDIO_FILE_QUEUE)
        sound_gen_thread.start()

        sound_play_thread = SoundPlayThread(AUDIO_FILE_QUEUE)
        sound_play_thread.start()

    # show response
    if not parent:
        parent = mw
    show_response(field_value_list, prompt_list, response_list, parent)


def gen_response(query, note_field, prompt_list, placeholder, language_list, parent=None) -> None:
    prompt_list = format_prompt_list(prompt_list, placeholder, language_list)
    ai_thread = AIThread(query, note_field, prompt_list, mw.addonManager.getConfig(__name__)["ai_config"])

    ai_thread.finished.connect(lambda: show_response_and_play_sound(ai_thread.success, ai_thread.field_value_list, prompt_list, ai_thread.response_list, mw.addonManager.getConfig(__name__)["language_list"], parent=parent))
    ai_thread.start()


def run_add_on(parent=None):
    if not parent:
        parent = mw

    def click_run_add_on(run_widget):
        config = mw.addonManager.getConfig(__name__)
        language_list = None
        if "language_list" in config:
            language_list = config["language_list"]
        run_widget.close()
        gen_response(
            run_widget.input_field_browse_query.text(), 
            run_widget.input_field_note_field.text(), 
            config["prompt_list"],
            config["placeholder"],
            language_list,
            # TODO: add quick editing in RunDialog
            parent=parent
        )

    run_dialog = RunDialog(parent)
    run_dialog.setModal(False)
    run_dialog.run_button.clicked.connect(lambda: click_run_add_on(run_dialog))
    run_dialog.show()


def run_add_on_browse(browser):
    global IS_BROWSE_OPEN 
    IS_BROWSE_OPEN = True
    def check_browse_close():
        global IS_BROWSE_OPEN
        IS_BROWSE_OPEN = False
    browser.destroyed.connect(check_browse_close)

    # add in the menu bar
    action_browse = QAction("Anki Quick AI", browser)
    browser.form.menubar.addAction(action_browse)
    qconnect(action_browse.triggered, lambda: run_add_on(browser))

    # Add a shortcut
    shortcut = mw.addonManager.getConfig(__name__)["shortcut"]
    shortcut = QShortcut(QKeySequence(shortcut), browser)
    shortcut.activated.connect(lambda: run_add_on(browser))





#  initiate connect and hooks

def init_control():
    # Add it to the tools menu
    action_mw = QAction("Anki Quick AI", mw)
    qconnect(action_mw.triggered, run_add_on)
    mw.form.menuTools.addAction(action_mw)

    # Add it to the browse window
    gui_hooks.browser_will_show.append(run_add_on_browse)

    # Hook for end of the deck
    if mw.addonManager.getConfig(__name__)["automatic_display"]:
        gui_hooks.reviewer_will_end.append(run_add_on)

    # Add a hotkey
    shortcut = mw.addonManager.getConfig(__name__)["shortcut"]
    shortcut = QShortcut(QKeySequence(shortcut), mw)
    shortcut.activated.connect(run_add_on)
