from .edge_tts_data import EDGE_TTS_DICT

import openai
import edge_tts
from iso639 import to_iso639_1
import random, asyncio, os



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
    if os.path.isfile(filename):
        os.remove(filename)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(communicate.save(filename))

        # Run all remaining tasks
        pending = asyncio.all_tasks(loop=loop)
        if pending:
            loop.run_until_complete(asyncio.gather(*pending))
    finally:
        loop.close()
        asyncio.set_event_loop(None)
