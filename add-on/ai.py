from .edge_tts_data import EDGE_TTS_DICT

import openai
import edge_tts
from iso639 import to_iso639_1
import random, asyncio, os
from asyncqt import QEventLoop
from PyQt6.QtCore import QThread


def call_openai(model, prompt, **kwargs):
    completion = openai.ChatCompletion.create(
        model = model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs
    )
    return completion["choices"][0]["message"]["content"].encode("utf8").decode()



def make_edge_tts_mp3(text, language, filename, loop):
    langcode = to_iso639_1(language)
    voice = random.choice(EDGE_TTS_DICT.get(langcode))
    communicate = edge_tts.Communicate(text, voice)
    if os.path.isfile(filename):
        os.remove(filename)

    # asyncio.run(communicate.save(filename))
    # loop = asyncio.get_event_loop()
    # try:
    loop.run_until_complete(communicate.save(filename))
    # finally:
    #     loop.close()

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    # # try:
    # loop.run_until_complete(communicate.save(filename))

    #     # Run all remaining tasks
    #     pending = asyncio.all_tasks(loop=loop)
    #     if pending:
    #         loop.run_until_complete(asyncio.gather(*pending))
    # finally:
    #     loop.close()
        # asyncio.set_event_loop(None)
    
    # loop = QEventLoop()
    # asyncio.set_event_loop(loop)
    # with loop:
    #     loop.run_until_complete(communicate.save(filename))

    # loop = asyncio.get_event_loop()
    # task = loop.create_task(communicate.save(filename))

    # # Get the current event loop
    # loop = asyncio.get_event_loop()
    # # Schedule the coroutine on the loop and get a Future object
    # future = asyncio.run_coroutine_threadsafe(communicate.save(filename), loop)
    # # Wait for the coroutine to complete and get its result
    # # (this will block the current thread until the coroutine is done)
    # result = future.result()