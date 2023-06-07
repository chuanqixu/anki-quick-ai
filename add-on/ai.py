from .edge_tts_data import EDGE_TTS_DICT

import openai
import edge_tts
from iso639 import to_iso639_1
import random, os, asyncio



def call_openai(model, prompt, **kwargs):
    completion = openai.ChatCompletion.create(
        model = model,
        messages=[{"role": "user", "content": prompt}],
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
