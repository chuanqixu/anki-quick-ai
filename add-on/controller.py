from aqt import mw
from aqt.utils import showInfo
from aqt.operations import QueryOp

import openai

from .anki import get_words
from .gpt import call_openai



def _get_story_from_ai(browse_cmd):
    config = mw.addonManager.getConfig(__name__)
    openai.api_key = config["api_key"]
    article_lang = config["article_language"]
    trans_lang = config["trans_language"]
    model = config["model"]

    words = get_words(browse_cmd)
    prompt = config["prompt"].format(language=article_lang, words=words)
    article = call_openai(prompt,  model)
    # make_edge_tts_mp3(article, article_lang, "output/article.mp3")

    prompt_trans = config["prompt_translation"].format(text=article, language=trans_lang)
    trans_article = call_openai(prompt_trans, model)
    # make_edge_tts_mp3(trans_article, trans_lang, "output/translated_article.mp3")

    return words, article, trans_article


def _show_story(words, article, trans_article):
    showInfo(f"New Words:\n{words}\n\nAI Generated Story:\n{article}\n\nAI Generated Translation:\n{trans_article}")



def gen_words_story() -> None:
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: _get_story_from_ai(mw.addonManager.getConfig(__name__)["query"]),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda x: _show_story(x[0], x[1], x[2])
    )

    op.with_progress().run_in_background()
