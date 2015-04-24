"""Application bootstrapping and initialization

Application bootstrapping that sets up database connections, configuration,
logging, etc"""

import logging
import os
from lib import log, config, alarm, text_to_speech
import tornado.ioloop
import tornado.web
from tornado import httpserver, ioloop


class Bootstrap():
    """Bootstrap class that initializes application
    
    Initializes application configuration, logging, database connections and
    everything else required by the application."""
    def __init__(self, environment='default', actions=None):
        self.environment = environment
        self.registry = {}
        
        #Maintains a list of all the bootstrap actions available
        self._bootstrap_actions = ['project_path', 'config',
                'log', 'web_server']
                
        #Keeps a dictionary by bootstrap action name as key and value 
        #is a boolean indicating if a bootstrap action has been performed
        self._bootstrap_status = {}
        #Default all statuses to False since nothing has been bootstrapped
        for action in self._bootstrap_actions:
            self._bootstrap_status[action] = False

        self._to_bootstrap = []
        #If a list of actions was passed, used that instead
        if actions:
            self._to_bootstrap = actions

    def bootstrap(self):
        #minimum requirements for bootstrapping
        self._bootstrap_action('config')
        
        if not self._to_bootstrap:
            config_actions = self.registry['config'].get('bootstrap_all')
            if config_actions:
                self._to_bootstrap = config_actions.split(',')
            else:
                self._to_bootstrap = self._bootstrap_actions
        
        #config is already bootstrapped
        if 'config' in self._to_bootstrap:
            self._to_bootstrap.remove('config')
        
        for action in self._to_bootstrap:
            self._bootstrap_action(action)
        return self.registry
        
    def _bootstrap_action(self, action):
        #only execute if we haven't yet
        if not self._bootstrap_status[action]:
            method_name = '_bootstrap_' + action
            method = getattr(self, method_name)
            method()
            self._bootstrap_status[action] = True

    def _bootstrap_project_path(self):
        self.registry['project_path'] = os.path.dirname(os.path.realpath(
                __file__ + '/../'))
        
    def _bootstrap_config(self):
        self._bootstrap_action('project_path')
        self.registry['config'] = config.Config([self.registry['project_path'] + '/config/application.default.cfg'],
                                    [self.registry['project_path'] + '/config/application.local.cfg'],
                                     self.environment)
        
    def _bootstrap_log(self):
        self._bootstrap_action('project_path')
        self._bootstrap_action('config')
        
        log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        file_logger = logging.FileHandler(filename=self.registry['config'].get('log.file'))
        file_logger.setLevel(self.registry['config'].getint('log.level'))
        file_logger.setFormatter(formatter)
        logger = logging.getLogger('HAL')
        logging.basicConfig(level=self.registry['config'].getint('log.level'), format=log_format)
        logger.addHandler(file_logger)
        logger = log.Log()
        self.registry['log'] = logger

    def _bootstrap_web_server(self):
        self._bootstrap_action('config')
        self._bootstrap_action('log')

        tornado_application = tornado.web.Application(
            handlers=[
                (r"/alarm_status", alarm.AlarmStatusHandler,
                     dict(registry=self.registry)),
                (r"/text_to_speech", text_to_speech.TextToSpeechHandler,
                     dict(registry=self.registry)),              
            ],
            template_path=os.path.join(self.registry['project_path'], "templates"),
            static_path=os.path.join(self.registry['project_path'], "static"),
            ui_modules={}
        )
    
        http_server = httpserver.HTTPServer(tornado_application, xheaders=True)
        http_server.listen(self.registry['config'].get('webserver.port'))
        self.registry['log'].info('HAL startup')
        ioloop.IOLoop.instance().start()
