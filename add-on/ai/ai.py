from .edge_tts_data import EDGE_TTS_DICT

import edge_tts
from iso639 import to_iso639_1
import random, os, asyncio
from .provider import *

provider = None

def update_provider(provider_name, api_key):
    global provider
    if provider == None or not isinstance(provider, globals()[provider_name]):
        provider = globals()[provider_name](api_key)
    if provider.api_key != api_key:
        provider.update_api_key(api_key)

def call_llm(provider_name, api_key, model, prompt, **kwargs):
    global provider
    update_provider(provider_name, api_key)
    completion = provider(model, prompt, **kwargs)
    return provider(model, prompt, **kwargs)


def make_edge_tts_mp3(text, language, voice, filename):
    langcode = to_iso639_1(language)
    if voice == "Random":
        voice = random.choice(EDGE_TTS_DICT.get(langcode))
    communicate = edge_tts.Communicate(text, voice)
    # if os.path.isfile(filename):
    #     os.remove(filename)

    # loop.run_until_complete(communicate.save(filename))
    asyncio.run(communicate.save(filename))


def get_avail_chat_model_list(provider_name, api_key):
    global provider
    update_provider(provider_name, api_key)
    return provider.get_avail_chat_model_list()
