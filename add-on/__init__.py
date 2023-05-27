import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from .controller import init_control
# from aqt import gui_hooks

# def on_profile_loaded():
#     init_control()

# gui_hooks.profile_did_open.append(on_profile_loaded)

init_control()