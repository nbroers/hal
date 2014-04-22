"""Application logging

Logging and related classes"""

import logging

class Log():
    """Proxy implementation of Python's logger to enable mock testing

    A proxy log class implementation to prevent use of the logging.getLogger()
    singleton. Using the log proxy, log objects can be mocked and injected into
    code under test.
    """
    def debug(self, message, *args, **kwargs):
        log = logging.getLogger('HAL')
        return log.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        log = logging.getLogger('HAL')
        return log.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        log = logging.getLogger('HAL')
        return log.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        log = logging.getLogger('HAL')
        return log.error(message, *args, **kwargs)

    def exception(self, message, *args):
        log = logging.getLogger('HAL')
        return log.exception(message, *args)
