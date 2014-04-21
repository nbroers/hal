"""Application bootstrapping and initialization

Application bootstrapping that sets up database connections, configuration,
logging, etc"""

import logging
import os
from lib import log, config, alarm
from flask import Flask
from flask.ext import restful

class Bootstrap():
    """Bootstrap class that initializes application
    
    Initializes application configuration, logging, database connections and
    everything else required by the application."""
    def __init__(self, port=None, environment='default', actions=None):
        self.environment = environment
        self.registry = {}
        self.port = port
        
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
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=self.registry['config'].getint('log.level'), format=log_format)
        logger.addHandler(file_logger)
        logger = log.Log()
        logger.info(__name__, 'HAL startup')
        self.registry['log'] = logger

    def _bootstrap_web_server(self):
        self._bootstrap_action('project_path')
        self._bootstrap_action('config')
        
        app = Flask(__name__)
        api = restful.Api(app)
    
        api.add_resource(alarm.AlarmStatusResource, '/alarm_status')
        
        app.run(debug=True, host='0.0.0.0', port=self.port)