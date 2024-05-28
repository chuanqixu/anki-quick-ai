from .provider import Provider
from groq import Groq

class ProviderGroq(Provider):
    def __init__(self, api_key, **kwargs):
        super().__init__(api_key, **kwargs)

    def get_client(self):
        return Groq(api_key=self.api_key)

    def __call__(self, model, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        try:
            messages = [{"role": "user", "content": prompt}]
            if "system_prompt" in kwargs and kwargs["system_prompt"]:
                messages.insert(0, {"role": "system", "content": kwargs["system_prompt"]})

            completion = self.client.chat.completions.create(messages=messages, model=model).choices[0].message.content
            return completion
        except Exception as e:
            return f"Error in retrieving from the API provider. Error information:\n\n{str(e)}"

    def get_avail_chat_model_list(self):
        avail_chat_model_list = []
        try:
            models = self.client.models.list().data
            avail_chat_model_list = [model.id for model in models if model.id.startswith("gpt")]
        finally:
            return avail_chat_model_list
