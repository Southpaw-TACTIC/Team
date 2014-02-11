#!Z:\team\Team\src\python\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'watchdog==0.7.1','console_scripts','watchmedo'
__requires__ = 'watchdog==0.7.1'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('watchdog==0.7.1', 'console_scripts', 'watchmedo')()
)
