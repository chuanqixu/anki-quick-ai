class Provider:
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __call__(self, model, prompt, **kwargs):
        raise NotImplementedError
    
    def get_avail_chat_model_list(self):
        raise NotImplementedError

    def update_api_key(self, api_key):
        raise NotImplementedError
