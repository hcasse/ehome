#!/usr/bin/python3

import os.path
import shutil
import subprocess

if os.path.exists("etc"):
	shutil.rmtree("etc")
shutil.copytree("etc-in", "etc")

os.environ["EHOME_DEBUG"] = "yes"
os.environ["EHOME_ROOT"] = os.getcwd()

subprocess.run("../bin/ehomed.py", shell=True)
