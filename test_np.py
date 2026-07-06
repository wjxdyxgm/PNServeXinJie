import traceback
import sys
try:
    import numpy
    print("Numpy OK:", numpy.__version__)
except Exception as e:
    traceback.print_exc()
