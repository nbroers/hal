from lib.bootstrap import Bootstrap
import argparse

parser = argparse.ArgumentParser(description='HAL command line options.')
parser.add_argument('--port', dest='port',
                   help="port on which web server will run.")
                   
arguments = parser.parse_args()
if not arguments.port:
    raise Exception('--port command line option is mandatory')

bootstrap = Bootstrap(int(arguments.port), 'default')
registry = bootstrap.bootstrap()