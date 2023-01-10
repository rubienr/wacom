""" Pytest configuration. """
import sys
from os.path import abspath
from os.path import dirname as dir_name

root_dir = dir_name(dir_name(abspath(__file__)))
sys.path.append(root_dir)
