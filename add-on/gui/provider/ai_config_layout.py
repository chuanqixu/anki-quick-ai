from aqt.qt import QBoxLayout
import os, inspect

from ...ai import get_avail_chat_model_list, special_names
from ...ankiaddonconfig import ConfigLayout

class AIConfigLayout(ConfigLayout):
    def __init__(self, config_window, conf) -> None:
        super().__init__(config_window, QBoxLayout.Direction.TopToBottom)
        subclass_file = inspect.stack()[1][1]
        filename = os.path.basename(subclass_file)
        filename = filename.replace("ai_config_layout_", "").replace(".py", "")
        if filename in special_names:
            self.provider_name = special_names[filename]
        else:
            self.provider_name = filename.capitalize()
        self.default_conf = conf
        self.prefix = f"ai_config.{self.provider_name}."

        self.basic()
        self.advanced()

    def get_key(self, key):
        return self.prefix + key

    def basic(self):
        default_api_key = self.default_conf.get(self.prefix + "api_key")
        api_key_text_input = self.text_input(
            self.prefix + "api_key",
            "API Key:"
        )
        api_key_text_input.setText(default_api_key)
        # self.text('You can get API key <a href="https://platform.openai.com/account/api-keys">here</a>', html=True, size=10)

        try:
            default_avail_chat_model_list = get_avail_chat_model_list(self.provider_name, default_api_key)
        except:
            default_avail_chat_model_list = ["API Key is not valid"]
        if len(default_avail_chat_model_list) == 0:
            default_avail_chat_model_list = ["API Key is not valid"]
        model_combo = self.dropdown(
            self.prefix + "model",
            default_avail_chat_model_list,
            default_avail_chat_model_list,
            "Model:",
            tooltip="Default is gpt-3.5-turbo",
            append_updates=False
        )

        def update_model(api_key):
            try:
                avail_chat_model_list = get_avail_chat_model_list(self.provider_name, api_key)
            except:
                avail_chat_model_list = ["API Key is not valid"]
            if len(avail_chat_model_list) == 0:
                avail_chat_model_list = ["API Key is not valid"]

            model_combo.clear()
            model_combo.insertItems(0, avail_chat_model_list)
            if api_key == default_api_key:
                model_combo.setCurrentText(self.default_conf.get(self.prefix + "model"))

        api_key_text_input.textChanged.connect(lambda text: update_model(text))

    def advanced(self):
        pass

    def clear(self):
        while self.count():
            child = self.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
