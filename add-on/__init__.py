import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from .controller import init_control

init_control()
