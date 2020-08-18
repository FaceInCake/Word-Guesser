from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('GuesserHelper.py', base=base)
]

setup(name='Word Guesser Helper',
      version = '2.0',
      description = 'Helps guess an unknown word, Wheel of Fortune style',
      options = dict(build_exe = buildOptions),
      executables = executables)
