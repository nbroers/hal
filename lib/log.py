"""Application logging

Logging and related classes"""

import logging

class Log():
    """Proxy implementation of Python's logger to enable mock testing

    A proxy log class implementation to prevent use of the logging.getLogger()
    singleton. Using the log proxy, log objects can be mocked and injected into
    code under test.
    """
    def debug(self, module, message, *args, **kwargs):
        log = logging.getLogger(module)
        return log.debug(message, *args, **kwargs)

    def info(self, module, message, *args, **kwargs):
        log = logging.getLogger(module)
        return log.info(message, *args, **kwargs)

    def warning(self, module, message, *args, **kwargs):
        log = logging.getLogger(module)
        return log.warning(message, *args, **kwargs)

    def error(self, module, message, *args, **kwargs):
        log = logging.getLogger(module)
        return log.error(message, *args, **kwargs)

    def exception(self, module, message, *args):
        log = logging.getLogger(module)
        return log.exception(message, *args)
