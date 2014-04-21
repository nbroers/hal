from flask.ext import restful

class AlarmStatusResource(restful.Resource):
    def get(self):
        return {'armed': True}