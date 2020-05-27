import cProfile
pr = cProfile.Profile()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

pr.enable()
import main
pr.disable()

pr.print_stats(sort='time')
input("Press Enter to exit...")