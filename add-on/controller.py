from aqt import mw, gui_hooks
from aqt.qt import QAction, qconnect

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import QThread, pyqtSignal

import openai
import playsound
import os
import asyncio
import queue
import time
import threading

from .anki import get_note_field_value_list
from .ai import call_openai, make_edge_tts_mp3
from .gui import RunDialog, ResponseDialog, conf
from .utils import remove_html_tags, format_prompt_list, prompt_html, field_value_html



IS_BROWSE_OPEN = False

AUDIO_FILE_QUEUE = queue.Queue()

class AIThread(QThread):
    field_value_ready = pyqtSignal(list)
    new_text_ready = pyqtSignal(str)
    start_one_iter = pyqtSignal(str)
    finished_one_iter = pyqtSignal(int, str, bool)

    def __init__(self, query, note_field, prompt_list, ai_config=None, play_sound=None, loop=None):
        super().__init__()
        self.ai_config = ai_config
        if not ai_config:
            self.ai_config = mw.addonManager.getConfig(__name__)["ai_config"]

        self.query = query
        self.note_field = note_field
        self.prompt_list = prompt_list
        self.field_value_list = None
        self.response_list = []
        self.play_sound = play_sound
        self.loop = loop

        self.language_list = ["Japanese", "English"]

        self.success = False

        if self.play_sound:
            self.finished_one_iter.connect(self.gen_sound)

    def run(self):
        self.success = False
        delay_time = 0.01

        self.field_value_list = get_note_field_value_list(mw.col, self.query, self.note_field)
        self.field_value_ready.emit(self.field_value_list)

        time.sleep(0.1) # make sure the first prompt will be printed

        # TODO: check api_key and model is given
        self.api_key = self.ai_config.pop("api_key")
        self.model = self.ai_config.pop("model")

        openai.api_key = self.api_key

        if self.play_sound:
            sound_play_thread = SoundPlayThread(AUDIO_FILE_QUEUE)
            sound_play_thread.start()

        response_str = ""
        for i, prompt in enumerate(self.prompt_list):
            prompt_html_str = prompt_html(prompt, "green")
            self.start_one_iter.emit(prompt_html_str)
            prompt = prompt.replace(f"#field_value#", str(self.field_value_list))
            prompt = prompt.replace(f"#response#", response_str)

            response = call_openai(self.model, prompt, **self.ai_config)

            response_str = ""
            for event in response: 
                event_text = event['choices'][0]['delta']
                new_text = event_text.get('content', '')
                self.new_text_ready.emit(new_text)
                response_str += new_text
                time.sleep(delay_time)

            if self.play_sound:
                self.finished_one_iter.emit(i, response_str, i == len(self.prompt_list) - 1)
            self.response_list.append(response_str)

        self.success = True

    def gen_sound(self, i, response_str, is_end):
        sound_gen_thread = SoundGenThread(i, response_str, self.language_list, self.loop, AUDIO_FILE_QUEUE, is_end)
        sound_gen_thread.start()


class SoundGenThread(threading.Thread): # Cannot be QThread, otherwise will cause Anki to crash because of the async loop
    def __init__(self, i, response_str, language_list, loop, queue, is_end):
        super().__init__()
        self.i = i
        self.response_str = response_str
        self.language_list = language_list
        self.loop = loop
        self.queue = queue
        self.is_end = is_end

    def run(self):
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "output")):
            os.makedirs(os.path.join(os.path.dirname(__file__), "output"))

        response_str = remove_html_tags(self.response_str)
        filename = os.path.join(os.path.dirname(__file__), "output", f"response_{self.i}.mp3")
        make_edge_tts_mp3(response_str, self.language_list[self.i], filename, self.loop)

        self.queue.put(filename)
        if self.is_end:
            self.queue.put("#end")


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
                try:
                    playsound.playsound(filename)
                finally:
                    continue


def gen_response(query, note_field, prompt_list, placeholder, language_list, parent=None) -> None:
    config = mw.addonManager.getConfig(__name__)
    prompt_list = format_prompt_list(prompt_list, placeholder, language_list)
    loop = asyncio.get_event_loop()
    ai_thread = AIThread(query, note_field, prompt_list, config["ai_config"], config["general"]["play_sound"], loop)
    ai_thread.start()

    def show_dialog(field_value_list):
        initial_text = field_value_html(field_value_list, "green")
        dialog = ResponseDialog(initial_text, ai_thread, parent)
        dialog.setModal(False)
        dialog.show()
    
    ai_thread.field_value_ready.connect(show_dialog)


def run_add_on(parent=None):
    if not parent:
        parent = mw

    def click_run_add_on(run_dialog):
        prompt_config = run_dialog.prompt_dict[run_dialog.curr_prompt_name]
        if "language_list" in prompt_config:
            language_list = prompt_config["language_list"]
        run_dialog.close()
        gen_response(
            run_dialog.input_field_browse_query.text(),
            run_dialog.input_field_note_field.text(),
            prompt_config["prompt"],
            prompt_config["placeholder"],
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
    shortcut = mw.addonManager.getConfig(__name__)["general"]["shortcut"]
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
    if mw.addonManager.getConfig(__name__)["general"]["automatic_display"]:
        gui_hooks.reviewer_will_end.append(run_add_on)

    # Add a hotkey
    shortcut = mw.addonManager.getConfig(__name__)["general"]["shortcut"]
    shortcut = QShortcut(QKeySequence(shortcut), mw)
    shortcut.activated.connect(run_add_on)
