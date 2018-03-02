from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
        windows=['UI_digit.py'],
        options={
                "py2exe":{
                        "unbuffered": True,
                        "optimize": 2,
                        "excludes": ["email"]
                }
        }
)
