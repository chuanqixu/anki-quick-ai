import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from aqt import mw, gui_hooks
from aqt.qt import QAction, qconnect

from .controller import gen_words_story, choose_running_add_on



# create a new menu item, "test"
action = QAction("AI Words Story", mw)
# set it to call testFunction when it's clicked
# qconnect(action.triggered, gen_words_story)
qconnect(action.triggered, gen_words_story)
# and add it to the tools menu
mw.form.menuTools.addAction(action)


# hook for end of the deck
gui_hooks.reviewer_will_end.append(choose_running_add_on)
