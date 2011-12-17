"""
The settings used by this site.

This consists of the general produciton settings, with an optional import of any local
settings.
"""
#@PydevCodeAnalysisIgnore


# Import production settings.
from production import *


# Import optional local settings.
try:
    from local import *
except ImportError:
    pass