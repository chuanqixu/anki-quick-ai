from PyQt6.QtWidgets import QWidget, QComboBox
from PyQt6.QtCore import Qt

from ..ankiaddonconfig import ConfigManager, ConfigWindow
from .prompt_window import PromptNameTableWidget
from ..ai.edge_tts_data import language_list, get_voice_list
from ..ai.provider import providers
from .provider import *


conf = ConfigManager()

def general_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("General")
    tab.setAlignment(Qt.AlignmentFlag.AlignTop)

    tab.text("Running Settings", bold=True)

    tab.checkbox("general.automatic_display", "Automatically run add-on when changing to main window")

    tab.text_input(
        "general.shortcut",
        "Shortcut for add-on:"
    )

    tab.space(20)
    tab.text("Sound (Currently may lead Anki to freeze)", bold=True)

    tab.checkbox("general.play_sound", "Generate and automatically play sound for response")

    name_combo = tab.dropdown(
        "general.default_sound_language",
        language_list,
        language_list,
        "Default edge-tts Language",
    )

    default_language = conf.get("general.default_sound_language")
    default_voice = conf.get("general.default_edge_tts_voice")
    default_voice_list = get_voice_list(conf["general"]["default_sound_language"])
    voice_combo = tab.dropdown(
        "general.default_edge_tts_voice",
        default_voice_list,
        default_voice_list,
        "Default edge-tts Voice",
        append_updates=False
    )
    voice_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

    def update_voice_combo(language):
        if language in language_list:
            voice_combo.clear()
            voice_combo.insertItems(0, get_voice_list(language))
        if language == default_language:
            voice_combo.setCurrentText(default_voice)

    def widget_update_voice_combo():
        voice_combo.setCurrentText(conf_window.conf.get("general.default_edge_tts_voice"))

    conf_window.widget_updates.append(widget_update_voice_combo)
    name_combo.currentTextChanged.connect(update_voice_combo)

    # This adds a stretchable blank space.
    # If you are not sure what this does,
    # Try resizing the config window without this line

    tab.stretch()


def prompt_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("Prompt")
    tab.setAlignment(Qt.AlignmentFlag.AlignTop)

    prompt_name_table_widget = PromptNameTableWidget(conf)
    tab.layout().addWidget(prompt_name_table_widget)
    conf_window.execute_on_save(lambda: conf.set("prompt", prompt_name_table_widget.data))
    conf_window.widget_updates.append(prompt_name_table_widget.load_data)



def ai_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("AI")
    tab.setAlignment(Qt.AlignmentFlag.AlignTop)

    default_provider = conf.get("ai_config.default_provider")
    default_provider_combo = tab.dropdown(
        "ai_config.default_provider",
        providers,
        providers,
        "Default Provider:",
        tooltip="Choose the default provider for the AI model",
    )
    default_provider_combo.setCurrentText(default_provider)

    tab.text("Provider Setting", bold=True)
    provider = default_provider
    provider_combo = QComboBox()
    provider_combo.insertItems(0, providers)
    provider_combo.setCurrentText(provider)
    row = tab.hlayout()
    row.text("Provider")
    row.space(7)
    row.addWidget(provider_combo)
    row.stretch()

    def widget_update_default_provider_combo():
        default_provider_combo.setCurrentText(conf_window.conf.get("ai_config.default_provider"))

    ai_config_widget = QWidget()
    ai_config_widget.setLayout(globals()["ai_config_layout_" + default_provider](conf_window, conf))
    tab.addWidget(ai_config_widget)

    def update_provider(provider):
        nonlocal ai_config_widget
        ai_config_widget.setParent(None)
        ai_config_widget.deleteLater()

        ai_config_widget = QWidget()
        ai_config_widget.setLayout(globals()["ai_config_layout_" + provider](conf_window, conf))
        tab.addWidget(ai_config_widget)

    provider_combo.currentTextChanged.connect(update_provider)



conf.use_custom_window()
conf.add_config_tab(general_tab)
conf.add_config_tab(prompt_tab)
conf.add_config_tab(ai_tab)
