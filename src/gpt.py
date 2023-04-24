from configure import settings, PROMPT, PROMPT_TRANS
from anki import retrieve_words

import openai



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


def call_openai_to_make_trans(text, language="Simplified Chinese"):
    prompt = PROMPT_TRANS.format(text=text, language=language)
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion["choices"][0]["message"]["content"].encode("utf8").decode()


if __name__ == "__main__":
    # retrieve words
    words = retrieve_words(deck_name=deck_name, query=query, field=field)
    print(words)
    article = call_openai_to_make_article(words, language=article_lang)
    print(article)
