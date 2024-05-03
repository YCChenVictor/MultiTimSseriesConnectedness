"""
This script:
    1. obtain the upper parent path given a file
    2. add path to system path
"""


import os
import sys


def parent_path_once(path):
    """
    return the parent path
    """
    parent = os.path.abspath(os.path.dirname(path))
    return parent


def f_parent_path(path, layer=0):
    """
    return the parent path given the layer. if layer = 1, then return only one
    upper parent path. if layer = 2, then return two upper parent path, and so
    on.
    """
    while layer > 0:
        layer = layer - 1
        path = parent_path_once(path)

    return path


def add_path_to_sys(path):
    """
    add path to system path
    """
    if path not in sys.path:
        sys.path.insert(0, path)
