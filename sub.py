__author__ = 'asherkhb'
# Simple practice script showing how to call command line processes from within python

import subprocess

subprocess.call("python json-decoder.py", shell=True)