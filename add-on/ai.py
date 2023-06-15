from .edge_tts_data import EDGE_TTS_DICT

import openai
import edge_tts
from iso639 import to_iso639_1
import random, os, asyncio



def call_openai(model, prompt, system_prompt, **kwargs):
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    completion = openai.ChatCompletion.create(
        model = model,
        messages=messages,
        stream=True,
        **kwargs
    )
    return completion


def make_edge_tts_mp3(text, language, voice, filename):
    langcode = to_iso639_1(language)
    if voice == "Random":
        voice = random.choice(EDGE_TTS_DICT.get(langcode))
    communicate = edge_tts.Communicate(text, voice)
    # if os.path.isfile(filename):
    #     os.remove(filename)

    # loop.run_until_complete(communicate.save(filename))
    asyncio.run(communicate.save(filename))


def get_avail_chat_model_list(api_key):
    avail_chat_model_list = []
    try:
        openai.api_key = api_key
        chat_model_list = ["gpt-4", "gpt-4-0314", "gpt-4-32k", "gpt-4-32k-0314", "gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
        model_list = [model["id"] for model in openai.Model.list()["data"]]
        avail_chat_model_list = [model for model in chat_model_list if model in model_list]
    finally:
        return avail_chat_model_list
