import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from aqt import mw
from aqt.qt import QAction, qconnect

from .controller import gen_words_story



# create a new menu item, "test"
action = QAction("AI Words Story", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, gen_words_story)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
