import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

from .gpt import call_openai_to_make_article, call_openai_to_make_trans, article_lang, trans_lang



def gen_words_story() -> None:
    words = mw.col.find_cards('"deck:current" introduced:1')
    article = call_openai_to_make_article(words, language=article_lang)
    # make_edge_tts_mp3(article, article_lang, "output/article.mp3")
    trans_article = call_openai_to_make_trans(article, language=trans_lang)
    showInfo(f"AI Generated Story:\n{article}\n\nAI Generated Translation:\n{trans_article}")
    # make_edge_tts_mp3(trans_article, trans_lang, "output/translated_article.mp3")



# create a new menu item, "test"
action = QAction("AI Words Story", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, gen_words_story)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

# gen_words_story()
