from .edge_tts_data import EDGE_TTS_DICT

from openai import OpenAI
from groq import Groq
import edge_tts
from iso639 import to_iso639_1
import random, os, asyncio


def call_llm(provider, api_key, model, prompt, system_prompt, **kwargs):
    completion = "Wrong provider"

    if provider == "Groq":
        client = Groq(api_key=api_key)
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        completion = client.chat.completions.create(messages=messages, model=model).choices[0].message.content

    elif provider == "OpenAI":
        client = OpenAI(api_key=api_key)
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        completion = client.chat.completions.create(
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


def get_avail_chat_model_list(api_provider, api_key):
    avail_chat_model_list = []

    if api_provider == "Groq":
        return ["llama3-70b-8192", "llama3-8b-8192", "llama2-70b-4096", "mixtral-8x7b-32768", "gemma-7b-it"]

    if api_provider == "OpenAI":
        try:
            client = OpenAI(api_key=api_key)
            models = client.models.list().data
            avail_chat_model_list = [model.id for model in models if model.id.startswith("gpt")]
        finally:
            return avail_chat_model_list
        
    return avail_chat_model_list
