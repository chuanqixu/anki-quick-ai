from .configure import settings, PROMPT, PROMPT_TRANS, EDGE_TTS_DICT
from .anki_local import retrieve_words

import openai
import edge_tts
import playsound
from iso639 import to_iso639_1
import random, asyncio

# Anki settings
deck_name = settings.deck_name
query = settings.query
field = settings.field

# GPT settings
openai.api_key = settings.api_key
article_lang = settings.article_lang
trans_lang = settings.trans_lang
model = settings.model



def call_openai_to_make_article(words, language):
    prompt = PROMPT.format(language=language, words=words)
    completion = openai.ChatCompletion.create(

        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion["choices"][0]["message"]["content"].encode("utf8").decode()


def call_openai_to_make_trans(text, language):
    prompt = PROMPT_TRANS.format(text=text, language=language)
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion["choices"][0]["message"]["content"].encode("utf8").decode()


# def make_edge_tts_mp3(text, trans_lang, filename):
#     """
#     TODO Refactor this shit
#     """
#     # langcode = langcodes.find(trans_lang).language
#     langcode = to_iso639_1(trans_lang)
#     voice = random.choice(EDGE_TTS_DICT.get(langcode))
#     communicate = edge_tts.Communicate(text, voice)
#     return asyncio.run(communicate.save(filename))


if __name__ == "__main__":
    import os
    if not os.path.exists("output"):
        os.makedirs("output")
    # retrieve words
    # words = retrieve_words(deck_name=deck_name, query=query, field=field)
    # article = call_openai_to_make_article(words, language=article_lang)
    # make_edge_tts_mp3(article, article_lang, "output/article.mp3")
    # trans_article = call_openai_to_make_trans(article, language=trans_lang)
    # make_edge_tts_mp3(trans_article, trans_lang, "output/translated_article.mp3")

    # color = '\033[92m'
    # end_color = '\033[0m'
    # words_str = '\t'.join(words)
    # print(f"{color}Today's Words:{end_color}\n{words_str}")
    # print(f"\n{color}Article Generated by ChatGPT:{end_color} \n\n{article}")
    # print(f"\n{color}Translation Generated by ChatGPT:{end_color} \n\n{trans_article}")
    # playsound.playsound("output/article.mp3")
    # playsound.playsound("output/translated_article.mp3")
