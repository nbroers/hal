"""Aplication base Handler (controller / action) classes

Base handler classes as well as related request mapping classes"""

import tornado.web

class Handler(tornado.web.RequestHandler):
    """Base handler class"""
    def initialize(self, registry):
        self._registry = registry

   

