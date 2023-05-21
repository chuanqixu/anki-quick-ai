from .edge_tts_data import EDGE_TTS_DICT

import openai
import edge_tts
from iso639 import to_iso639_1
import random, asyncio



def call_openai(prompt, model):
    completion = openai.ChatCompletion.create(
        model = model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion["choices"][0]["message"]["content"].encode("utf8").decode()



def make_edge_tts_mp3(text, trans_lang, filename):
    """
    TODO Refactor this shit
    """
    # langcode = langcodes.find(trans_lang).language
    langcode = to_iso639_1(trans_lang)
    voice = random.choice(EDGE_TTS_DICT.get(langcode))
    communicate = edge_tts.Communicate(text, voice)
    return asyncio.run(communicate.save(filename))
