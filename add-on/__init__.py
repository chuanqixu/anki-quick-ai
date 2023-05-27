import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from aqt import mw, gui_hooks
from aqt.qt import QAction, qconnect

from .controller import gen_response, run_add_on



config = mw.addonManager.getConfig(__name__)

action_mw = QAction("Anki Quick AI", mw)
qconnect(action_mw.triggered, lambda: run_add_on(config["query"]))

# Add it to the tools menu
mw.form.menuTools.addAction(action_mw)

def run_add_on_browse(browser):
    action_browse = QAction("Anki Quick AI", mw)
    browser.form.menubar.addAction(action_browse)
    qconnect(action_browse.triggered, lambda: run_add_on(browser.form.searchEdit.lineEdit().text(), browser))
# Add it to the browse window
gui_hooks.browser_will_show.append(run_add_on_browse)


if config["automatic_display"]:
    # hook for end of the deck
    gui_hooks.reviewer_will_end.append(run_add_on)
