from ..ankiaddonconfig import ConfigManager, ConfigWindow
from .prompt_window import PromptNameTableDialog
from PyQt6.QtWidgets import QPushButton



conf = ConfigManager()

def general_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("General")

    tab.text("Running Settings", bold=True)

    tab.checkbox("general.automatic_display", "Automatically run add-on when changing to main window")

    tab.text_input(
        "general.shortcut",
        "Shortcut for add-on:"
    )

    tab.space(20)
    tab.text("Sound", bold=True)

    tab.checkbox("general.play_sound", "Generate and automatically play sound for response")
    tab.text_input(
        "general.default_sound_language",
        "Default Sound Language:",
        tooltip="Default language for edge-tts sound generation.",
    )

    # This adds a stretchable blank space.
    # If you are not sure what this does,
    # Try resizing the config window without this line

    tab.stretch()


def prompt_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("Prompt")

    prompt_name_table_dialog = PromptNameTableDialog(conf)
    tab.layout().addWidget(prompt_name_table_dialog)
    conf_window.execute_on_save(lambda: conf.set("prompt", prompt_name_table_dialog.prompt_data))

    # This adds a stretchable blank space.
    # If you are not sure what this does,
    # Try resizing the config window without this line
    tab.stretch()


def ai_tab(conf_window: ConfigWindow) -> None:
    tab = conf_window.add_tab("AI")

    tab.text("Required", bold=True)

    tab.text_input(
        "ai_config.api_key",
        "OpenAI API Key:",
        tooltip="Please go to OpenAI website to see how to acquire the key",
    )

    tab.text_input(
        "ai_config.model",
        "Model:",
        tooltip="Default is gpt-3.5-turbo",
    )

    tab.space(20)
    tab.text("Advanced", bold=True)

    tab.number_input(
        "ai_config.temperature",
        "Sampling temperature:",
        decimal=True,
        minimum=0,
        maximum=2,
        tooltip="Between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.",
    )

    tab.number_input(
        "ai_config.max_tokens",
        "Max Token:",
        minimum=0,
        maximum=2147483647,
        tooltip="The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length.",
    )

    tab.number_input(
        "ai_config.presence_penalty",
        "Presence Penalty:",
        decimal=True,
        minimum=-2.0,
        maximum=2.0,
        tooltip="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
    )

    tab.number_input(
        "ai_config.frequency_penalty",
        "Frequency Penalty:",
        decimal=True,
        minimum=-2.0,
        maximum=2.0,
        tooltip="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
    )

    # This adds a stretchable blank space.
    # If you are not sure what this does,
    # Try resizing the config window without this line
    tab.stretch() 


conf.use_custom_window()
conf.add_config_tab(general_tab)
conf.add_config_tab(prompt_tab)
conf.add_config_tab(ai_tab)
