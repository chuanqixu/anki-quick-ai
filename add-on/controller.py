from aqt import mw
from aqt.utils import showInfo
from aqt.operations import QueryOp

from .anki import get_words
from .gpt import call_openai_to_make_article, call_openai_to_make_trans, article_lang, trans_lang



def _get_story_from_ai(browse_cmd):
    words = get_words(browse_cmd)
    article = call_openai_to_make_article(words, language=article_lang)
    # make_edge_tts_mp3(article, article_lang, "output/article.mp3")
    trans_article = call_openai_to_make_trans(article, language=trans_lang)
    # make_edge_tts_mp3(trans_article, trans_lang, "output/translated_article.mp3")
    return article, trans_article


def _show_story(article, trans_article):
    showInfo(f"AI Generated Story:\n{article}\n\nAI Generated Translation:\n{trans_article}")



def gen_words_story() -> None:
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: _get_story_from_ai('"deck:current" introduced:1'),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda x: _show_story(x[0], x[1])
    )

    op.with_progress().run_in_background()
