
import logging

logger = logging.getLogger("pysolpro")

apc = None

try:
    from sp.ArgParseCache import ArgParserCache
    import argcomplete
    apc = ArgParserCache()
    logger.debug("argcompleter initialized")
except Exception as e:
    logger.warning("argcomplete not installed, tab completion disabled")

