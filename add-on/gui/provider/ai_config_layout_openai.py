from .ai_config_layout import AIConfigLayout

class AIConfigLayoutOpenAI(AIConfigLayout):
    def __init__(self, conf_window, conf) -> None:
        super().__init__(conf_window, conf)

    def advanced(self):
        self.text("Advanced", bold=True)
        self.text('<a href="https://platform.openai.com/docs/api-reference/chat/create#chat/create-temperature">More Details</a>', html=True, size=10)

        self.number_input(
            self.get_key("temperature"),
            "Sampling temperature:",
            decimal=True,
            minimum=0,
            maximum=2,
            tooltip="Between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.",
        )

        self.number_input(
            self.get_key("max_tokens"),
            "Max Token:",
            minimum=0,
            maximum=2147483647,
            tooltip="The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length.",
        )

        self.number_input(
            self.get_key("presence_penalty"),
            "Presence Penalty:",
            decimal=True,
            minimum=-2.0,
            maximum=2.0,
            tooltip="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
        )

        self.number_input(
            self.get_key("frequency_penalty"),
            "Frequency Penalty:",
            decimal=True,
            minimum=-2.0,
            maximum=2.0,
            tooltip="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
        )
