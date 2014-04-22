"""Aplication base Handler (controller / action) classes

Base handler classes as well as related request mapping classes"""

import tornado.web
import traceback

class Handler(tornado.web.RequestHandler):
    """Base handler class"""
    def initialize(self, registry):
        self._registry = registry

    """Custom error handler for uncaught exceptions and errors"""
    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs.keys():
            self._registry['log'].info(''.join(traceback.format_exception(
                    *kwargs['exc_info'])))
            
        self.write({'message': 'Server Error - Check server logs'})
   