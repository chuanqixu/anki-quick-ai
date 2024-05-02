from aqt import mw, gui_hooks, browser
from aqt.qt import QAction, qconnect

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import QThread, pyqtSignal
import os
import time
import threading
import shutil
import json

from .anki import get_note_field_value_list, get_note_id_list, get_note_field_value_clean
from .ai import call_llm, make_edge_tts_mp3
from .gui import RunDialog, ResponseDialog, conf
from .utils import remove_html_tags, format_prompt_list, color_html, prompt_html, field_value_html
from .ai.edge_tts_data import get_voice_list

IS_BROWSE_OPEN = False

class AIThread(QThread):
    field_value_ready = pyqtSignal(list)
    new_text_ready = pyqtSignal(str)
    start_one_iter = pyqtSignal(str)
    finished_one_iter = pyqtSignal(int, str)
    finished_gen_sound = pyqtSignal(str)

    def __init__(self, prompt_config, ai_config=None, play_sound=None):
        super().__init__()
        config = mw.addonManager.getConfig(__name__)
        self.ai_config = ai_config
        if not ai_config:
            self.ai_config = config["ai_config"]

        self.query = prompt_config["query"]
        self.note_field_config = prompt_config["note_field"]
        self.system_prompt = prompt_config["system_prompt"]
        self.prompt_list = prompt_config["prompt"]
        self.language_list = prompt_config["language"]
        self.agentic_behavior = prompt_config["agentic_behavior"]
        self.default_language = config["general"]["default_sound_language"]
        self.voice = config["general"]["default_edge_tts_voice"]

        self.field_value_list = None
        self.response_list = []
        self.play_sound = play_sound

        self.delay_time = 0.01

        if self.play_sound:
            self.finished_one_iter.connect(self.gen_sound)

        if self.agentic_behavior:
            self.finished_one_iter.connect(self.run_agentic_job)

    def run_agentic_job(self, i, output):
        try:
            output = output.replace("```json", "```")
            start = output.find("```")
            end = output.rfind("```")
            output = output[start+3:end]
            json_out = json.loads(output.strip())

            note = mw.col.getNote(int(self.query.split(":")[1]))

            updated_fields = []

            for key, value in json_out.items():
                if key in note:
                    note[key] = value
                    updated_fields.append(key)

            note.flush()
            
            self.new_text_ready.emit("\n\n======== AGENT RESPONSE ========")
            self.new_text_ready.emit(f"\nAgent updated the fields: {', '.join(updated_fields)}")
        except Exception as e:
            pass

    def run(self):
        if self.agentic_behavior:
            self.field_value_list = get_note_field_value_clean(mw.col, self.query, self.note_field_config)
        else:
            self.field_value_list = get_note_field_value_list(mw.col, self.query, self.note_field_config)

        self.field_value_ready.emit(self.field_value_list)

        time.sleep(0.1) # make sure the first prompt will be printed

        self.provider = self.ai_config.pop("provider")
        self.api_key = self.ai_config.pop("api_key")
        self.model = self.ai_config.pop("model")

        # TODO: check api_key and model is given
        self.initial_response()

    def response(self, prompt):
        response_idx = len(self.response_list)
        prompt_html_str = prompt_html(prompt, "green")
        prompt = prompt.replace(f"#field_value#", str(self.field_value_list))
        prompt = prompt.replace(f"#language#", self.language_list[response_idx] if response_idx < len(self.language_list) else self.default_language)
        if response_idx > 0:
            prompt = prompt.replace(f"#response#", self.response_list[-1])

        if self.agentic_behavior:
            note_fields = note_fields = {field.split(":")[0]: f"<value for {field.split(':')[0].lower()} field>" for field in self.field_value_list}
            prompt = prompt.replace(f"#json_fields#", json.dumps(note_fields, indent=2))

        self.start_one_iter.emit(prompt_html_str)

        response = call_llm(self.provider, self.api_key, self.model, prompt, **self.ai_config)

        response_str = ""
        
        if isinstance(response, str):
            self.new_text_ready.emit(response)
            response_str += response
        else:        
            for event in response: 
                new_text = event.choices[0].delta.content
                if new_text:
                    self.new_text_ready.emit(new_text)
                    response_str += new_text
                time.sleep(self.delay_time)

        if self.play_sound:
            self.finished_one_iter.emit(response_idx, response_str)
        
        self.response_list.append(response_str)

    def initial_response(self):
        for prompt in self.prompt_list:
            self.response(prompt)

    def gen_sound(self, i, response_str):
        if i < len(self.language_list):
            language = self.language_list[i]
            voice = self.voice
            if voice not in get_voice_list(language):
                voice = "Random"
        else:
            language = self.default_language
            voice = "Random"
        
        sound_gen_thread = SoundGenThread(i, response_str, language, voice, self)
        sound_gen_thread.daemon = True
        sound_gen_thread.start()
    
    def signal_finished_gen_sound(self, filename):
        self.finished_gen_sound.emit(filename)



class SoundGenThread(threading.Thread): # Cannot be QThread, otherwise will cause Anki to crash because of the async loop
    def __init__(self, i, response_str, language, voice, ai_thread):
        super().__init__()
        self.i = i
        self.response_str = response_str
        self.language = language
        self.voice = voice
        self.ai_thread = ai_thread

    def run(self):
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "output")):
            os.makedirs(os.path.join(os.path.dirname(__file__), "output"))

        response_str = remove_html_tags(self.response_str)
        filename = os.path.join(os.path.dirname(__file__), "output", f"response_{self.i}.mp3")
        make_edge_tts_mp3(response_str, self.language, self.voice, filename)
        self.ai_thread.signal_finished_gen_sound(filename)



def gen_response(prompt_config, parent=None, response_dialog=None, recursive=False):
    try:
        if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")):
            shutil.rmtree(os.path.join(os.path.dirname(os.path.dirname(__file__)), "output"))
    finally:
        pass
    if response_dialog:
        response_dialog.close()

    config = mw.addonManager.getConfig(__name__)
    prompt_config["prompt"] = format_prompt_list(prompt_config["prompt"], prompt_config["placeholder"], prompt_config["language"])

    def show_dialog(field_value_list):
        initial_text = field_value_html(field_value_list, "green")
        dialog = ResponseDialog(initial_text, ai_thread, parent)
        dialog.regen_button.clicked.connect(lambda: gen_response(prompt_config, parent, dialog))
        dialog.setModal(False)
        dialog.show()

    has_agentic_behavior = prompt_config.get("agentic_behavior") if prompt_config.get("agentic_behavior") else False

    if has_agentic_behavior and not recursive:
        notes = get_note_id_list(mw.col, prompt_config["query"])
        for note in notes:
            new_query = f"nid:{note}"
            prompt_config["query"] = new_query

            gen_response(prompt_config, parent=parent, response_dialog=response_dialog, recursive=True)
    else:
        ai_thread = AIThread(prompt_config, config["ai_config"], config["general"]["play_sound"])
        ai_thread.start()
        ai_thread.field_value_ready.connect(show_dialog)


def run_add_on(parent=None):
    if not parent:
        parent = mw

    def click_run_add_on(run_widget):
        prompt_config = run_widget.prompt_dict[run_widget.curr_prompt_name]
        prompt_config["query"] = run_widget.input_field_browse_query.text()
        run_widget.close()
        gen_response(
            prompt_config,
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

@gui_hooks.browser_menus_did_init.append
def on_browser_menus_did_init(browser: browser.Browser):
    action = QAction("Anki Quick AI: Run on selected items", browser)
    action.triggered.connect(lambda: run_add_on(browser))
    browser.form.menu_Cards.addSeparator()
    browser.form.menu_Cards.addAction(action)