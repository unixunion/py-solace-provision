
import logging

from sp.ArgParseCache import ArgParserCache

logger = logging.getLogger("pysolpro")

apc = None

try:
    import argcomplete
    apc = ArgParserCache()
    logger.debug("argcompleter initialized")
except Exception as e:
    logger.warning("argcomplete not installed, tab completion disabled")

