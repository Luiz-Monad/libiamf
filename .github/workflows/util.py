#!/usr/bin/env python3
import subprocess

global _log_root
_log_root = ""

def set_logroot(root):
    global _log_root
    _log_root = root

def logrun(cmd, cwd=None):
    global _log_root
    wd = "" if cwd is None else str(cwd)
    rwd = wd.replace(str(_log_root), "")
    print("+", rwd, (" ".join(cmd)))

def run(cmd, cwd=None):
    logrun(cmd, cwd=cwd)
    subprocess.run(cmd, cwd=cwd, check=True)

def runout(cmd, cwd=None):
    logrun(cmd, cwd=cwd)
    return subprocess.check_output(cmd, cwd=cwd).decode()
