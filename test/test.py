#!/usr/bin/python3

import os.path
import shutil
import subprocess

os.environ["EHOME_DEBUG"] = "yes"
os.environ["EHOME_ROOT"] = os.getcwd()

subprocess.run("../bin/ehomed.py", shell=True)
