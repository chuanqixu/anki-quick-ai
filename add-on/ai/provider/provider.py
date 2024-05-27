from abc import abstractmethod

class Provider:
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        for key, value in kwargs.items():
            self.__dict__[key] = value
        try:
            self.client = self.get_client()
        except:
            raise Exception("API Key is not valid")

    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def __call__(self, model, prompt, **kwargs):
        pass

    @abstractmethod
    def get_avail_chat_model_list(self):
        pass

    def update_api_key(self, api_key):
        self.api_key = api_key
        self.client = self.get_client()
